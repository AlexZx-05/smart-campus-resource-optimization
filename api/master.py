from flask import Blueprint, jsonify
from models import Faculty, Room, Course, TimeSlot

master_bp = Blueprint("master", __name__)

@master_bp.route("/api/faculty")
def get_faculty():
    return jsonify([{
        "id": f.id,
        "name": f.name,
        "department": f.department,
        "max_hours_per_week": f.max_hours_per_week
    } for f in Faculty.query.all()])

@master_bp.route("/api/rooms")
def get_rooms():
    return jsonify([{
        "id": r.id,
        "room_name": r.room_name,
        "capacity": r.capacity,
        "room_type": r.room_type
    } for r in Room.query.all()])

@master_bp.route("/api/courses")
def get_courses():
    return jsonify([{
        "id": c.id,
        "course_name": c.course_name,
        "department": c.department,
        "weekly_hours": c.weekly_hours,
        "faculty_id": c.faculty_id
    } for c in Course.query.all()])

@master_bp.route("/api/timeslots")
def get_timeslots():
    return jsonify([{
        "id": t.id,
        "day": t.day,
        "start_time": t.start_time,
        "end_time": t.end_time
    } for t in TimeSlot.query.all()])
