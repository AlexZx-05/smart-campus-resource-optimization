

from extensions import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    room_type = db.Column(db.String(20))
