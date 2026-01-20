from extensions import db

class Timetable(db.Model):
    __tablename__ = "timetable"

    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('time_slot.id'), nullable=False)

    # 🔥 Relationships (THIS FIXES YOUR ERROR)
    course = db.relationship("Course", backref="timetable_entries")
    faculty = db.relationship("Faculty", backref="timetable_entries")
    room = db.relationship("Room", backref="timetable_entries")
    timeslot = db.relationship("TimeSlot", backref="timetable_entries")
