from models import Timetable, Room, TimeSlot, Faculty
from extensions import db


def suggest_best_free_slot(faculty_id):
    """
    Returns the best free slot for a faculty:
    - Faculty must be free
    - Room must be free
    """

    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return {"message": "Faculty not found"}

    # 1️⃣ Get faculty's occupied slots
    faculty_entries = Timetable.query.filter_by(faculty_id=faculty_id).all()
    busy_slots = set(e.timeslot_id for e in faculty_entries)

    rooms = Room.query.all()
    slots = TimeSlot.query.all()

    # 2️⃣ Check each slot-room combination
    for slot in slots:
        # Skip if faculty already busy
        if slot.id in busy_slots:
            continue

        for room in rooms:
            # Check if room is free at this slot
            room_busy = Timetable.query.filter_by(
                room_id=room.id,
                timeslot_id=slot.id
            ).first()

            if room_busy:
                continue

            # ✅ BEST SLOT FOUND
            return {
                "faculty": faculty.name,
                "day": slot.day,
                "time": f"{slot.start_time}-{slot.end_time}",
                "room": room.room_name,
                "reason": "Faculty free + Room free"
            }

    return {
        "message": "No free slot available for this faculty"
    }
