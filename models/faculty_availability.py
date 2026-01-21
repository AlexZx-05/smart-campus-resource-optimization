from extensions import db

class FacultyAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    available = db.Column(db.Boolean, default=True)
