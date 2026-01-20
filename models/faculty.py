
from extensions import db


class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    max_hours_per_week = db.Column(db.Integer)
