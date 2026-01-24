from flask import Blueprint, jsonify
from models import Timetable, Room, TimeSlot, Faculty

timetable_bp = Blueprint("timetable", __name__)

# =========================================================
# 📋 FULL TIMETABLE (ADMIN VIEW)
# =========================================================
@timetable_bp.route("/api/timetable")
def get_timetable():
    return jsonify([
        {
            "course": e.course.course_name,
            "faculty": e.faculty.name,
            "room": e.room.room_name,
            "day": e.timeslot.day,
            "time": f"{e.timeslot.start_time}-{e.timeslot.end_time}",
            "batch": e.batch
        }
        for e in Timetable.query.all()
    ])


# =========================================================
# 🏫 VISUAL TIMELINE (ROOM-WISE, FREE + OCCUPIED)
# =========================================================
@timetable_bp.route("/api/timeline")
def get_timeline():
    timeline = {}
    rooms = Room.query.all()
    slots = TimeSlot.query.all()
    entries = Timetable.query.all()

    occupied = {(e.room_id, e.timeslot_id): e for e in entries}

    for slot in slots:
        day = slot.day
        timeline.setdefault(day, {})

        for room in rooms:
            timeline[day].setdefault(room.room_name, [])
            key = (room.id, slot.id)

            if key in occupied:
                e = occupied[key]
                timeline[day][room.room_name].append({
                    "time": f"{slot.start_time}-{slot.end_time}",
                    "status": "OCCUPIED",
                    "course": e.course.course_name,
                    "faculty": e.faculty.name,
                    "batch": e.batch
                })
            else:
                timeline[day][room.room_name].append({
                    "time": f"{slot.start_time}-{slot.end_time}",
                    "status": "FREE"
                })

    return jsonify(timeline)


# =========================================================
# 🎓 STUDENT BATCH-WISE TIMETABLE
# =========================================================
@timetable_bp.route("/api/timetable/batch/<batch>")
def get_batch_timetable(batch):
    entries = Timetable.query.filter_by(batch=batch).all()

    if not entries:
        return jsonify({
            "batch": batch,
            "message": "No classes scheduled"
        })

    result = {}

    for e in entries:
        day = e.timeslot.day
        result.setdefault(day, []).append({
            "time": f"{e.timeslot.start_time}-{e.timeslot.end_time}",
            "course": e.course.course_name,
            "faculty": e.faculty.name,
            "room": e.room.room_name
        })

    return jsonify({
        "batch": batch,
        "timetable": result
    })


# =========================================================
# 👨‍🏫 FACULTY-WISE TIMETABLE
# =========================================================
@timetable_bp.route("/api/timetable/faculty/<int:faculty_id>")
def get_faculty_timetable(faculty_id):
    faculty = Faculty.query.get(faculty_id)

    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    entries = Timetable.query.filter_by(faculty_id=faculty_id).all()

    if not entries:
        return jsonify({
            "faculty": faculty.name,
            "message": "No classes scheduled"
        })

    result = {}

    for e in entries:
        day = e.timeslot.day
        result.setdefault(day, []).append({
            "time": f"{e.timeslot.start_time}-{e.timeslot.end_time}",
            "course": e.course.course_name,
            "batch": e.batch,
            "room": e.room.room_name
        })

    return jsonify({
        "faculty": faculty.name,
        "timetable": result
    })
