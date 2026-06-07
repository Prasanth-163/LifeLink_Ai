import os
from dotenv import load_dotenv
load_dotenv()
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection

def find_volunteer():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT email, full_name, city FROM users WHERE role = 'volunteer' LIMIT 1")
    vol = cursor.fetchone()
    if vol:
        print(f"EXISTING_VOLUNTEER_EMAIL={vol['email']}")
        print(f"EXISTING_VOLUNTEER_CITY={vol['city']}")
    else:
        print("NO_VOLUNTEER")
    conn.close()

if __name__ == "__main__":
    find_volunteer()
