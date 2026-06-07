import sys
import os
import mysql.connector
from dotenv import load_dotenv

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def final_health_check():
    print("--- LifeLink AI Final Health Check ---")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor(dictionary=True)
        
        # 1. Check Requests
        cursor.execute("SELECT COUNT(*) as count FROM blood_requests WHERE status IN ('pending', 'matched', 'escalated')")
        active_count = cursor.fetchone()['count']
        print(f"[DB] Active Requests: {active_count} (Expected: 0)")
        
        # 2. Check Dataset Donors
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE email LIKE 'dataset_donor_%'")
        donor_count = cursor.fetchone()['count']
        print(f"[DB] Dataset Donors: {donor_count} (Expected: ~298)")
        
        # 3. Check Circles
        cursor.execute("SELECT COUNT(*) as count FROM donor_circles")
        circle_count = cursor.fetchone()['count']
        print(f"[DB] Total Circle Assignments: {circle_count}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] DB Check Failed: {e}")

    # 4. Check File Integrity
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        
        auto_task_path = os.path.join(script_dir, 'automated_task.py')
        vol_route_path = os.path.join(root_dir, 'routes', 'volunteer_routes.py')
        circle_service_path = os.path.join(root_dir, 'services', 'circle_service.py')

        with open(auto_task_path, 'r') as f:
            content = f.read()
            if 'while True' in content:
                print("[FILE] WARNING: infinite loop still present in automated_task.py")
            else:
                print("[FILE] SUCCESS: infinite loop removed from automated_task.py")
        
        with open(vol_route_path, 'r') as f:
            content = f.read()
            if 'run_automation()' in content and 'get_active_requests' in content:
                print("[FILE] SUCCESS: Heartbeat automation present in volunteer routes")
            else:
                print("[FILE] WARNING: Heartbeat automation missing in volunteer routes")

        with open(circle_service_path, 'r') as f:
            content = f.read()
            if 'len(top_8)' in content:
                print("[FILE] WARNING: Typo top_8 still exists in circle_service.py")
            else:
                print("[FILE] SUCCESS: Typo fixed in circle_service.py")

    except Exception as e:
        print(f"[ERROR] File Check Failed: {e}")

if __name__ == "__main__":
    final_health_check()
