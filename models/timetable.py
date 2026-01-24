from extensions import db

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"))
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    timeslot_id = db.Column(db.Integer, db.ForeignKey("time_slot.id"))

    batch = db.Column(db.String(50))  # 👈 NEW

    course = db.relationship("Course")
    faculty = db.relationship("Faculty")
    room = db.relationship("Room")
    timeslot = db.relationship("TimeSlot")
