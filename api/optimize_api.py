from flask import Blueprint, jsonify
from optimizer import generate_timetable

optimize_bp = Blueprint("optimize", __name__)

@optimize_bp.route("/api/optimize", methods=["GET"])
def run_optimizer():
    generate_timetable()

    return jsonify({
        "status": "success",
        "message": "Timetable optimized successfully"
    })
