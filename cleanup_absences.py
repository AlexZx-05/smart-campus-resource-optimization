from app import create_app
from extensions import db
from models import FacultyAvailability

app = create_app()

with app.app_context():
    deleted = db.session.query(FacultyAvailability).delete()
    db.session.commit()

    print(f"✅ Cleanup complete. Deleted {deleted} absence records.")
