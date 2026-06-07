from datetime import datetime, timedelta

def predict_next_transfusion(last_transfusion_date, frequency_in_days):
    if not last_transfusion_date:
        return datetime.now().date() + timedelta(days=7) # Default to 1 week from now if no data
    
    if isinstance(last_transfusion_date, str):
        last_date = datetime.strptime(last_transfusion_date, "%Y-%m-%d").date()
    else:
        last_date = last_transfusion_date
        
    return last_date + timedelta(days=frequency_in_days)

def get_upcoming_patients(patients, days_ahead=7):
    """
    patients: list of patients with expected_next_transfusion_date
    """
    today = datetime.now().date()
    threshold = today + timedelta(days=days_ahead)
    
    upcoming = []
    for patient in patients:
        next_date = patient['expected_next_transfusion_date']
        if isinstance(next_date, str):
            next_date = datetime.strptime(next_date, "%Y-%m-%d").date()
            
        if today <= next_date <= threshold:
            upcoming.append(patient)
            
    return upcoming
