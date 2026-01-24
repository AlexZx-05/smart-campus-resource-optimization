from flask import Blueprint, jsonify, request
from extensions import db
from models import Faculty, FacultyPreference

preference_bp = Blueprint("preference", __name__)

@preference_bp.route("/api/faculty/<int:faculty_id>/preference", methods=["POST"])
def set_preference(faculty_id):
    faculty = db.session.get(Faculty, faculty_id)
    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    data = request.json
    pref = FacultyPreference.query.filter_by(faculty_id=faculty_id).first() or FacultyPreference(faculty_id=faculty_id)

    pref.blocked_days = ",".join(data.get("blocked_days", []))
    pref.preferred_start_time = data.get("preferred_start_time")
    pref.preferred_end_time = data.get("preferred_end_time")

    db.session.add(pref)
    db.session.commit()

    return jsonify({"message": "Preference saved"})

@preference_bp.route("/api/faculty/<int:faculty_id>/preference", methods=["GET"])
def get_preference(faculty_id):
    pref = FacultyPreference.query.filter_by(faculty_id=faculty_id).first()
    if not pref:
        return jsonify({"message": "No preferences set"})

    return jsonify({
        "blocked_days": pref.blocked_days.split(",") if pref.blocked_days else [],
        "preferred_start_time": pref.preferred_start_time,
        "preferred_end_time": pref.preferred_end_time
    })
