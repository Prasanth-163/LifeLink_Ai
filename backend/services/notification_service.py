import datetime

def send_email_notification(donor_email, subject, body):
    # Simulated email sending
    print(f"[EMAIL MOCK] To: {donor_email} | Subject: {subject}")
    print(f"Body: {body}\n")

def send_sms_notification(phone, text):
    print(f"[SMS MOCK] To: {phone} | Text: {text}")

def notify_donor(donor, patient, urgency):
    subject = f"Urgent: {patient['blood_group']} Blood Needed"
    body = f"Hello {donor['full_name']},\n\nA patient in your circle needs {patient['blood_group']} blood. Please log in to your dashboard to respond and donate within 24 hours.\n\nThank you,\nLifeLink AI"
    send_email_notification(donor['email'], subject, body)

def notify_general_pool(donor, patient):
    subject = f"Emergency: {patient['blood_group']} Blood Needed"
    body = f"Hello {donor['full_name']},\n\nWe urgently need {patient['blood_group']} blood for a patient. If you can help, please log in to your dashboard and accept. \n\nIMPORTANT: If you do not receive a call within 1 hour of accepting, it means the blood has already been supplied by someone else. Thank you for your support!"
    send_email_notification(donor['email'], subject, body)

def notify_volunteers(volunteer, patient, request_urgency):
    subject = f"Escalation Alert: Blood Request in {patient['city']}"
    body = f"Hello {volunteer['full_name']},\n\nA blood request for {patient['blood_group']} in your city ({patient['city']}) has been escalated. Status: {request_urgency}. Please coordinate if possible."
    send_email_notification(volunteer['email'], subject, body)
