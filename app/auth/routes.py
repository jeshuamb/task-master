from flask import render_template, redirect, url_for, request, flash, session, jsonify, current_app, abort
from flask_login import login_user, current_user, logout_user, login_required
from ..helpers import send_reset_email, reset_generation_token, verify_reset_token
from .models import User
from flask_wtf.csrf import  generate_csrf
from .forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordTokenForm
import time

from . import auth_bp
from app import login_manager, limiter

@auth_bp.route('/signup/', methods=["GET", "POST"])
def signup():

    if current_user.is_authenticated:
        return redirect(url_for("admin.app_page"))
    
    session.permanent = False
    
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data
        password = form.password.data

        new_user = User.get_user_by_email(email=email)

        if new_user is not None:
            flash("El correo ya está registrado. Inicia sesión o usa otro.", "error_registro")
            return redirect(url_for("auth.signup"))

        user = User(name=name, email=email)
        user.set_password(password=password)
        user.save()
        flash("¡Listo! Registro completado ✅", "exito_registro")
        return redirect(url_for("auth.signin"))
    return render_template('auth/registrarse.html', form=form)

@auth_bp.route('/signin/', methods=["GET", "POST"])
@limiter.limit("5 per minute")
def signin():
        
    if current_user.is_authenticated:
        return redirect(url_for("admin.app_page"))
    
    session.permanent = False
    
    form = LoginForm()
    
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.get_user_by_email(email=email)

        if user is None:
            flash("¡Usuario no encontrado!", "error_usuario")
            return redirect(url_for("auth.signin"))
        elif not user.verify_password(password=password):
            flash("¡Contraseña incorrecta!", "error_contraseña")
            return redirect(url_for("auth.signin"))
        else:
            login_user(user, remember=False)
            session.permanent = True
            session['_permanent_last_modified'] = time.time()
            session['just_logged_in'] = True
            session['show_welcome'] = True
            return redirect(url_for("admin.app_page"))
    return render_template('auth/iniciar_sesion.html', form=form)

@auth_bp.route('/reset_password/', methods=["GET", "POST"])
@limiter.limit("5 per minute")
@limiter.limit("15 per hour")
def reset_password():

    form = ResetPasswordForm()

    if request.method == "POST" and form.validate_on_submit():
        
        email = form.email.data

        user = User.get_user_by_email(email=email)

        if user:
            token = reset_generation_token(user_id=user.id)
            link = url_for("auth.reset_password_token", token=token, _external=True)
            email_sent = send_reset_email(email=email, link=link)

            if not email_sent:
                flash("No se pudo enviar el correo en este momento. Intenta nuevamente más tarde. Si estás usando una VPN, desactívala para continuar con el restablecimiento de contraseña.", "error_email")
                return render_template('auth/reset_password.html', form=form)

        flash("Si existe una cuenta asociada a ese correo electrónico, se ha enviado un enlace para restablecer la contraseña.", "info_email")

    return render_template('auth/reset_password.html', form=form)

@auth_bp.route("/reset_password_token/<token>/", methods=["GET", "POST"])
def reset_password_token(token):

    form = ResetPasswordTokenForm()

    user_id = verify_reset_token(token)

    if not user_id:
        flash("El enlace de restablecimiento de contraseña no es válido o ha expirado.", "error_token")
        return redirect(url_for("auth.reset_password"))
    
    if request.method == "POST" and form.validate_on_submit():
        password = form.password.data
        user = User.get_user_by_id(user_id)

        if user is None:
            flash("El enlace de restablecimiento de contraseña no es válido o el usuario ya no existe.", "error_token")
            return redirect(url_for("auth.reset_password"))

        user.set_password(password=password)
        user.save()
        flash("¡Contraseña restablecida exitosamente! Ahora puedes iniciar sesión con tu nueva contraseña.", "success_token")
        return redirect(url_for("auth.signin"))


    return render_template("auth/reset_password_token.html", form=form, token=token)

@auth_bp.route('/logout/', methods=["POST"])
@login_required
def logout():
    logout_user()          
    session.clear()
    return redirect(url_for("auth.signin"), code=303)

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(int(user_id))

@auth_bp.route("/csrf-token", methods=["GET"])
def csrf_token():
    return jsonify({"csrf_token": generate_csrf()})

@auth_bp.route("/session_status")
@login_required
def session_status():
    
    total_seconds = current_app.permanent_session_lifetime.total_seconds()
    
    last_modified = session.get('_permanent_last_modified')
    if last_modified is None:
        last_modified = time.time()
        session['_permanent_last_modified'] = last_modified

    elapsed = time.time() - float(last_modified)
    remaining = total_seconds - elapsed

    if remaining <= 0:
        logout_user()
        session.clear()
        return jsonify({"expired": True}), 401

    return jsonify({
        "remaining": remaining
    })

@auth_bp.route("/refresh_session", methods=["POST"])
@login_required
def refresh_session():
    session.permanent = True
    session.modified = True
    session['_permanent_last_modified'] = time.time()
    return jsonify({"ok": True})

@auth_bp.route("/session_expired/")
def session_expired():
    return render_template("auth/session_expired.html")

@auth_bp.route("/auto_logout", methods=["POST"])
@login_required
def auto_logout():
    logout_user()
    session.clear()
    return "", 204