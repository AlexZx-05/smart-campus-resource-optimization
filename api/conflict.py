from flask import Blueprint, jsonify, request
from services.conflict_explainer import explain_conflict

conflict_bp = Blueprint("conflict", __name__)

@conflict_bp.route("/api/why-not")
def why_not():
    reasons = explain_conflict(
        faculty_id=request.args.get("faculty_id", type=int),
        day=request.args.get("day"),
        time_range=request.args.get("time"),
        room_name=request.args.get("room")
    )

    return jsonify({"reasons": reasons})
