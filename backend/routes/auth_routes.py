from flask import Blueprint, request, jsonify
import bcrypt
import datetime
from database.db import get_db_connection
from models.user_model import UserModel
from models.donor_model import DonorModel
from models.patient_model import PatientModel
from services.circle_service import CircleService
from utils.jwt_handler import generate_token

auth_bp = Blueprint("auth", __name__)

def calculate_age(dob_str):
    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        full_name = data["full_name"]
        email = data["email"]
        phone = data["phone"]
        password = data["password"]
        dob = data["dob"]
        city = data["city"]
        role = data["role"]

        # Age validation for donors
        if role == "donor":
            age = calculate_age(dob)
            if age < 18:
                return jsonify({"message": "You must be at least 18 years old to register as a donor."}), 400

        existing_user = UserModel.get_user_by_email(email)
        if existing_user:
            return jsonify({"message": "Email already exists"}), 400

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Start transaction
        conn.start_transaction()

        cursor.execute(
            """
            INSERT INTO users (full_name, email, phone, password_hash, dob, city, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (full_name, email, phone, hashed_password.decode(), dob, city, role)
        )
        user_id = cursor.lastrowid

        # Handle Role-Specific Tables
        if role == "donor":
            blood_group = data.get("blood_group")
            last_donation_date = data.get("last_donation_date")
            # Handle empty string for optional date
            if not last_donation_date or last_donation_date == "":
                last_donation_date = None
            
            cursor.execute(
                """
                INSERT INTO donors (user_id, blood_group, last_donation_date)
                VALUES (%s, %s, %s)
                """,
                (user_id, blood_group, last_donation_date)
            )
        elif role == "patient":
            blood_group = data.get("blood_group")
            frequency_in_days = data.get("frequency_in_days")
            expected_next_transfusion_date = data.get("expected_next_transfusion_date")
            
            # Validation: Expected next transfusion date cannot be in the past
            today = datetime.date.today()
            expected_date = datetime.datetime.strptime(expected_next_transfusion_date, "%Y-%m-%d").date()
            if expected_date < today:
                return jsonify({"message": "Expected next transfusion date cannot be in the past."}), 400
            
            cursor.execute(
                """
                INSERT INTO patients (user_id, blood_group, frequency_in_days, expected_next_transfusion_date)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, blood_group, frequency_in_days, expected_next_transfusion_date)
            )
            patient_id = cursor.lastrowid
            # Create AI-generated donor circle
            # Note: CircleService currently opens its own connection. 
            # For a hackathon, this is okay, but ideally it should use the same cursor/transaction.
            # However, create_initial_circle selects from donors, so we should commit first or pass the connection.
            # Let's keep it simple for now and commit before calling CircleService if needed, 
            # but actually CircleService is better called after a successful commit.
        
        conn.commit()

        # Call CircleService and raise initial request after commit for patients
        if role == "patient":
            try:
                # 1. Create the circle
                CircleService.create_initial_circle(patient_id)
                
                # 2. Raise the initial blood request immediately
                # Re-opening cursor to work with committed data
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                # Fetch patient info again to be safe
                cursor.execute("SELECT patient_id, blood_group FROM patients WHERE patient_id = %s", (patient_id,))
                p_info = cursor.fetchone()
                
                if p_info:
                    print(f"Raising initial request for new patient: {p_info['patient_id']}")
                    cursor.execute("""
                        INSERT INTO blood_requests (patient_id, blood_group, units_required, urgency, status)
                        VALUES (%s, %s, %s, 'normal', 'pending')
                    """, (p_info['patient_id'], p_info['blood_group'], 1))
                    conn.commit()
                    
                    # 3. Trigger immediate notification logic (Heartbeat)
                    from scripts.automated_task import run_automation
                    run_automation()
            except Exception as e:
                print(f"Post-Registration Flow Error: {e}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()

        return jsonify({"message": "Registration Successful", "user_id": user_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    data = request.json

    email = data["email"]
    password = data["password"]

    user = UserModel.get_user_by_email(email)

    if not user:

        return jsonify({
            "message": "Invalid Email"
        }), 401

    valid = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not valid:

        return jsonify({
            "message": "Invalid Password"
        }), 401

    token = generate_token(user)

    return jsonify({
        "message": "Login Successful",
        "token": token,
        "role": user["role"],
        "user_id": user["user_id"]
    })