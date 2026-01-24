from flask import Blueprint, jsonify, request
from extensions import db
from models import Timetable, TimeSlot, Room

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/api/book-slot", methods=["POST"])
def book_slot():
    data = request.json
    start, end = data["time"].split("-")

    slot = TimeSlot.query.filter_by(
        day=data["day"], start_time=start, end_time=end
    ).first()

    room = Room.query.filter_by(room_name=data["room"]).first()

    if Timetable.query.filter_by(room_id=room.id, timeslot_id=slot.id).first():
        return jsonify({"error": "Slot already booked"}), 409

    entry = Timetable(
        course_id=data["course_id"],
        faculty_id=data["faculty_id"],
        room_id=room.id,
        timeslot_id=slot.id
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Class booked successfully"})
