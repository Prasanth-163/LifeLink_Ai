from ai.donor_prediction import predict_participation_score

def get_compatible_blood_groups(patient_blood_group):
    compatibility = {
        'A+': ['A+', 'A-', 'O+', 'O-'],
        'A-': ['A-', 'O-'],
        'B+': ['B+', 'B-', 'O+', 'O-'],
        'B-': ['B-', 'O-'],
        'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'AB-': ['A-', 'B-', 'AB-', 'O-'],
        'O+': ['O+', 'O-'],
        'O-': ['O-']
    }
    return compatibility.get(patient_blood_group, [])

def rank_donors(donors, patient_blood_group):
    """
    donors: list of dicts with donor info
    """
    compatible_groups = get_compatible_blood_groups(patient_blood_group)
    
    eligible_donors = [d for d in donors if d['blood_group'] in compatible_groups and d.get('donor_status') == 'eligible']
    
    for donor in eligible_donors:
        # Use AI prediction if not already scored or to ensure freshness
        if 'participation_score' not in donor or donor['participation_score'] == 50.0:
            donor['participation_score'] = predict_participation_score(
                donor.get('donations_till_date', 0),
                donor.get('total_calls', 0),
                donor.get('calls_to_donations_ratio', 0),
                donor.get('donations_till_date', 0) > 0,
                donor.get('last_donation_date')
            )
        
        # Weighted Ranking: 80% Participation Score, 20% Historical Volume
        score = (donor['participation_score'] * 0.8) + (min(donor.get('donations_till_date', 0), 10) * 2)
        donor['ranking_score'] = score

    ranked_donors = sorted(eligible_donors, key=lambda x: x.get('ranking_score', 0), reverse=True)
    return ranked_donors
