from models import Room, TimeSlot, Timetable

def get_vacant_slots():
    vacant = []

    rooms = Room.query.all()
    slots = TimeSlot.query.all()

    # Create a set of occupied (room_id, slot_id)
    occupied = set(
        (t.room_id, t.timeslot_id)
        for t in Timetable.query.all()
    )

    for room in rooms:
        for slot in slots:
            if (room.id, slot.id) not in occupied:
                vacant.append({
                    "room": room.room_name,
                    "day": slot.day,
                    "time": f"{slot.start_time} - {slot.end_time}"
                })

    return vacant
