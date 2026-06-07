import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection

def check_donors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT u.full_name, d.donations_till_date, d.total_calls, d.calls_to_donations_ratio, d.participation_score FROM users u JOIN donors d ON u.user_id = d.user_id LIMIT 10")
    donors = cursor.fetchall()
    print("\n--- Donor Stats Check ---")
    for d in donors:
        print(f"Donor: {d['full_name']} | Donations: {d['donations_till_date']} | Calls: {d['total_calls']} | Ratio: {d['calls_to_donations_ratio']} | Score: {d['participation_score']}")
    conn.close()

if __name__ == "__main__":
    check_donors()
