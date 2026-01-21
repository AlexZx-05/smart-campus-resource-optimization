from flask import Flask, jsonify, request
from extensions import db
from datetime import datetime, timedelta


# -----------------------------
# App Factory
# -----------------------------
def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # -----------------------------
    # Create Tables
    # -----------------------------
    with app.app_context():
        from models import (
            Student,
            Faculty,
            Course,
            Room,
            TimeSlot,
            Timetable,
            FacultyAvailability
        )
        db.create_all()

    # -----------------------------
    # BASIC ROUTES
    # -----------------------------
    @app.route("/")
    def home():
        return "Smart Campus Resource Optimization System is running!"

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "OK",
            "message": "Backend is healthy"
        })

    # -----------------------------
    # MASTER DATA APIs
    # -----------------------------
    @app.route("/api/faculty")
    def get_faculty():
        from models import Faculty
        return jsonify([
            {
                "id": f.id,
                "name": f.name,
                "department": f.department,
                "max_hours_per_week": f.max_hours_per_week
            } for f in Faculty.query.all()
        ])

    @app.route("/api/rooms")
    def get_rooms():
        from models import Room
        return jsonify([
            {
                "id": r.id,
                "room_name": r.room_name,
                "capacity": r.capacity,
                "room_type": r.room_type
            } for r in Room.query.all()
        ])

    @app.route("/api/courses")
    def get_courses():
        from models import Course
        return jsonify([
            {
                "id": c.id,
                "course_name": c.course_name,
                "department": c.department,
                "weekly_hours": c.weekly_hours,
                "faculty_id": c.faculty_id
            } for c in Course.query.all()
        ])

    @app.route("/api/timeslots")
    def get_timeslots():
        from models import TimeSlot
        return jsonify([
            {
                "id": t.id,
                "day": t.day,
                "start_time": t.start_time,
                "end_time": t.end_time
            } for t in TimeSlot.query.all()
        ])

    # -----------------------------
    # TIMETABLE API
    # -----------------------------
    @app.route("/api/timetable")
    def get_timetable():
        from models import Timetable
        return jsonify([
            {
                "course": e.course.course_name,
                "faculty": e.faculty.name,
                "room": e.room.room_name,
                "day": e.timeslot.day,
                "time": f"{e.timeslot.start_time}-{e.timeslot.end_time}"
            } for e in Timetable.query.all()
        ])

    # -----------------------------
    # 🔥 VISUAL TIMELINE (FREE + OCCUPIED)
    # -----------------------------
    @app.route("/api/timeline")
    def get_timeline():
        from models import Timetable, Room, TimeSlot

        timeline = {}
        rooms = Room.query.all()
        slots = TimeSlot.query.all()
        entries = Timetable.query.all()

        occupied = {
            (e.room_id, e.timeslot_id): {
                "course": e.course.course_name,
                "faculty": e.faculty.name
            } for e in entries
        }

        for slot in slots:
            day = slot.day
            timeline.setdefault(day, {})

            for room in rooms:
                timeline[day].setdefault(room.room_name, [])
                key = (room.id, slot.id)
                time_range = f"{slot.start_time}-{slot.end_time}"

                if key in occupied:
                    timeline[day][room.room_name].append({
                        "time": time_range,
                        "status": "OCCUPIED",
                        "course": occupied[key]["course"],
                        "faculty": occupied[key]["faculty"]
                    })
                else:
                    timeline[day][room.room_name].append({
                        "time": time_range,
                        "status": "FREE"
                    })

        return jsonify(timeline)

    # -----------------------------
    # METRICS
    # -----------------------------
    @app.route("/api/metrics")
    def get_metrics():
        from models import Course, Room, TimeSlot, Timetable

        total_courses = Course.query.count()
        scheduled = Timetable.query.count()
        rooms = Room.query.count()
        slots = TimeSlot.query.count()

        utilization = (
            (scheduled / (rooms * slots)) * 100
            if rooms and slots else 0
        )

        return jsonify({
            "total_courses": total_courses,
            "scheduled_classes": scheduled,
            "room_utilization_percent": round(utilization, 2),
            "room_conflicts": 0,
            "faculty_conflicts": 0
        })

    # -----------------------------
    # FACULTY ABSENCE LIST
    # -----------------------------
    @app.route("/api/faculty/unavailable")
    def get_unavailable_faculty():
        from models import FacultyAvailability, Faculty

        records = FacultyAvailability.query.filter_by(available=False).all()
        result = []

        for r in records:
            faculty = db.session.get(Faculty, r.faculty_id)
            result.append({
                "faculty": faculty.name,
                "date": r.date.isoformat(),
                "status": "Absent"
            })

        return jsonify(result)

    # -----------------------------
    # ⭐ BEST FREE SLOT SUGGESTION
    # -----------------------------
    @app.route("/api/suggest-slot/<int:faculty_id>")
    def suggest_slot(faculty_id):
        from services.slot_suggester import suggest_best_free_slot
        return jsonify(suggest_best_free_slot(faculty_id))

    # -----------------------------
    # MARK ABSENCE + AUTO REOPTIMIZE
    # -----------------------------
    @app.route("/api/faculty/<int:faculty_id>/unavailable-range", methods=["POST"])
    def mark_faculty_unavailable_range(faculty_id):
        from models import FacultyAvailability
        from optimizer import generate_timetable

        data = request.json
        start = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        current = start
        created = 0

        while current <= end:
            exists = FacultyAvailability.query.filter_by(
                faculty_id=faculty_id,
                date=current
            ).first()

            if not exists:
                db.session.add(FacultyAvailability(
                    faculty_id=faculty_id,
                    date=current,
                    available=False
                ))
                created += 1

            current += timedelta(days=1)

        db.session.commit()
        generate_timetable()

        return jsonify({
            "message": "Faculty absence recorded & timetable re-optimized",
            "days_blocked": created
        })

    # -----------------------------
    # RUN OPTIMIZER
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
# RUN SERVER
# -----------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
