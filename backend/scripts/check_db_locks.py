import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def check_locks():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor(dictionary=True)
        print("Checking MySQL process list...")
        cursor.execute("SHOW PROCESSLIST")
        processes = cursor.fetchall()
        for p in processes:
            print(f"ID: {p['Id']} | User: {p['User']} | Command: {p['Command']} | Time: {p['Time']} | Info: {p['Info']}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_locks()
