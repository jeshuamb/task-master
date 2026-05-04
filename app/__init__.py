from flask import Flask, render_template, redirect, url_for, request, flash, session, current_app
from .logger_config import logger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, logout_user, current_user 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .extensions import mail
import time

csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="redis://localhost:6379"
)

def create_app(settings_module):
    
    app = Flask(__name__)
    app.config.from_object(settings_module)
    
    csrf.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.signin" 

    # Blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    # =========================
    #  HANDLERS GLOBALES
    # =========================

    @app.after_request
    def add_header(response):
        endpoint = request.endpoint or ""

        sensitive_routes = {
            "auth.signin",
            "auth.signup",
            "auth.reset_password",
            "auth.reset_password_token",
            "admin.app_page",
            "admin.update_task",
        }

        if endpoint in sensitive_routes:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        else:
            response.headers["Cache-Control"] = "no-cache, must-revalidate, max-age=0"

        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @app.before_request
    def refresh_session_activity():
        
        if session.pop('just_logged_in', False):
            return
        
        ignored_routes = current_app.config.get("IGNORED_ROUTES", [])

        if current_user.is_authenticated and request.endpoint not in ignored_routes:
            session.permanent = True
            session.modified = True

            active_routes = [
                "admin.completed_task",
                "admin.clear_completed",
                "admin.delete_task",
                "admin.update_task"
            ]

            last_modified = session.get('_permanent_last_modified')

            if last_modified:
                total_seconds = app.permanent_session_lifetime.total_seconds()
                elapsed = time.time() - float(last_modified)

                if elapsed >= total_seconds:
                    logout_user()
                    return redirect(url_for("auth.session_expired"))  # 👈 FIX

            if request.endpoint in active_routes:
                session['_permanent_last_modified'] = time.time()

            elif '_permanent_last_modified' not in session:
                session['_permanent_last_modified'] = time.time()

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("El formulario expiró. Intenta nuevamente.", "error_csrf")
        return redirect(request.url)
    
    @app.errorhandler(404)
    def not_found_error(e):
        return render_template("auth/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template("auth/403.html"), 403
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template("auth/405.html"), 405
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        path = request.path

        if "signin" in path:
            type = "login"
        elif "reset_password" in path:
            type = "reset"
        else:
            type = "generic"

        return render_template("auth/429.html", type=type), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Error 500 no controlado")
        return render_template("auth/500.html"), 500

    return app
