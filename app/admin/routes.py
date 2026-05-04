from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user 
from datetime import timezone
from ..utils import get_ve
from .models import Task
from .forms import Tasks

from . import admin_bp

@admin_bp.route("/app/", methods=["GET", "POST"])
@login_required
def app_page():
    
    form = Tasks()
    filter_type = request.args.get("filter", "all")

    if filter_type == "active":
        tasks = Task.get_tasks().filter_by(user_id=current_user.id, completed=False).all()
    elif filter_type == "completed":
        tasks = Task.get_tasks().filter_by(user_id=current_user.id, completed=True).all()
    else:
        tasks = Task.get_tasks().filter_by(user_id=current_user.id).all()

    total_count = Task.get_tasks().filter_by(user_id=current_user.id).count()
    tasks_completed_count = Task.get_tasks().filter_by(user_id=current_user.id, completed=True).count()

    if form.validate_on_submit():
        content = form.content.data
        
        task = Task(content=content, user_id=current_user.id)
        task.save()
        return redirect(url_for("admin.app_page", filter=filter_type))
    
    VE = get_ve()
    show_welcome = session.pop('show_welcome', False)
    return render_template("admin/task_master.html",
                            form=form, 
                            tasks=tasks,
                            filter_type=filter_type,
                            total_count=total_count,
                            tasks_completed_count=tasks_completed_count,
                            VE=VE,
                            timezone=timezone,
                            show_welcome=show_welcome)

@admin_bp.route("/app/completed/<id>/", methods=["POST"])
@login_required
def completed_task(id):

    task = Task.get_task_by_id(id)

    if task is None or task.user_id != current_user.id:
        flash("¡No tienes permiso para modificar el estado de esa tarea!", "error_tarea")
        return redirect(url_for("admin.app_page"))
    
    task.completed = not task.completed
    task.save()
    return redirect(url_for("admin.app_page"))

@admin_bp.route("/app/clear_completed/", methods=["POST"])
@login_required
def clear_completed():
    tasks = Task.get_tasks().filter_by(user_id=current_user.id, completed=True).all()

    if not tasks:
        flash("¡No hay tareas completadas para eliminar!", "error_completadas")
        return redirect(url_for("admin.app_page"))
    
    for task in tasks:
        task.delete()
    return redirect(url_for("admin.app_page"))

@admin_bp.route('/app/update_task/<id>/', methods=["GET","POST"])
@login_required
def update_task(id=None):
    
    task = Task.get_task_by_id(id)

    if task is None or task.user_id != current_user.id:
        flash("¡No tienes permiso para acceder a esa tarea!", "error_tarea")
        return redirect(url_for("admin.app_page"))

    form = Tasks(obj=task)
    if form.validate_on_submit():
        task.content = form.content.data
        task.save()
        return redirect(url_for("admin.app_page"))
    return render_template("admin/update.html", form=form, task=task)

@admin_bp.route('/app/delete_task/<id>/', methods=["POST"])
@login_required
def delete_task(id=None):

    task = Task.get_task_by_id(id)

    if task is None or task.user_id != current_user.id:
        flash("¡No tienes permiso para eliminar esa tarea!", "error_tarea")
        return redirect(url_for("admin.app_page"))

    task.delete()
    return redirect(url_for("admin.app_page"))