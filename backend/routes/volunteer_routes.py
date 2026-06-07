from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from database.db import get_db_connection
from ai.scheduler import get_upcoming_patients
from ai.circle_optimizer import evaluate_circle
from ai.donor_prediction import predict_participation_score

volunteer_bp = Blueprint("volunteer", __name__)

@volunteer_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_volunteer_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.full_name, u.email, u.phone, u.city, u.role
            FROM users u 
            WHERE u.user_id = %s
        """, (user_id,))
        volunteer = cursor.fetchone()
        return jsonify(volunteer)
    finally:
        cursor.close()
        conn.close()

@volunteer_bp.route("/profile/update", methods=["PUT"])
def update_profile():
    data = request.json
    user_id = data['user_id']
    phone = data['phone']
    city = data['city']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET phone = %s, city = %s 
            WHERE user_id = %s
        """, (phone, city, user_id))
        conn.commit()
        return jsonify({"message": "Profile updated successfully"})
    finally:
        cursor.close()
        conn.close()

@volunteer_bp.route("/circle-health", methods=["GET"])
def get_circle_health():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all patients
        cursor.execute("SELECT p.patient_id, u.full_name as patient_name FROM patients p JOIN users u ON p.user_id = u.user_id WHERE p.status = 'active'")
        patients = cursor.fetchall()
        
        health_reports = []
        for p in patients:
            recommendations = evaluate_circle(p['patient_id'])
            if recommendations:
                health_reports.append({
                    'patient_id': p['patient_id'],
                    'patient_name': p['patient_name'],
                    'recommendations': recommendations
                })
        return jsonify(health_reports)
    finally:
        cursor.close()
        conn.close()

@volunteer_bp.route("/active-requests", methods=["GET"])
def get_active_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT br.*, u.full_name as patient_name, u.city 
            FROM blood_requests br
            JOIN patients p ON br.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE br.status IN ('pending', 'matched', 'escalated')
            AND br.request_id IN (
                SELECT MAX(request_id) 
                FROM blood_requests 
                WHERE status IN ('pending', 'matched', 'escalated')
                GROUP BY patient_id
            )
            ORDER BY br.urgency DESC, br.request_date ASC
        """)
        requests = cursor.fetchall()
        
        for req in requests:
            # Get matched donors (accepted)
            cursor.execute("""
                SELECT d.donor_id, u.full_name, u.phone, dr.response
                FROM donor_responses dr
                JOIN donors d ON dr.donor_id = d.donor_id
                JOIN users u ON d.user_id = u.user_id
                WHERE dr.request_id = %s AND dr.response = 'accepted'
            """, (req['request_id'],))
            req['matched_donors'] = cursor.fetchall()

            # Get notification history (Approach History)
            cursor.execute("""
                SELECT n.sent_at, u.full_name, u.phone, n.status
                FROM notifications n
                JOIN donors d ON n.donor_id = d.donor_id
                JOIN users u ON d.user_id = u.user_id
                WHERE n.request_id = %s
                ORDER BY n.sent_at ASC
            """, (req['request_id'],))
            req['approach_history'] = cursor.fetchall()
        return jsonify(requests)
    finally:
        cursor.close()
        conn.close()

@volunteer_bp.route("/upcoming-patients", methods=["GET"])
def get_upcoming_patients_route():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT u.full_name, p.* FROM patients p JOIN users u ON p.user_id = u.user_id WHERE p.status = 'active'")
        all_patients = cursor.fetchall()
        upcoming = get_upcoming_patients(all_patients, days_ahead=7)
        return jsonify(upcoming)
    finally:
        cursor.close()
        conn.close()

@volunteer_bp.route("/request/close", methods=["POST"])
def close_request():
    data = request.json
    request_id = data['request_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE blood_requests SET status = 'completed' WHERE request_id = %s", (request_id,))
        conn.commit()
        return jsonify({"message": "Request closed and removed from dashboards."})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@volunteer_bp.route("/confirm-donation", methods=["POST"])
def confirm_donation():
    data = request.json
    donor_id = data.get('donor_id')
    request_id = data.get('request_id')
    
    print(f"[DEBUG] Confirming donation for Donor {donor_id}, Req {request_id}")
    
    if not donor_id or not request_id:
        return jsonify({"message": "Missing donor_id or request_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Fetch Request and Patient Info
        cursor.execute("""
            SELECT br.patient_id, p.frequency_in_days 
            FROM blood_requests br 
            JOIN patients p ON br.patient_id = p.patient_id 
            WHERE br.request_id = %s
        """, (request_id,))
        req_info = cursor.fetchone()
        
        if not req_info:
            print("[DEBUG] Request not found in database")
            return jsonify({"message": "Request not found"}), 404
            
        patient_id = req_info['patient_id']
        freq = req_info['frequency_in_days']

        # 2. Fetch Donor Info for AI Re-scoring
        cursor.execute("SELECT * FROM donors WHERE donor_id = %s", (donor_id,))
        donor = cursor.fetchone()
        if not donor:
            print("[DEBUG] Donor not found in database")
            return jsonify({"message": "Donor not found"}), 404
        
        # Calculate new stats
        new_donations = (donor['donations_till_date'] or 0) + 1
        new_calls = (donor['total_calls'] or 0) + 1
        
        # Ratio = Calls / Donations (Lower is better)
        new_ratio = round(new_calls / new_donations, 2)
        
        # Re-calculate AI Participation Score
        try:
            new_score = predict_participation_score(
                new_donations, 
                new_calls, 
                new_ratio, 
                True, # donated_earlier
                datetime.now().strftime('%Y-%m-%d')
            )
            
            # Logic: If it's a successful donation, the score should ideally increase or stay high.
            # If the AI model is sensitive to the ratio, we ensure it doesn't penalize a success.
            if donor['participation_score'] is not None:
                if new_score < donor['participation_score']:
                    # Reward the success manually if the model is too strict on the ratio
                    new_score = min(98, int(donor['participation_score'] + 2))
            else:
                new_score = max(new_score, 80) # Default high for new donors who donate
        except Exception as ai_err:
            print(f"[DEBUG] AI Rescoring Error: {ai_err}")
            new_score = (donor['participation_score'] or 50) + 5

        # 3. Update Donor
        cursor.execute("""
            UPDATE donors 
            SET last_donation_date = CURDATE(), 
                next_eligible_date = DATE_ADD(CURDATE(), INTERVAL 90 DAY),
                donations_till_date = %s,
                total_calls = %s,
                calls_to_donations_ratio = %s,
                participation_score = %s,
                donor_status = 'not_eligible'
            WHERE donor_id = %s
        """, (new_donations, new_calls, new_ratio, new_score, donor_id))
        
        # 4. Update Request
        cursor.execute("UPDATE blood_requests SET status = 'completed' WHERE request_id = %s", (request_id,))
        
        # 5. Record Donation
        cursor.execute("""
            INSERT INTO donations (donor_id, patient_id, request_id, donation_date) 
            VALUES (%s, %s, %s, CURDATE())
        """, (donor_id, patient_id, request_id))
        
        conn.commit()
        print(f"[DEBUG] Success! Donor stats updated for Donor {donor_id}. Patient update pending transfusion date.")
        return jsonify({
            "message": "Donation confirmed! Donor stats updated. Patient schedule will update on their transfusion date.",
            "new_score": new_score
        })
    except Exception as e:
        conn.rollback()
        print(f"[DEBUG] Confirm Donation Critical Error: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
