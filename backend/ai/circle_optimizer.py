from database.db import get_db_connection
import datetime

def evaluate_circle(patient_id):
    """
    Evaluates a patient's circle for weak donors (inactive twice) or long-serving donors.
    Returns a list of donor_ids recommended for replacement.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    recommendations = []
    
    try:
        # Get all donors in the circle
        cursor.execute("""
            SELECT dc.donor_id, u.full_name, d.participation_score, dc.added_on 
            FROM donor_circles dc
            JOIN donors d ON dc.donor_id = d.donor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE dc.patient_id = %s AND dc.active = TRUE
        """, (patient_id,))
        circle_donors = cursor.fetchall()
        
        today = datetime.date.today()
        
        for donor in circle_donors:
            donor_id = donor['donor_id']
            added_on = donor['added_on']
            
            # 1. Check for Tenure (9 months refresh)
            if added_on:
                if isinstance(added_on, datetime.datetime):
                    added_on = added_on.date()
                tenure_months = (today.year - added_on.year) * 12 + (today.month - added_on.month)
                if tenure_months >= 9:
                    recommendations.append({
                        'donor_id': donor_id,
                        'full_name': donor['full_name'],
                        'type': 'replace_donor',
                        'reason': f"Donor has served in this circle for {tenure_months} months. AI recommends refresh."
                    })
                    continue

            # 2. Check the last 2 requests where this donor was NOTIFIED
            cursor.execute("""
                SELECT n.request_id, dr.response 
                FROM notifications n
                LEFT JOIN donor_responses dr ON n.request_id = dr.request_id AND n.donor_id = dr.donor_id
                WHERE n.donor_id = %s
                ORDER BY n.sent_at DESC
                LIMIT 2
            """, (donor_id,))
            recent_notifications = cursor.fetchall()
            
            if len(recent_notifications) >= 2:
                failures = [r for r in recent_notifications if r['response'] != 'accepted']
                if len(failures) == 2:
                    recommendations.append({
                        'donor_id': donor_id,
                        'full_name': donor['full_name'],
                        'type': 'replace_donor',
                        'reason': 'Inactive for 2 consecutive notified requests.'
                    })
                    continue
            
            # 3. Participation score threshold
            if donor['participation_score'] < 30:
                recommendations.append({
                    'donor_id': donor_id,
                    'full_name': donor['full_name'],
                    'type': 'replace_donor',
                    'reason': f"AI Score ({donor['participation_score']}%) dropped below threshold."
                })
                
        return recommendations
    finally:
        cursor.close()
        conn.close()
