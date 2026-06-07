import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def kill_stuck_processes():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW PROCESSLIST")
        processes = cursor.fetchall()
        
        killed_count = 0
        for p in processes:
            # Kill processes that have been running for more than 100 seconds and are not Sleep/Daemon
            if p['Time'] > 60 and p['Command'] != 'Sleep' and p['Command'] != 'Daemon' and p['User'] == 'root':
                print(f"Killing Process ID: {p['Id']} | Info: {p['Info']}")
                cursor.execute(f"KILL {p['Id']}")
                killed_count += 1
        
        conn.commit()
        print(f"Successfully killed {killed_count} stuck processes.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    kill_stuck_processes()
