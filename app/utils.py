from flask import current_app
from datetime import timezone

def get_ve():
    return current_app.config.get("TIMEZONE", timezone.utc)