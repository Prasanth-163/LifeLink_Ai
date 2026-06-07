import sys
import os

# Manual connection to avoid any path issues
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def cleanup_requests():
    print("Connecting to database...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        print("Connected.")

        # Set all active requests to completed
        print("Closing active requests...")
        cursor.execute("UPDATE blood_requests SET status = 'completed' WHERE status IN ('pending', 'matched', 'escalated')")
        affected_rows = cursor.rowcount

        # Clean up notifications
        print("Clearing notifications...")
        cursor.execute("DELETE FROM notifications")
        
        # Clean up donor responses (pending ones)
        print("Clearing pending responses...")
        cursor.execute("DELETE FROM donor_responses WHERE response = 'pending'")

        conn.commit()
        print(f"Successfully closed {affected_rows} active care requests.")
        print("Cleared notification and pending response history.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_requests()
