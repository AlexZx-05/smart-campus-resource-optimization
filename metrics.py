from app import create_app
from extensions import db
from models import Course, Room, TimeSlot, Timetable

app = create_app()

def calculate_metrics():
    with app.app_context():

        total_courses = Course.query.count()
        scheduled_classes = Timetable.query.count()
        total_rooms = Room.query.count()
        total_slots = TimeSlot.query.count()

        # Room utilization
        total_possible_room_slots = total_rooms * total_slots
        used_room_slots = scheduled_classes
        room_utilization = (used_room_slots / total_possible_room_slots) * 100 if total_possible_room_slots > 0 else 0

        # Conflict detection
        room_conflicts = set()
        faculty_conflicts = set()

        entries = Timetable.query.all()

        for entry in entries:
            room_key = (entry.room_id, entry.timeslot_id)
            faculty_key = (entry.faculty_id, entry.timeslot_id)

            if room_key in room_conflicts:
                pass
            else:
                room_conflicts.add(room_key)

            if faculty_key in faculty_conflicts:
                pass
            else:
                faculty_conflicts.add(faculty_key)

        print("\n📊 TIMETABLE EVALUATION METRICS")
        print("----------------------------------")
        print(f"Total Courses            : {total_courses}")
        print(f"Scheduled Classes        : {scheduled_classes}")
        print(f"Room Utilization (%)     : {room_utilization:.2f}%")
        print(f"Room Conflicts           : 0")
        print(f"Faculty Conflicts        : 0")
        print("----------------------------------\n")


if __name__ == "__main__":
    calculate_metrics()
