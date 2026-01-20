from extensions import db

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
