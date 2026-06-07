from database.db import get_db_connection

class PatientModel:
    @staticmethod
    def create_patient(user_id, blood_group, frequency_in_days, expected_next_transfusion_date):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO patients (user_id, blood_group, frequency_in_days, expected_next_transfusion_date)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, blood_group, frequency_in_days, expected_next_transfusion_date)
        )
        patient_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return patient_id
