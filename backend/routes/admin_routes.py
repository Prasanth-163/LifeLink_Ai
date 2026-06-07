from flask import Blueprint, request, jsonify
from database.db import get_db_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/stats", methods=["GET"])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total counts
    cursor.execute("SELECT COUNT(*) as total_donors FROM donors")
    total_donors = cursor.fetchone()['total_donors']
    
    cursor.execute("SELECT COUNT(*) as total_patients FROM patients")
    total_patients = cursor.fetchone()['total_patients']
    
    cursor.execute("SELECT COUNT(*) as total_requests FROM blood_requests")
    total_requests = cursor.fetchone()['total_requests']
    
    # Success Rate (Completed Requests / Total Requests)
    cursor.execute("SELECT COUNT(*) as completed FROM blood_requests WHERE status = 'completed'")
    completed = cursor.fetchone()['completed']
    success_rate = (completed / total_requests * 100) if total_requests > 0 else 0
    
    # Average Participation Score
    cursor.execute("SELECT AVG(participation_score) as avg_score FROM donors")
    avg_score = cursor.fetchone()['avg_score'] or 0
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "total_donors": total_donors,
        "total_patients": total_patients,
        "total_requests": total_requests,
        "success_rate": round(success_rate, 2),
        "avg_participation_score": round(avg_score, 2)
    })
