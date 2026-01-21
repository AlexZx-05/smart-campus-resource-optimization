from models import Timetable, FacultyAvailability
from extensions import db

def handle_faculty_absence(faculty_id):
    """
    Remove all timetable entries of an absent faculty
    """
    print(f"🚫 Handling absence for faculty_id={faculty_id}")

    deleted = Timetable.query.filter_by(
        faculty_id=faculty_id
    ).delete()

    db.session.commit()

    print(f"🗑️ Removed {deleted} timetable entries")
