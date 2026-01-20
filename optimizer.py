from app import create_app
from extensions import db
from models import Course, Room, TimeSlot, Timetable

app = create_app()

def generate_timetable():
    with app.app_context():

        print("🔄 Starting timetable optimization...")

        # Clear existing timetable
        Timetable.query.delete()
        db.session.commit()

        courses = Course.query.all()
        rooms = Room.query.all()
        slots = TimeSlot.query.all()

        print(f"Courses: {len(courses)}")
        print(f"Rooms: {len(rooms)}")
        print(f"TimeSlots: {len(slots)}")

        used_room_slot = set()
        used_faculty_slot = set()

        total_assigned = 0

        for course in courses:
            print(f"\nTrying to assign course: {course.course_name}")

            assigned = False

            for slot in slots:
                for room in rooms:

                    # Constraint 1: room capacity
                    if room.capacity < 30:
                        continue

                    # Constraint 2: room-time clash
                    if (room.id, slot.id) in used_room_slot:
                        continue

                    # Constraint 3: faculty-time clash
                    if (course.faculty_id, slot.id) in used_faculty_slot:
                        continue

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

                    print(f"✅ Assigned {course.course_name} → {room.room_name} @ {slot.day} {slot.start_time}")

                    total_assigned += 1
                    assigned = True
                    break

                if assigned:
                    break

            if not assigned:
                print(f"⚠️ Could not assign course: {course.course_name}")

        print(f"\n🎉 Optimization finished. Total entries created: {total_assigned}")


if __name__ == "__main__":
    generate_timetable()
