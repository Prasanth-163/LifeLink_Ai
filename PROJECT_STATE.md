# LifeLink AI - Project Documentation & Current State

## 1. Project Overview
**LifeLink AI** is an autonomous, AI-powered blood care coordination network specifically designed to support Thalassemia patients. The core innovation is the **Dynamic Donor Circle**—a dedicated group of 8 compatible donors assigned to each patient to minimize manual outreach effort.

## 2. Core Aim
To eliminate the manual stress of "Blood Warriors" and patients by automating the transfusion lifecycle:
*   Predicting transfusion dates.
*   Automating blood requests.
*   Managing serial donor notifications with a strict 24-hour response window.
*   Intelligently escalating to a general pool only when necessary.

## 3. Technical Architecture
### Backend (Python/Flask)
*   **Database**: MySQL (relational schema for users, donors, patients, circles, and requests).
*   **AI/ML**: 
    *   **Random Forest Classifier**: Trained on `Dataset.csv` (7000+ records) with 98% accuracy to predict donor participation scores.
    *   **Ranking Engine**: Ranks donors within circles based on AI scores and donation history.
    *   **Scheduler**: Predicts next transfusion dates and lead times.
*   **Orchestration**: `automated_task.py` acts as an autonomous agent running the 24-hour cyclic escalation logic.

### Frontend (React/Tailwind)
*   **Role-Based Dashboards**: Customized views for Donors, Patients, Volunteers, and Admins.
*   **Real-time Tracking**: Countdown timers for patients and impact stats for donors.

## 4. Key Workflows Implemented
### A. The Transfusion Cycle
1.  **Lead Time**: 5 days before a predicted transfusion, a request is raised.
2.  **Serial Notification**: Donor #1 in the circle is notified first.
3.  **The 24-Hour Rule**: If a volunteer does not close the request within 24 hours (confirming donation), the AI automatically notifies Donor #2. This is handled via a **Real-time Heartbeat** in the API.
4.  **Escalation**: If the circle (8 donors) is exhausted, it escalates to all compatible donors in the city (General Pool).

### B. Donor Participation
*   **One-Donor-One-Circle**: Donors are uniquely assigned to one patient to ensure dedicated care.
*   **Dataset Integration**: The system is seeded with 200+ donors from historical data to ensure immediate circle availability.
*   Upon accepting a general pool request, they are told: *"If you don't receive a call within 1 hr, someone else has donated."*

### C. Volunteer Oversight
*   **Profile Management**: Volunteers have full profile editing capabilities.
*   **Command Center**: Volunteers verify physical donations, which **automatically schedules the patient's next cycle** and updates donor stats.

## 5. Database Schema (Highlights)
*   `users`: Auth and profile data.
*   `donors`: Blood group, scores, and eligibility.
*   `patients`: Frequency and scheduled dates.
*   `donor_circles`: The AI-generated mapping of 8 donors per patient.
*   `blood_requests`: Tracking status (`pending`, `matched`, `completed`, `escalated`).
*   `notifications`: History of who was contacted and when (critical for the 24-hour timer).

## 6. How to Run & Verify
### Prerequisites
1.  MySQL Database running with `backend/database/schema.sql` imported.
2.  `.env` file in `backend/` with DB credentials.

### Steps
1.  **Install Dependencies**:
    ```bash
    pip install -r requirement.txt
    cd frontend && npm install
    ```
2.  **Train AI Model**:
    ```bash
    python backend/ai/donor_prediction.py
    ```
3.  **Start Backend**:
    ```bash
    python backend/app.py
    ```
4.  **Start Frontend**:
    ```bash
    npm run dev (inside frontend/)
    ```
5.  **Run Automation Agent** (Simulate 24h checks):
    ```bash
    python backend/scripts/automated_task.py
    ```

---
**Current Status**: Complete up to Automated Cyclic Escalation. All dashboards are functional and synced with AI modules.
