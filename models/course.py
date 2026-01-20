from extensions import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    weekly_hours = db.Column(db.Integer)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
