import requests
import json

def test_confirm_donation():
    url = "http://localhost:5000/api/volunteer/confirm-donation"
    
    # We need a valid request_id and donor_id from the database
    # For testing, let's assume we have them or create a mock if possible
    # But since I can't easily create a mock via requests without auth, 
    # I'll just check if the route exists and returns a 400 for missing data
    
    print("Testing missing data...")
    response = requests.post(url, json={})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    print("\nTesting invalid IDs...")
    response = requests.post(url, json={"request_id": 9999, "donor_id": 9999})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    # Note: This requires the server to be running.
    # Since I am in a CLI, I'll run the logic directly in a script instead.
    pass
