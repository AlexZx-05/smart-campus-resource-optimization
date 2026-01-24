from flask import Flask
from extensions import db

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from models import (
            Student, Faculty, Course, Room,
            TimeSlot, Timetable,
            FacultyAvailability, FacultyPreference
        )
        db.create_all()

    @app.route("/")
    def home():
        return "Smart Campus Resource Optimization System is running!"

    from api import register_blueprints
    register_blueprints(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
