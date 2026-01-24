from .health import health_bp
from .master import master_bp
from .timetable import timetable_bp
from .preferences import preference_bp
from .suggestion import suggestion_bp
from .booking import booking_bp
from .reschedule import reschedule_bp
from .conflict import conflict_bp
from .optimize_api import optimize_bp
# import other blueprints here

    
    # register others the same way

def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(master_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(preference_bp)
    app.register_blueprint(suggestion_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(reschedule_bp)
    app.register_blueprint(conflict_bp)
    app.register_blueprint(optimize_bp)
