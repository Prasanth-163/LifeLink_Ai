# LifeLink AI - Blood Care Coordination Network

LifeLink AI is an autonomous, AI-powered blood support network designed to minimize manual effort for Blood Warriors and improve support for Thalassemia patients.

## 🚀 Core Innovation: Dynamic Donor Circles
Instead of manual outreach, LifeLink AI automatically generates a dedicated **Donor Circle** of 8 compatible donors for each patient. These donors are intelligently ranked and matched using machine learning.

## 🧠 AI Features
- **Donor Participation Prediction:** A Random Forest Classifier that predicts the likelihood of a donor contributing based on historical engagement (98% accuracy).
- **Smart Donor Ranking:** Prioritizes donors based on blood compatibility, eligibility, and participation scores.
- **Circle Health Optimizer:** Automatically identifies inactive or low-performing donor circles and recommends replacements.
- **Autonomous Scheduler:** Predicts upcoming transfusion needs and creates blood requests automatically.

## 🛠️ Tech Stack
- **Frontend:** React, Tailwind CSS, Lucide Icons, Axios.
- **Backend:** Python, Flask.
- **Database:** MySQL.
- **AI/ML:** Scikit-Learn, Pandas, Joblib.

## 📂 Project Structure
- `backend/ai/`: Machine learning models and coordination logic.
- `backend/routes/`: API endpoints for different user roles.
- `backend/services/`: Core business logic (Circle management, etc.).
- `backend/scripts/`: Automation tasks.
- `frontend/src/pages/`: Role-specific dashboards and auth pages.

## 🏃 How to Run

### Backend
1. Navigate to `backend/`.
2. Ensure you have Python 3.12+ installed.
3. Install dependencies: `pip install -r ../requirement.txt`.
4. Run the app: `python app.py`.
5. Run automated tasks: `python scripts/automated_task.py`.

### Frontend
1. Navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Run dev server: `npm run dev`.

## 📈 Database Setup
Import the schema from `backend/database/schema.sql` into your MySQL instance. Update `backend/.env` with your credentials.

---
Built for Hackathon Excellence.
