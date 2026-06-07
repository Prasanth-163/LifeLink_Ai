from flask import Blueprint, request, jsonify
from database.db import get_db_connection
from ai.donor_prediction import predict_participation_score
from utils.jwt_handler import verify_token

donor_bp = Blueprint("donor", __name__)

from datetime import datetime, timedelta

def calculate_eligibility(last_donation_date):
    if not last_donation_date:
        return 'eligible', None
    
    if isinstance(last_donation_date, str):
        last_date = datetime.strptime(last_donation_date, "%Y-%m-%d").date()
    else:
        last_date = last_donation_date
        
    next_eligible = last_date + timedelta(days=90)
    today = datetime.now().date()
    
    status = 'eligible' if today >= next_eligible else 'not_eligible'
    return status, next_eligible

@donor_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_donor_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT u.full_name, u.email, u.phone, u.city, d.* 
        FROM users u 
        JOIN donors d ON u.user_id = d.user_id 
        WHERE u.user_id = %s
    """, (user_id,))
    donor = cursor.fetchone()
    
    if not donor:
        cursor.close()
        conn.close()
        return jsonify({"message": "Donor not found"}), 404
    
    # Update eligibility
    status, next_eligible = calculate_eligibility(donor['last_donation_date'])
    
    # Update participation score using AI
    score = predict_participation_score(
        donor['donations_till_date'],
        donor['total_calls'],
        donor['calls_to_donations_ratio'],
        donor['donations_till_date'] > 0,
        donor['last_donation_date']
    )
    
    cursor.execute("""
        UPDATE donors 
        SET participation_score = %s, donor_status = %s, next_eligible_date = %s 
        WHERE donor_id = %s
    """, (score, status, next_eligible, donor['donor_id']))
    conn.commit()
    
    donor['participation_score'] = score
    donor['donor_status'] = status
    donor['next_eligible_date'] = next_eligible.strftime("%Y-%m-%d") if next_eligible else None
    
    cursor.close()
    conn.close()
    return jsonify(donor)

@donor_bp.route("/profile/update", methods=["PUT"])
def update_profile():
    data = request.json
    user_id = data['user_id']
    phone = data['phone']
    city = data['city']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users 
        SET phone = %s, city = %s 
        WHERE user_id = %s
    """, (phone, city, user_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Profile updated successfully"})

@donor_bp.route("/requests/<int:donor_id>", methods=["GET"])
def get_donor_requests(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get requests where donor is in the circle or it's a general pool request
    cursor.execute("""
        SELECT br.*, p_u.full_name as patient_name, p_u.city 
        FROM blood_requests br
        JOIN patients p ON br.patient_id = p.patient_id
        JOIN users p_u ON p.user_id = p_u.user_id
        JOIN donor_circles dc ON br.patient_id = dc.patient_id
        WHERE dc.donor_id = %s AND br.status = 'pending'
    """, (donor_id,))
    requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(requests)

@donor_bp.route("/respond", methods=["POST"])
def respond_to_request():
    data = request.json
    donor_id = data['donor_id']
    request_id = data['request_id']
    response = data['response'] # 'accepted' or 'declined'
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO donor_responses (donor_id, request_id, response, response_time)
        VALUES (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE response = %s, response_time = NOW()
    """, (donor_id, request_id, response, response))
    
    # Check if this is an escalated request
    cursor.execute("SELECT status FROM blood_requests WHERE request_id = %s", (request_id,))
    req = cursor.fetchone()
    
    if response == 'accepted':
        cursor.execute("UPDATE blood_requests SET status = 'matched' WHERE request_id = %s", (request_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    if req and req['status'] == 'escalated' and response == 'accepted':
        return jsonify({
            "message": "Response recorded successfully", 
            "escalated_message": "If you didn't receive another call within 1 hr then someone has already given blood and thank you."
        })

    return jsonify({"message": "Response recorded successfully"})

@donor_bp.route("/donation/confirm", methods=["POST"])
def confirm_donation():
    data = request.json
    donor_id = data['donor_id']
    request_id = data['request_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Get request details
        cursor.execute("SELECT patient_id FROM blood_requests WHERE request_id = %s", (request_id,))
        request_info = cursor.fetchone()
        if not request_info:
            return jsonify({"message": "Request not found"}), 404
            
        patient_id = request_info['patient_id']
        
        # 2. Record in donations table
        cursor.execute("""
            INSERT INTO donations (donor_id, patient_id, request_id, donation_date, status)
            VALUES (%s, %s, %s, CURDATE(), 'completed')
        """, (donor_id, patient_id, request_id))
        
        # 3. Update donor stats
        cursor.execute("""
            UPDATE donors 
            SET last_donation_date = CURDATE(), 
                donations_till_date = donations_till_date + 1,
                total_calls = total_calls + 1,
                calls_to_donations_ratio = (donations_till_date + 1) / (total_calls + 1)
            WHERE donor_id = %s
        """, (donor_id,))
        
        # 4. Update request status
        cursor.execute("UPDATE blood_requests SET status = 'completed' WHERE request_id = %s", (request_id,))
        
        conn.commit()
        return jsonify({"message": "Donation recorded! Your stats have been updated."})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
