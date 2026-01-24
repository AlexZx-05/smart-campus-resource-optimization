from flask import Blueprint, jsonify
from services.slot_suggester import suggest_best_free_slot

suggestion_bp = Blueprint("suggestion", __name__)

@suggestion_bp.route("/api/suggest-slot/<int:faculty_id>")
def suggest_slot(faculty_id):
    return jsonify(suggest_best_free_slot(faculty_id))
