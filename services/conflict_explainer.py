from models import (
    Timetable,
    TimeSlot,
    Room,
    FacultyAvailability,
    FacultyPreference
)
from extensions import db
from datetime import date


def explain_conflict(faculty_id, day, time_range, room_name):
    reasons = []

    # 1️⃣ Find the timeslot
    start_time, end_time = time_range.split("-")
    slot = TimeSlot.query.filter_by(
        day=day,
        start_time=start_time,
        end_time=end_time
    ).first()

    if not slot:
        reasons.append("Invalid day or time slot")
        return reasons

    # 2️⃣ Room conflict
    room = Room.query.filter_by(room_name=room_name).first()
    if room:
        room_conflict = Timetable.query.filter_by(
            room_id=room.id,
            timeslot_id=slot.id
        ).first()
        if room_conflict:
            reasons.append("Room already booked")

    # 3️⃣ Faculty time conflict
    faculty_conflict = Timetable.query.filter_by(
        faculty_id=faculty_id,
        timeslot_id=slot.id
    ).first()
    if faculty_conflict:
        reasons.append("Faculty already has a class at this time")

    # 4️⃣ Faculty preference conflict
    pref = FacultyPreference.query.filter_by(
        faculty_id=faculty_id
    ).first()

    if pref and pref.blocked_days:
        blocked_days = pref.blocked_days.split(",")
        if day in blocked_days:
            reasons.append("Day blocked by faculty preference")

    # 5️⃣ Faculty absence (date-based)
    today = date.today()
    absence = FacultyAvailability.query.filter_by(
        faculty_id=faculty_id,
        date=today,
        available=False
    ).first()

    if absence:
        reasons.append("Faculty marked absent")

    if not reasons:
        reasons.append("Slot is available")

    return reasons
