import sys
import os
from datetime import datetime, timedelta

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db_connection
from ai.donor_prediction import predict_participation_score

def manual_test_confirm():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Create a dummy patient if none exists
        cursor.execute("SELECT patient_id FROM patients LIMIT 1")
        p = cursor.fetchone()
        if not p:
            print("No patients found. Create one first.")
            return
        patient_id = p['patient_id']
        
        # Create a dummy donor if none exists
        cursor.execute("SELECT donor_id FROM donors LIMIT 1")
        d = cursor.fetchone()
        if not d:
            print("No donors found.")
            return
        donor_id = d['donor_id']
        
        # Create a dummy request
        cursor.execute("INSERT INTO blood_requests (patient_id, blood_group, units_required) VALUES (%s, 'O+', 1)", (patient_id,))
        request_id = cursor.lastrowid
        conn.commit()
        
        print(f"Attempting to confirm Request ID: {request_id} for Donor ID: {donor_id}")
        
        # --- SIMULATE ROUTE LOGIC ---
        cursor.execute("""
            SELECT br.patient_id, br.units_required, p.frequency_in_days 
            FROM blood_requests br 
            JOIN patients p ON br.patient_id = p.patient_id 
            WHERE br.request_id = %s
        """, (request_id,))
        req_info = cursor.fetchone()
        
        if not req_info:
            print("Request info not found")
            return
            
        patient_id = req_info['patient_id']
        freq = req_info['frequency_in_days']

        cursor.execute("SELECT * FROM donors WHERE donor_id = %s", (donor_id,))
        donor = cursor.fetchone()
        
        new_donations = donor['donations_till_date'] + 1
        new_calls = donor['total_calls'] + 1
        new_ratio = round(new_calls / new_donations, 2)
        
        print(f"New Stats -> Don: {new_donations}, Calls: {new_calls}, Ratio: {new_ratio}")

        new_score = predict_participation_score(
            new_donations, 
            new_calls, 
            new_ratio, 
            True,
            datetime.now().strftime('%Y-%m-%d')
        )
        print(f"Predicted AI Score: {new_score}")
        
        if new_score < donor['participation_score'] and new_donations > donor['donations_till_date']:
            print(f"Score dropped from {donor['participation_score']} to {new_score}. Applying correction...")
            new_score = min(95, int(donor['participation_score'] + 5))
            print(f"Corrected Score: {new_score}")

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
        
        cursor.execute("UPDATE blood_requests SET status = 'completed' WHERE request_id = %s", (request_id,))
        
        next_date = datetime.now().date() + timedelta(days=freq)
        cursor.execute("""
            UPDATE patients 
            SET last_transfusion_date = CURDATE(), 
                expected_next_transfusion_date = %s 
            WHERE patient_id = %s
        """, (next_date, patient_id))
        
        cursor.execute("""
            INSERT INTO donations (donor_id, patient_id, request_id, donation_date) 
            VALUES (%s, %s, %s, CURDATE())
        """, (donor_id, patient_id, request_id))
        
        conn.commit()
        print("SUCCESS: Donation confirmed and statistics updated.")
        
    except Exception as e:
        conn.rollback()
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    manual_test_confirm()
