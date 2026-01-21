from models import Course, Room, TimeSlot


def generate_baseline_metrics():
    courses = Course.query.all()
    rooms = Room.query.all()
    slots = TimeSlot.query.all()

    scheduled_classes = len(courses)

    # -----------------------------
    # Simulate MANUAL scheduling behavior
    # -----------------------------

    # Assumption 1: Admin uses only first 2 rooms repeatedly
    used_rooms = min(2, len(rooms))

    # Assumption 2: Manual scheduling causes room reuse conflicts
    room_conflicts = max(0, scheduled_classes - used_rooms)

    # Assumption 3: Faculty workload not balanced
    # If classes exceed safe manual handling threshold
    faculty_conflicts = max(0, scheduled_classes - 3)

    # -----------------------------
    # Room Utilization
    # -----------------------------
    total_possible = len(rooms) * len(slots)
    room_utilization = (
        (scheduled_classes / total_possible) * 100
        if total_possible else 0
    )

    return {
        "scheduled_classes": scheduled_classes,
        "room_utilization_percent": round(room_utilization, 2),
        "room_conflicts": room_conflicts,
        "faculty_conflicts": faculty_conflicts
    }
