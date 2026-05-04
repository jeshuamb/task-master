import os
from app import create_app
from config import config

# env = os.getenv("FLASK_ENV", "default")
env = os.getenv("CONFIG_ENV", "development")

app = create_app(config[env])

if app.debug:
    app.logger.info(f"ENV: {env}")
    app.logger.info(f"SECURE COOKIE: {app.config['SESSION_COOKIE_SECURE']}")

if __name__ == "__main__":
    app.run()
