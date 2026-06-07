from flask import Blueprint, request, jsonify
from database.db import get_db_connection

patient_bp = Blueprint("patient", __name__)

@patient_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_patient_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT u.full_name, u.email, u.phone, u.city, p.* 
        FROM users u 
        JOIN patients p ON u.user_id = p.user_id 
        WHERE u.user_id = %s
    """, (user_id,))
    patient = cursor.fetchone()
    
    if patient:
        # Calculate days until next transfusion
        from datetime import datetime
        if patient['expected_next_transfusion_date']:
            next_date = patient['expected_next_transfusion_date']
            if isinstance(next_date, str):
                next_date = datetime.strptime(next_date, "%Y-%m-%d").date()
            
            today = datetime.now().date()
            diff = (next_date - today).days
            patient['days_until_transfusion'] = max(0, diff)
        else:
            patient['days_until_transfusion'] = None
    
    cursor.close()
    conn.close()
    return jsonify(patient)

@patient_bp.route("/profile/update", methods=["PUT"])
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

@patient_bp.route("/circle/<int:patient_id>", methods=["GET"])
def get_patient_circle(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT u.full_name, u.phone, d.blood_group, d.participation_score, dc.ranking_position
        FROM donor_circles dc
        JOIN donors d ON dc.donor_id = d.donor_id
        JOIN users u ON d.user_id = u.user_id
        WHERE dc.patient_id = %s
        ORDER BY dc.ranking_position
    """, (patient_id,))
    circle = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(circle)

@patient_bp.route("/requests/<int:patient_id>", methods=["GET"])
def get_patient_requests(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM blood_requests 
        WHERE patient_id = %s 
        ORDER BY request_date DESC
    """, (patient_id,))
    requests = cursor.fetchall()
    
    for req in requests:
        # Get confirmed donors for each request
        cursor.execute("""
            SELECT u.full_name, dr.response_time
            FROM donor_responses dr
            JOIN donors d ON dr.donor_id = d.donor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE dr.request_id = %s AND dr.response = 'accepted'
        """, (req['request_id'],))
        req['confirmed_donors'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(requests)

@patient_bp.route("/request/create", methods=["POST"])
def create_request():
    data = request.json
    patient_id = data['patient_id']
    blood_group = data['blood_group']
    units_required = data.get('units_required', 1)
    urgency = data.get('urgency', 'normal')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO blood_requests (patient_id, blood_group, units_required, urgency)
        VALUES (%s, %s, %s, %s)
    """, (patient_id, blood_group, units_required, urgency))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Trigger automation to notify the first donor in the circle immediately
    from scripts.automated_task import run_automation
    try:
        run_automation()
    except Exception as e:
        print(f"Immediate Notification Error: {e}")

    return jsonify({"message": "Blood request created and circle notified!"})
