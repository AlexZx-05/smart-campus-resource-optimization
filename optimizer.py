from app import create_app
from extensions import db
from models import Course, Room, TimeSlot, Timetable

app = create_app()


def generate_timetable():
    with app.app_context():

        print("🔄 Starting timetable optimization...")

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

        # 3️⃣ Sort slots by start time (important)
        for day in slots_by_day:
            slots_by_day[day].sort(key=lambda s: s.start_time)

        used_room_slot = set()
        used_faculty_slot = set()

        total_assigned = 0

        # 🔁 SLOT ROTATION INDEX (THIS IS THE KEY FIX)
        slot_rotation_index = 0

        days = list(slots_by_day.keys())

        for course in courses:
            required_hours = course.weekly_hours
            assigned_hours = 0

            print(f"\n📘 Scheduling {course.course_name} ({required_hours} hrs/week)")

            day_index = 0

            # 4️⃣ Assign ONE class per day (spread across week)
            while assigned_hours < required_hours and day_index < len(days):
                day = days[day_index]
                day_slots = slots_by_day[day]

                # 🎯 Pick slot using rotation (instead of always first slot)
                slot = day_slots[slot_rotation_index % len(day_slots)]

                for room in rooms:

                    # ❌ Room already used at this time
                    if (room.id, slot.id) in used_room_slot:
                        continue

                    # ❌ Faculty already teaching at this time
                    if (course.faculty_id, slot.id) in used_faculty_slot:
                        continue

                    # ✅ Assign class
                    entry = Timetable(
                        course_id=course.id,
                        faculty_id=course.faculty_id,
                        room_id=room.id,
                        timeslot_id=slot.id
                    )

                    db.session.add(entry)
                    db.session.commit()

                    used_room_slot.add((room.id, slot.id))
                    used_faculty_slot.add((course.faculty_id, slot.id))

                    assigned_hours += 1
                    total_assigned += 1

                    print(
                        f"✅ {course.course_name} → {room.room_name} "
                        f"@ {day} {slot.start_time}"
                    )

                    # 🔁 Move to next time slot for next assignment
                    slot_rotation_index += 1
                    break

                day_index += 1

            if assigned_hours < required_hours:
                print(f"⚠️ Only {assigned_hours}/{required_hours} hours assigned")

        print(f"\n🎉 Optimization complete. Total classes scheduled: {total_assigned}")


if __name__ == "__main__":
    generate_timetable()
