from database.db import get_db_connection

class DonorModel:
    @staticmethod
    def create_donor(user_id, blood_group, last_donation_date=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate next eligible date if last_donation_date is provided (typically 90 days for men)
        # For simplicity, we can default it or handle it in business logic
        
        cursor.execute(
            """
            INSERT INTO donors (user_id, blood_group, last_donation_date)
            VALUES (%s, %s, %s)
            """,
            (user_id, blood_group, last_donation_date)
        )
        conn.commit()
        cursor.close()
        conn.close()
