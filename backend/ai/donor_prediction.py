import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "donor_model.pkl")
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dataset", "Dataset.csv")

def train_model():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)

    # Preprocessing
    # Features mentioned in prompt: donations_till_date, total_calls, calls_to_donations_ratio, donated_earlier, active_status, last_donation_date
    
    # Target: user_donation_active_status (Active/Inactive)
    df['target'] = df['user_donation_active_status'].map({'Active': 1, 'Inactive': 0})
    df = df.dropna(subset=['target'])

    # Feature engineering
    df['donations_till_date'] = df['donations_till_date'].fillna(0)
    df['total_calls'] = df['total_calls'].fillna(0)
    df['calls_to_donations_ratio'] = df['calls_to_donations_ratio'].fillna(0)
    df['donated_earlier'] = df['donated_earlier'].fillna(False).astype(int)
    
    # Convert last_donation_date to days since (using a fixed reference date if needed, or just year)
    # For simplicity, let's just use year or months. 
    # Let's extract year from last_donation_date
    df['last_donation_year'] = pd.to_datetime(df['last_donation_date'], errors='coerce').dt.year.fillna(0)

    features = ['donations_till_date', 'total_calls', 'calls_to_donations_ratio', 'donated_earlier', 'last_donation_year']
    X = df[features]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")
    
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy:.2f}")

def predict_participation_score(donations_till_date, total_calls, calls_to_donations_ratio, donated_earlier, last_donation_date):
    if not os.path.exists(MODEL_PATH):
        train_model()
    
    model = joblib.load(MODEL_PATH)
    
    # Preprocess inputs
    donated_earlier_int = 1 if donated_earlier else 0
    last_donation_year = pd.to_datetime(last_donation_date, errors='coerce').year if last_donation_date else 0
    if pd.isna(last_donation_year): last_donation_year = 0
    
    input_data = np.array([[donations_till_date, total_calls, calls_to_donations_ratio, donated_earlier_int, last_donation_year]])
    
    # Get probability of being "Active" (1)
    probability = model.predict_proba(input_data)[0][1]
    
    return int(probability * 100)

if __name__ == "__main__":
    train_model()
