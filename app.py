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
            FacultyAvailability,
            FacultyPreference
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
        return jsonify({"status": "OK", "message": "Backend is healthy"})

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
    # VISUAL TIMELINE
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

                if key in occupied:
                    timeline[day][room.room_name].append({
                        "time": f"{slot.start_time}-{slot.end_time}",
                        "status": "OCCUPIED",
                        "course": occupied[key]["course"],
                        "faculty": occupied[key]["faculty"]
                    })
                else:
                    timeline[day][room.room_name].append({
                        "time": f"{slot.start_time}-{slot.end_time}",
                        "status": "FREE"
                    })

        return jsonify(timeline)

    # -----------------------------
    # BEST FREE SLOT SUGGESTION
    # -----------------------------
    @app.route("/api/suggest-slot/<int:faculty_id>")
    def suggest_slot(faculty_id):
        from services.slot_suggester import suggest_best_free_slot
        return jsonify(suggest_best_free_slot(faculty_id))

    # -----------------------------
    # FACULTY PREFERENCE API
    # -----------------------------
    @app.route("/api/faculty/<int:faculty_id>/preference", methods=["POST"])
    def set_faculty_preference(faculty_id):
        from models import FacultyPreference, Faculty

        faculty = db.session.get(Faculty, faculty_id)
        if not faculty:
            return jsonify({"error": "Faculty not found"}), 404

        data = request.json

        pref = FacultyPreference.query.filter_by(
            faculty_id=faculty_id
        ).first()

        if not pref:
            pref = FacultyPreference(faculty_id=faculty_id)

        pref.blocked_days = ",".join(data.get("blocked_days", []))
        pref.preferred_start_time = data.get("preferred_start_time")
        pref.preferred_end_time = data.get("preferred_end_time")

        db.session.add(pref)
        db.session.commit()

        return jsonify({
            "message": "Faculty preference saved successfully",
            "faculty": faculty.name
        })

    # -----------------------------
    # ❓ CONFLICT EXPLANATION API
    # -----------------------------
    @app.route("/api/why-not")
    def explain_why_not():
        from services.conflict_explainer import explain_conflict

        faculty_id = request.args.get("faculty_id", type=int)
        day = request.args.get("day")
        time_range = request.args.get("time")
        room = request.args.get("room")

        if not all([faculty_id, day, time_range, room]):
            return jsonify({"error": "Missing query parameters"}), 400

        reasons = explain_conflict(
            faculty_id=faculty_id,
            day=day,
            time_range=time_range,
            room_name=room
        )

        return jsonify({
            "faculty_id": faculty_id,
            "day": day,
            "time": time_range,
            "room": room,
            "reasons": reasons
        })

    # -----------------------------
    # ⭐ AUTO BOOK SLOT API
    # -----------------------------
    @app.route("/api/book-slot", methods=["POST"])
    def book_slot():
        from models import Timetable, TimeSlot, Room

        data = request.json

        faculty_id = data.get("faculty_id")
        course_id = data.get("course_id")
        day = data.get("day")
        time_range = data.get("time")
        room_name = data.get("room")

        if not all([faculty_id, course_id, day, time_range, room_name]):
            return jsonify({"error": "Missing required fields"}), 400

        start_time, end_time = time_range.split("-")
        slot = TimeSlot.query.filter_by(
            day=day,
            start_time=start_time,
            end_time=end_time
        ).first()

        if not slot:
            return jsonify({"error": "Invalid day or time slot"}), 400

        room = Room.query.filter_by(room_name=room_name).first()
        if not room:
            return jsonify({"error": "Room not found"}), 404

        if Timetable.query.filter_by(room_id=room.id, timeslot_id=slot.id).first():
            return jsonify({"error": "Slot already booked for this room"}), 409

        if Timetable.query.filter_by(faculty_id=faculty_id, timeslot_id=slot.id).first():
            return jsonify({"error": "Faculty already has a class at this time"}), 409

        entry = Timetable(
            course_id=course_id,
            faculty_id=faculty_id,
            room_id=room.id,
            timeslot_id=slot.id
        )

        db.session.add(entry)
        db.session.commit()

        return jsonify({
            "message": "Class booked successfully",
            "day": day,
            "time": time_range,
            "room": room_name
        })

    # -----------------------------
    # RUN OPTIMIZER
    # -----------------------------
    @app.route("/api/optimize")
    def run_optimizer():
        from optimizer import generate_timetable
        generate_timetable()
        return jsonify({"message": "Timetable optimized successfully"})

    return app


# -----------------------------
# RUN SERVER
# -----------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
