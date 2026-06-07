import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv
import bcrypt
import datetime

load_dotenv()

def map_blood_group(bg):
    if not bg or pd.isna(bg): return None
    bg = bg.strip().lower()
    mapping = {
        'a positive': 'A+',
        'a negative': 'A-',
        'b positive': 'B+',
        'b negative': 'B-',
        'o positive': 'O+',
        'o negative': 'O-',
        'ab positive': 'AB+',
        'ab negative': 'AB-'
    }
    return mapping.get(bg, bg[:5]) # Fallback to first 5 chars if not matched

def import_dataset():
    df = pd.read_csv('dataset/Dataset.csv')
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()
    
    print(f"Starting import of {len(df)} records...")
    
    # Filter donors
    donors_df = df[df['role'].isin(['Emergency Donor', 'Bridge Donor'])].head(200)
    
    imported_count = 0
    for _, row in donors_df.iterrows():
        try:
            u_id_str = str(row['user_id'])
            # Use part of the hash as unique identifier to avoid duplicates
            email = f"donor_{u_id_str[10:20]}@example.com"
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone(): continue
            
            phone = f"+91{u_id_str[2:12]}" # Mock unique phone
            cursor.execute("SELECT user_id FROM users WHERE phone = %s", (phone,))
            if cursor.fetchone(): continue

            pwd = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
            dob = "1990-01-01"
            
            cursor.execute("""
                INSERT INTO users (full_name, email, phone, password_hash, dob, city, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (f"Donor {u_id_str[2:7]}", email, phone, pwd, dob, "Hyderabad", 'donor'))
            
            user_id = cursor.lastrowid
            
            blood_group = map_blood_group(row['blood_group'])
            last_don = row['last_donation_date'] if pd.notna(row['last_donation_date']) else None
            if last_don:
                try:
                    last_don = pd.to_datetime(last_don).strftime('%Y-%m-%d')
                except:
                    last_don = None
            
            from ai.donor_prediction import predict_participation_score
            
            donations = row['donations_till_date'] if pd.notna(row['donations_till_date']) else 0
            calls = row['total_calls'] if pd.notna(row['total_calls']) else 0
            ratio = row['calls_to_donations_ratio'] if pd.notna(row['calls_to_donations_ratio']) else 0
            
            score = predict_participation_score(donations, calls, ratio, donations > 0, last_don)

            cursor.execute("""
                INSERT INTO donors (user_id, blood_group, last_donation_date, donations_till_date, total_calls, calls_to_donations_ratio, participation_score, donor_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, 
                blood_group, 
                last_don,
                donations,
                calls,
                ratio,
                score,
                'eligible' if row['eligibility_status'] == 'eligible' else 'not_eligible'
            ))
            imported_count += 1
        except Exception as e:
            # print(f"Error importing row: {e}")
            continue
            
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Dataset import completed. Imported {imported_count} new donors.")

if __name__ == "__main__":
    import_dataset()
