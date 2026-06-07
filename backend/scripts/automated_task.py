import sys
import os
import datetime
import time

# Add the backend directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db_connection
from ai.scheduler import get_upcoming_patients
from ai.circle_optimizer import evaluate_circle
from services.notification_service import notify_donor, notify_general_pool, notify_volunteers
from services.circle_service import CircleService

def run_automation():
    print(f"[{datetime.datetime.now()}] AI Agent Heartbeat: Checking network state...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Proactive Request Creation (5 Days Lead Time)
        cursor.execute("""
            SELECT u.full_name, u.city, p.* 
            FROM patients p 
            JOIN users u ON p.user_id = u.user_id 
            WHERE p.status = 'active'
            AND p.expected_next_transfusion_date <= DATE_ADD(CURDATE(), INTERVAL 5 DAY)
        """)
        due_patients = cursor.fetchall()
        
        for patient in due_patients:
            cursor.execute("""
                SELECT request_id FROM blood_requests 
                WHERE patient_id = %s AND status IN ('pending', 'matched', 'escalated')
                AND request_date > DATE_SUB(NOW(), INTERVAL %s DAY)
            """, (patient['patient_id'], patient['frequency_in_days'] - 2))
            
            if not cursor.fetchone():
                print(f"Proactive Action: Raising request for {patient['full_name']} (Transfusion in <= 5 days)")
                cursor.execute("""
                    INSERT INTO blood_requests (patient_id, blood_group, units_required, urgency)
                    VALUES (%s, %s, %s, 'normal')
                """, (patient['patient_id'], patient['blood_group'], patient['units_required']))
                conn.commit()
                
                cursor.execute("SELECT u.full_name, u.email FROM users u WHERE u.role = 'volunteer' AND u.city = %s", (patient['city'],))
                volunteers = cursor.fetchall()
                for vol in volunteers:
                    notify_volunteers(vol, patient, 'normal')

        # 2. Rank 1 -> Rank 2 -> Emergency Escalation Logic
        cursor.execute("""
            SELECT br.*, p.blood_group as patient_blood_group, u.full_name as patient_name, u.city as patient_city 
            FROM blood_requests br
            JOIN patients p ON br.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE br.status IN ('pending', 'matched', 'escalated')
        """)
        active_requests = cursor.fetchall()

        for req in active_requests:
            request_id = req['request_id']
            patient_id = req['patient_id']
            req_status = req['status']

            cursor.execute("""
                SELECT dc.donor_id, u.full_name, u.email, u.phone
                FROM donor_circles dc
                JOIN donors d ON dc.donor_id = d.donor_id
                JOIN users u ON d.user_id = u.user_id
                WHERE dc.patient_id = %s AND d.donor_status = 'eligible'
                ORDER BY dc.ranking_position ASC
                LIMIT 2
            """, (patient_id,))
            circle_donors = cursor.fetchall()

            cursor.execute("SELECT donor_id, sent_at FROM notifications WHERE request_id = %s ORDER BY sent_at ASC", (request_id,))
            notified_history = cursor.fetchall()
            
            if not notified_history:
                if circle_donors:
                    first_donor = circle_donors[0]
                    print(f"Notification Sent: Circle Rank 1 -> {first_donor['full_name']} (Req ID: {request_id})")
                    cursor.execute("""
                        INSERT INTO notifications (donor_id, request_id, message, sent_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (first_donor['donor_id'], request_id, "Critical: Blood needed for circle patient."))
                    notify_donor(first_donor, req, req['urgency'])
                    conn.commit()
                else:
                    cursor.execute("UPDATE blood_requests SET status = 'escalated' WHERE request_id = %s", (request_id,))
                    conn.commit()
            else:
                if req_status != 'escalated' and req_status != 'completed':
                    latest_notification = notified_history[-1]
                    last_donor_id = latest_notification['donor_id']
                    last_sent_at = latest_notification['sent_at']
                    
                    time_elapsed = datetime.datetime.now() - last_sent_at
                    if time_elapsed.total_seconds() > 86400: # 24 Hours
                        if len(circle_donors) > 1 and last_donor_id == circle_donors[0]['donor_id']:
                            next_donor = circle_donors[1]
                            print(f"Notification Sent: Circle Rank 2 -> {next_donor['full_name']}")
                            cursor.execute("""
                                INSERT INTO notifications (donor_id, request_id, message, sent_at)
                                VALUES (%s, %s, %s, NOW())
                            """, (next_donor['donor_id'], request_id, "Emergency: Previous circle donor unavailable."))
                            notify_donor(next_donor, req, req['urgency'])
                            cursor.execute("UPDATE blood_requests SET status = 'pending' WHERE request_id = %s", (request_id,))
                            conn.commit()
                        else:
                            cursor.execute("UPDATE blood_requests SET status = 'escalated' WHERE request_id = %s", (request_id,))
                            conn.commit()

            if req_status == 'escalated':
                cursor.execute("""
                    SELECT d.donor_id, u.full_name, u.email 
                    FROM donors d
                    JOIN users u ON d.user_id = u.user_id
                    WHERE d.blood_group = %s AND d.donor_status = 'eligible' 
                    AND d.donor_id NOT IN (SELECT donor_id FROM donor_circles)
                    AND d.donor_id NOT IN (SELECT donor_id FROM notifications WHERE request_id = %s)
                """, (req['patient_blood_group'], request_id))
                emergency_donors = cursor.fetchall()
                
                for ed in emergency_donors:
                    notify_general_pool(ed, req)
                    cursor.execute("""
                        INSERT INTO notifications (donor_id, request_id, message, sent_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (ed['donor_id'], request_id, "Emergency Pool Alert: Urgent blood needed in your city."))

                cursor.execute("SELECT u.full_name, u.email FROM users u WHERE u.role = 'volunteer' AND u.city = %s", (req['patient_city'],))
                city_volunteers = cursor.fetchall()
                for vol in city_volunteers:
                    notify_volunteers(vol, {'city': req['patient_city'], 'blood_group': req['patient_blood_group']}, req['urgency'])
                conn.commit()

        # 3. Update Patient Stats on Transfusion Date
        print(f"[{datetime.datetime.now()}] Checking for matured transfusion cycles...")
        cursor.execute("""
            SELECT p.patient_id, p.expected_next_transfusion_date, p.frequency_in_days, br.request_id, u.full_name
            FROM patients p
            JOIN blood_requests br ON p.patient_id = br.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE br.status = 'completed' 
            AND p.expected_next_transfusion_date <= CURDATE()
        """)
        matured_cycles = cursor.fetchall()

        for cycle in matured_cycles:
            next_date = datetime.date.today() + datetime.timedelta(days=cycle['frequency_in_days'])
            cursor.execute("""
                UPDATE patients 
                SET last_transfusion_date = %s, expected_next_transfusion_date = %s 
                WHERE patient_id = %s
            """, (cycle['expected_next_transfusion_date'], next_date, cycle['patient_id']))
            conn.commit()

        # 4. AI Circle Optimization (Self-Healing Network)
        print(f"[{datetime.datetime.now()}] AI Agent: Evaluating network health...")
        cursor.execute("SELECT patient_id FROM patients WHERE status = 'active'")
        active_patients = cursor.fetchall()
        
        for p in active_patients:
            recommendations = evaluate_circle(p['patient_id'])
            for rec in recommendations:
                if rec['type'] == 'replace_donor':
                    print(f"AI Success: Replacing inactive donor {rec['donor_id']} for Patient {p['patient_id']}")
                    CircleService.replace_donor(p['patient_id'], rec['donor_id'])

    except Exception as e:
        print(f"AI Agent Heartbeat Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_automation()
