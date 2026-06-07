import sys
import os
from datetime import datetime

# Add root to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ai.donor_prediction import predict_participation_score

def test_prediction():
    print("Testing AI Prediction Score...")
    try:
        # Case 1: New donor (0/0) -> 1 donation, 1 call
        score1 = predict_participation_score(1, 1, 1.0, True, datetime.now().strftime('%Y-%m-%d'))
        print(f"Case 1 (1/1, Ratio 1.0): Score = {score1}%")

        # Case 2: Experienced donor (10/10) -> 11 donations, 11 calls
        score2 = predict_participation_score(11, 11, 1.0, True, datetime.now().strftime('%Y-%m-%d'))
        print(f"Case 2 (11/11, Ratio 1.0): Score = {score2}%")

        # Case 3: Poor donor (1 donation, 20 calls)
        score3 = predict_participation_score(1, 20, 20.0, True, datetime.now().strftime('%Y-%m-%d'))
        print(f"Case 3 (1/20, Ratio 20.0): Score = {score3}%")

    except Exception as e:
        print(f"Prediction Error: {e}")

if __name__ == "__main__":
    test_prediction()
