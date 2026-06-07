use lifelink_ai;
CREATE TABLE users (

    user_id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE NOT NULL,

    phone VARCHAR(15) UNIQUE NOT NULL,

    password_hash VARCHAR(255) NOT NULL,

    dob DATE NOT NULL,

    city VARCHAR(100) NOT NULL,

    role ENUM(
        'admin',
        'volunteer',
        'donor',
        'patient'
    ) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE donors (

    donor_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    blood_group VARCHAR(5) NOT NULL,

    last_donation_date DATE,

    next_eligible_date DATE,

    donations_till_date INT DEFAULT 0,

    total_calls INT DEFAULT 0,

    calls_to_donations_ratio FLOAT DEFAULT 0,

    participation_score FLOAT DEFAULT 50.0,

    donor_status ENUM(
        'eligible',
        'not_eligible'
    ) DEFAULT 'eligible',

    active_status BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE
);

CREATE TABLE patients (

    patient_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    blood_group VARCHAR(5) NOT NULL,

    frequency_in_days INT NOT NULL,

    units_required INT DEFAULT 1,

    last_transfusion_date DATE,

    expected_next_transfusion_date DATE,

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE
);

CREATE TABLE donor_circles (

    circle_id INT AUTO_INCREMENT PRIMARY KEY,

    patient_id INT NOT NULL,

    donor_id INT NOT NULL,

    ranking_position INT NOT NULL,

    active BOOLEAN DEFAULT TRUE,

    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
    REFERENCES patients(patient_id)
    ON DELETE CASCADE,

    FOREIGN KEY (donor_id)
    REFERENCES donors(donor_id)
    ON DELETE CASCADE,

    UNIQUE(patient_id, donor_id),
    UNIQUE(donor_id)
);

CREATE TABLE blood_requests (

    request_id INT AUTO_INCREMENT PRIMARY KEY,

    patient_id INT NOT NULL,

    blood_group VARCHAR(5) NOT NULL,

    units_required INT DEFAULT 1,

    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    urgency ENUM(
        'normal',
        'urgent',
        'critical'
    ) DEFAULT 'normal',

    status ENUM(
        'pending',
        'matched',
        'completed',
        'escalated'
    ) DEFAULT 'pending',

    FOREIGN KEY (patient_id)
    REFERENCES patients(patient_id)
    ON DELETE CASCADE
);

CREATE TABLE donor_responses (

    response_id INT AUTO_INCREMENT PRIMARY KEY,

    donor_id INT NOT NULL,

    request_id INT NOT NULL,

    response ENUM(
        'accepted',
        'declined',
        'pending'
    ) DEFAULT 'pending',

    response_source ENUM(
        'dashboard',
        'email',
        'sms'
    ) DEFAULT 'dashboard',

    response_time DATETIME,

    FOREIGN KEY (donor_id)
    REFERENCES donors(donor_id)
    ON DELETE CASCADE,

    FOREIGN KEY (request_id)
    REFERENCES blood_requests(request_id)
    ON DELETE CASCADE
);

CREATE TABLE donations (

    donation_id INT AUTO_INCREMENT PRIMARY KEY,

    donor_id INT NOT NULL,

    patient_id INT NOT NULL,

    request_id INT NOT NULL,

    donation_date DATE,

    status ENUM(
        'completed',
        'cancelled'
    ) DEFAULT 'completed',

    FOREIGN KEY (donor_id)
    REFERENCES donors(donor_id)
    ON DELETE CASCADE,

    FOREIGN KEY (patient_id)
    REFERENCES patients(patient_id)
    ON DELETE CASCADE,

    FOREIGN KEY (request_id)
    REFERENCES blood_requests(request_id)
    ON DELETE CASCADE
);

CREATE TABLE notifications (

    notification_id INT AUTO_INCREMENT PRIMARY KEY,

    donor_id INT NOT NULL,

    request_id INT NOT NULL,

    message TEXT NOT NULL,

    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    is_read BOOLEAN DEFAULT FALSE,

    status ENUM(
        'sent',
        'delivered',
        'failed'
    ) DEFAULT 'sent',

    FOREIGN KEY (donor_id)
    REFERENCES donors(donor_id)
    ON DELETE CASCADE,

    FOREIGN KEY (request_id)
    REFERENCES blood_requests(request_id)
    ON DELETE CASCADE
);

CREATE TABLE ai_recommendations (

    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,

    patient_id INT NOT NULL,

    donor_id INT NOT NULL,

    recommendation_type ENUM(
        'replace_donor',
        'add_donor',
        'remove_donor'
    ) NOT NULL,

    reason TEXT,

    status ENUM(
        'pending',
        'approved',
        'rejected'
    ) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
    REFERENCES patients(patient_id)
    ON DELETE CASCADE,

    FOREIGN KEY (donor_id)
    REFERENCES donors(donor_id)
    ON DELETE CASCADE
);