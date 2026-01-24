from flask import Blueprint, jsonify, request
from extensions import db
from models import Timetable, TimeSlot, Room, FacultyPreference

reschedule_bp = Blueprint("reschedule", __name__)

@reschedule_bp.route("/api/cancel-class", methods=["POST"])
def cancel_class():
    data = request.json
    start, end = data["time"].split("-")

    slot = TimeSlot.query.filter_by(
        day=data["day"], start_time=start, end_time=end
    ).first()

    room = Room.query.filter_by(room_name=data["room"]).first()

    entry = Timetable.query.filter_by(
        course_id=data["course_id"],
        room_id=room.id,
        timeslot_id=slot.id
    ).first()

    if not entry:
        return jsonify({"error": "Class not found"}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Class cancelled"})
