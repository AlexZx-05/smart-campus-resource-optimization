from app import create_app
from extensions import db

from models import Student, Faculty, Course, Room, TimeSlot, Timetable

# Create app properly
app = create_app()

with app.app_context():

    # ---------------- CLEAR OLD DATA ----------------
    db.session.query(Timetable).delete()
    db.session.query(Student).delete()
    db.session.query(Course).delete()
    db.session.query(Faculty).delete()
    db.session.query(Room).delete()
    db.session.query(TimeSlot).delete()
    db.session.commit()

    # ---------------- FACULTY ----------------
    faculty_list = [
        Faculty(name="Dr. Sharma", department="CSE", max_hours_per_week=12),
        Faculty(name="Dr. Verma", department="CSE", max_hours_per_week=10),
        Faculty(name="Dr. Singh", department="ECE", max_hours_per_week=12),
        Faculty(name="Dr. Patel", department="ME", max_hours_per_week=10),
        Faculty(name="Dr. Rao", department="CSE", max_hours_per_week=14),
    ]
    db.session.add_all(faculty_list)
    db.session.commit()

    # ---------------- ROOMS ----------------
    rooms = [
        Room(room_name="CSE-101", capacity=60, room_type="classroom"),
        Room(room_name="CSE-102", capacity=60, room_type="classroom"),
        Room(room_name="CSE-LAB1", capacity=30, room_type="lab"),
        Room(room_name="ECE-201", capacity=50, room_type="classroom"),
        Room(room_name="ME-301", capacity=40, room_type="classroom"),
    ]
    db.session.add_all(rooms)
    db.session.commit()

    # ---------------- TIME SLOTS ----------------
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = []

    for day in days:
        time_slots.append(TimeSlot(day=day, start_time="09:00", end_time="10:00"))
        time_slots.append(TimeSlot(day=day, start_time="10:00", end_time="11:00"))
        time_slots.append(TimeSlot(day=day, start_time="11:00", end_time="12:00"))

    db.session.add_all(time_slots)
    db.session.commit()

    # ---------------- COURSES ----------------
    courses = [
        Course(course_name="DBMS", department="CSE", weekly_hours=4, faculty_id=faculty_list[0].id),
        Course(course_name="Operating Systems", department="CSE", weekly_hours=4, faculty_id=faculty_list[1].id),
        Course(course_name="Computer Networks", department="CSE", weekly_hours=3, faculty_id=faculty_list[4].id),
        Course(course_name="Digital Electronics", department="ECE", weekly_hours=3, faculty_id=faculty_list[2].id),
        Course(course_name="Thermodynamics", department="ME", weekly_hours=3, faculty_id=faculty_list[3].id),
    ]
    db.session.add_all(courses)
    db.session.commit()

    # ---------------- STUDENTS ----------------
    students = []
    for i in range(1, 101):
        students.append(Student(
            name=f"Student_{i}",
            department="CSE",
            year=3
        ))

    db.session.add_all(students)
    db.session.commit()

    print("✅ Sample campus data inserted successfully!")
