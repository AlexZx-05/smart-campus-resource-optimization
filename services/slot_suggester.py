from models import Faculty, Room, TimeSlot, Timetable, FacultyPreference
from extensions import db
from datetime import datetime


# Base scoring (can be tuned later)
DAY_SCORE = {
    "Monday": 2,
    "Tuesday": 1,
    "Wednesday": 1,
    "Thursday": 0,
    "Friday": -5   # heavy penalty (almost blocked)
}

TIME_SCORE = {
    "09:00": -2,   # avoid early morning
    "10:00": 2,
    "11:00": 3,
    "12:00": 3
}


def time_to_minutes(t):
    """Convert HH:MM to minutes"""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def suggest_best_free_slot(faculty_id):
    faculty = db.session.get(Faculty, faculty_id)
    if not faculty:
        return {"error": "Faculty not found"}

    # 🔹 Fetch faculty preference (if exists)
    preference = FacultyPreference.query.filter_by(
        faculty_id=faculty_id
    ).first()

    blocked_days = []
    preferred_start = None
    preferred_end = None

    if preference:
        if preference.blocked_days:
            blocked_days = preference.blocked_days.split(",")

        preferred_start = preference.preferred_start_time
        preferred_end = preference.preferred_end_time

    rooms = Room.query.all()
    slots = TimeSlot.query.all()
    timetable = Timetable.query.all()

    occupied_room_slot = set()
    occupied_faculty_slot = set()

    for t in timetable:
        occupied_room_slot.add((t.room_id, t.timeslot_id))
        occupied_faculty_slot.add((t.faculty_id, t.timeslot_id))

    ranked_slots = []

    for slot in slots:

        # ❌ Skip blocked days
        if slot.day in blocked_days:
            continue

        for room in rooms:

            # ❌ Room busy
            if (room.id, slot.id) in occupied_room_slot:
                continue

            # ❌ Faculty busy
            if (faculty_id, slot.id) in occupied_faculty_slot:
                continue

            score = 0

            # 🧮 Day preference score
            score += DAY_SCORE.get(slot.day, 0)

            # 🧮 Time preference score
            score += TIME_SCORE.get(slot.start_time, 0)

            # ⭐ Preferred time window bonus
            if preferred_start and preferred_end:
                slot_start = time_to_minutes(slot.start_time)
                pref_start = time_to_minutes(preferred_start)
                pref_end = time_to_minutes(preferred_end)

                if pref_start <= slot_start < pref_end:
                    score += 3   # bonus

            ranked_slots.append({
                "day": slot.day,
                "time": f"{slot.start_time}-{slot.end_time}",
                "room": room.room_name,
                "score": score
            })

    if not ranked_slots:
        return {
            "faculty": faculty.name,
            "message": "No slots available respecting preferences"
        }

    # 🔥 Sort by score (high → low)
    ranked_slots.sort(key=lambda x: x["score"], reverse=True)

    # 🔹 Keep unique times only (avoid same time repeated)
    unique_time = {}
    for s in ranked_slots:
        if s["time"] not in unique_time:
            unique_time[s["time"]] = s

    top = list(unique_time.values())[:3]

    for i, s in enumerate(top, start=1):
        s["rank"] = i

    return {
        "faculty": faculty.name,
        "reason": "Top 3 ranked UNIQUE time slots (preferences applied)",
        "suggestions": top
    }
