from extensions import db


class FacultyPreference(db.Model):
    __tablename__ = "faculty_preferences"

    id = db.Column(db.Integer, primary_key=True)

    # One-to-one with Faculty
    faculty_id = db.Column(
        db.Integer,
        db.ForeignKey("faculty.id"),
        unique=True,
        nullable=False
    )

    # Preferences
    blocked_days = db.Column(db.String(100))          # e.g. "Friday,Monday"
    preferred_start_time = db.Column(db.String(10))  # e.g. "10:00"
    preferred_end_time = db.Column(db.String(10))    # e.g. "12:00"

    faculty = db.relationship("Faculty", backref="preference")
