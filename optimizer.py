from extensions import db
from models import (
    Course,
    Room,
    TimeSlot,
    Timetable,
    FacultyPreference,
    FacultyAvailability
)
from flask import current_app


DAY_SCORE = {
    "Monday": 2,
    "Tuesday": 1,
    "Wednesday": 1,
    "Thursday": 0,
    "Friday": -100  # HARD BLOCK
}

TIME_SCORE = {
    "09:00": -2,
    "10:00": 1,
    "11:00": 3
}


def generate_timetable():
    with current_app.app_context():

        print("🔄 Starting preference-aware optimization...")

        # 1️⃣ Clear old timetable
        Timetable.query.delete()
        db.session.commit()

        courses = Course.query.all()
        rooms = Room.query.all()
        slots = TimeSlot.query.all()

        # 2️⃣ Group slots by day
        slots_by_day = {}
        for slot in slots:
            slots_by_day.setdefault(slot.day, []).append(slot)

        for day in slots_by_day:
            slots_by_day[day].sort(key=lambda s: s.start_time)

        used_room_slot = set()
        used_faculty_slot = set()

        total_assigned = 0
        days = list(slots_by_day.keys())

        for course in courses:
            required = course.weekly_hours
            assigned = 0
            faculty_id = course.faculty_id

            pref = FacultyPreference.query.filter_by(
                faculty_id=faculty_id
            ).first()

            blocked_days = pref.blocked_days.split(",") if pref and pref.blocked_days else []
            pref_start = pref.preferred_start_time if pref else None
            pref_end = pref.preferred_end_time if pref else None

            print(f"\n📘 Scheduling {course.course_name}")

            ranked_options = []

            for day in days:

                if day in blocked_days:
                    continue

                for slot in slots_by_day[day]:

                    if (faculty_id, slot.id) in used_faculty_slot:
                        continue

                    for room in rooms:

                        if (room.id, slot.id) in used_room_slot:
                            continue

                        score = DAY_SCORE.get(day, 0)
                        score += TIME_SCORE.get(slot.start_time, 0)

                        if pref_start and pref_end:
                            if pref_start <= slot.start_time <= pref_end:
                                score += 3

                        ranked_options.append((score, day, slot, room))

            ranked_options.sort(reverse=True, key=lambda x: x[0])

            for score, day, slot, room in ranked_options:
                if assigned >= required:
                    break

                entry = Timetable(
                    course_id=course.id,
                    faculty_id=faculty_id,
                    room_id=room.id,
                    timeslot_id=slot.id,
                    batch=course.department 
                  
                )

                db.session.add(entry)
                db.session.commit()

                used_room_slot.add((room.id, slot.id))
                used_faculty_slot.add((faculty_id, slot.id))

                assigned += 1
                total_assigned += 1

                print(
                    f"✅ {course.course_name} → {day} "
                    f"{slot.start_time}-{slot.end_time} | "
                    f"{room.room_name} | score={score}"
                )

            if assigned < required:
                print(f"⚠️ Only {assigned}/{required} assigned")

        print(f"\n🎉 Optimization complete: {total_assigned} classes")
