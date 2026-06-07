from flask import Flask

from flask_cors import CORS

from routes.auth_routes import auth_bp
from routes.donor_routes import donor_bp
from routes.patient_routes import patient_bp
from routes.volunteer_routes import volunteer_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(donor_bp, url_prefix="/api/donor")
app.register_blueprint(patient_bp, url_prefix="/api/patient")
app.register_blueprint(volunteer_bp, url_prefix="/api/volunteer")
app.register_blueprint(admin_bp, url_prefix="/api/admin")


@app.route("/")
def home():

    return {
        "message": "LifeLink AI Backend Running"
    }


if __name__ == "__main__":

    app.run(debug=True)