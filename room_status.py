from datetime import datetime
from models import Room, Timetable, TimeSlot


def get_live_room_status():
    now = datetime.now()

    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    status_list = []

    rooms = Room.query.all()

    for room in rooms:
        entry = (
            Timetable.query
            .join(TimeSlot)
            .filter(
                Timetable.room_id == room.id,
                TimeSlot.day == current_day,
                TimeSlot.start_time <= current_time,
                TimeSlot.end_time >= current_time
            )
            .first()
        )

        if entry:
            status_list.append({
                "room": room.room_name,
                "status": "OCCUPIED",
                "course": entry.course.course_name,
                "faculty": entry.faculty.name,
                "batch": f"{entry.course.department} Year"
            })
        else:
            status_list.append({
                "room": room.room_name,
                "status": "FREE"
            })

    return status_list
