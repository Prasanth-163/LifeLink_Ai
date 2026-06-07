import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
from database.db import get_db_connection
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT email FROM users WHERE role = 'donor' AND email LIKE 'donor_%@example.com' LIMIT 5")
donors = cursor.fetchall()
print('\n--- DATASET DONORS ---')
if not donors:
    print('No dataset donors found. Did you run import_dataset.py?')
else:
    for d in donors:
        print(f'Email: {d["email"]} | Password: password123')
print('----------------------\n')
