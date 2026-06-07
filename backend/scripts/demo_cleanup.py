import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection

def cleanup():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # 1. Clear old duplicate requests
    cursor.execute("UPDATE blood_requests SET status = 'completed' WHERE status IN ('pending', 'matched', 'escalated')")
    # 2. Reset a few donors to 0 for realistic testing
    cursor.execute("UPDATE donors SET donations_till_date = 0, total_calls = 0, calls_to_donations_ratio = 0, participation_score = 50.0 LIMIT 5")
    conn.commit()
    print('Cleaned up active requests and reset 5 donors to zero-state for testing.')
    conn.close()

if __name__ == "__main__":
    cleanup()
