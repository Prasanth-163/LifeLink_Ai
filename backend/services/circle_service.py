from database.db import get_db_connection
from ai.donor_ranking import rank_donors

class CircleService:
    @staticmethod
    def create_initial_circle(patient_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # 1. Get patient's blood group
            cursor.execute("SELECT blood_group FROM patients WHERE patient_id = %s", (patient_id,))
            patient = cursor.fetchone()
            if not patient:
                return False

            blood_group = patient['blood_group']

            # 2. Get all eligible donors who are NOT in any circle yet
            # CRITICAL: Enforce One-Donor-One-Circle rule
            cursor.execute("""
                SELECT d.*, u.full_name, u.city FROM donors d
                JOIN users u ON d.user_id = u.user_id
                WHERE d.donor_id NOT IN (SELECT donor_id FROM donor_circles)
                AND d.donor_status = 'eligible' 
                AND d.active_status = TRUE
            """)
            all_available_donors = cursor.fetchall()

            if len(all_available_donors) < 1:
                print(f"No available donors found for Patient ID {patient_id}")
                return False

            # 3. Use AI to rank them based on compatibility and scores
            # This rank_donors call already uses AI Participation Scores internally
            ranked_donors = rank_donors(all_available_donors, blood_group)

            # 4. Take top 8 (or all available if less than 8) and assign to circle
            num_to_assign = min(len(ranked_donors), 8)
            top_donors = ranked_donors[:num_to_assign]
            
            for i, donor in enumerate(top_donors):
                cursor.execute("""
                    INSERT INTO donor_circles (patient_id, donor_id, ranking_position)
                    VALUES (%s, %s, %s)
                """, (patient_id, donor['donor_id'], i + 1))

            conn.commit()
            print(f"Created circle with {len(top_donors)} donors for Patient ID {patient_id}")
            return True
        except Exception as e:
            print(f"Error creating circle: {e}")
            conn.rollback()
            return False
    @staticmethod
    def replace_donor(patient_id, old_donor_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Get patient info
            cursor.execute("SELECT blood_group FROM patients WHERE patient_id = %s", (patient_id,))
            patient = cursor.fetchone()
            if not patient: return False
            
            # 2. Find a new donor from general pool (not in any circle)
            cursor.execute("""
                SELECT d.* FROM donors d
                WHERE d.donor_id NOT IN (SELECT donor_id FROM donor_circles)
                AND d.blood_group = %s AND d.donor_status = 'eligible' AND d.active_status = TRUE
                ORDER BY d.participation_score DESC
                LIMIT 1
            """, (patient['blood_group'],))
            new_donor = cursor.fetchone()
            
            if not new_donor:
                print(f"Optimization Alert: No replacement available for Patient {patient_id}")
                return False
                
            # 3. Swap in circle
            cursor.execute("SELECT ranking_position FROM donor_circles WHERE patient_id = %s AND donor_id = %s", (patient_id, old_donor_id))
            res = cursor.fetchone()
            pos = res['ranking_position'] if res else 8
            
            cursor.execute("DELETE FROM donor_circles WHERE patient_id = %s AND donor_id = %s", (patient_id, old_donor_id))
            cursor.execute("""
                INSERT INTO donor_circles (patient_id, donor_id, ranking_position)
                VALUES (%s, %s, %s)
            """, (patient_id, new_donor['donor_id'], pos))
            
            # 4. Log Recommendation for History
            cursor.execute("""
                INSERT INTO ai_recommendations (patient_id, donor_id, recommendation_type, reason, status)
                VALUES (%s, %s, 'replace_donor', 'Autonomous replacement of inactive donor.', 'approved')
            """, (patient_id, old_donor_id))
            
            conn.commit()
            print(f"AI Success: Donor {old_donor_id} replaced by {new_donor['donor_id']} in Circle {patient_id}")
            return True
        except Exception as e:
            print(f"Replacement Error: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
