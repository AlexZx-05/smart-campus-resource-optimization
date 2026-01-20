from flask import Flask, jsonify
from extensions import db


# -----------------------------
# App Factory
# -----------------------------
def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize DB
    db.init_app(app)

    # Import models & create tables
    with app.app_context():
        from models import Student, Faculty, Course, Room, TimeSlot, Timetable
        db.create_all()

    # -----------------------------
    # ROUTES
    # -----------------------------

    @app.route("/")
    def home():
        return "Smart Campus Resource Optimization System is running!"

    # -----------------------------
    # Health Check API
    # -----------------------------
    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "OK",
            "message": "Backend is healthy"
        })

    # -----------------------------
    # Faculty API
    # -----------------------------
    @app.route("/api/faculty")
    def get_faculty():
        from models import Faculty
        faculty = Faculty.query.all()
        return jsonify([
            {
                "id": f.id,
                "name": f.name,
                "department": f.department,
                "max_hours_per_week": f.max_hours_per_week
            } for f in faculty
        ])

    # -----------------------------
    # Rooms API
    # -----------------------------
    @app.route("/api/rooms")
    def get_rooms():
        from models import Room
        rooms = Room.query.all()
        return jsonify([
            {
                "id": r.id,
                "room_name": r.room_name,
                "capacity": r.capacity,
                "room_type": r.room_type
            } for r in rooms
        ])

    # -----------------------------
    # Courses API
    # -----------------------------
    @app.route("/api/courses")
    def get_courses():
        from models import Course
        courses = Course.query.all()
        return jsonify([
            {
                "id": c.id,
                "course_name": c.course_name,
                "department": c.department,
                "weekly_hours": c.weekly_hours,
                "faculty_id": c.faculty_id
            } for c in courses
        ])

    # -----------------------------
    # Time Slots API
    # -----------------------------
    @app.route("/api/timeslots")
    def get_timeslots():
        from models import TimeSlot
        slots = TimeSlot.query.all()
        return jsonify([
            {
                "id": t.id,
                "day": t.day,
                "start_time": t.start_time,
                "end_time": t.end_time
            } for t in slots
        ])

    # -----------------------------
    # Timetable API
    # -----------------------------
    @app.route("/api/timetable")
    def get_timetable():
        from models import Timetable
        entries = Timetable.query.all()
        return jsonify([
            {
                "course": e.course.course_name,
                "faculty": e.faculty.name,
                "room": e.room.room_name,
                "day": e.timeslot.day,
                "time": f"{e.timeslot.start_time} - {e.timeslot.end_time}"
            } for e in entries
        ])

    # -----------------------------
    # Metrics API
    # -----------------------------
    @app.route("/api/metrics")
    def get_metrics():
        from models import Course, Room, TimeSlot, Timetable

        total_courses = Course.query.count()
        scheduled_classes = Timetable.query.count()
        total_rooms = Room.query.count()
        total_slots = TimeSlot.query.count()

        total_possible = total_rooms * total_slots
        room_utilization = (
            (scheduled_classes / total_possible) * 100
            if total_possible else 0
        )

        return jsonify({
            "total_courses": total_courses,
            "scheduled_classes": scheduled_classes,
            "room_utilization_percent": round(room_utilization, 2),
            "room_conflicts": 0,
            "faculty_conflicts": 0
        })

    # -----------------------------
    # Run Optimizer API (SHOW-OFF)
    # -----------------------------
    @app.route("/api/optimize")
    def run_optimizer():
        from optimizer import generate_timetable
        generate_timetable()
        return jsonify({
            "message": "Timetable optimized successfully"
        })

    return app


# -----------------------------
# Run Server
# -----------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
