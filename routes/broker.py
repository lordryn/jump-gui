import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app

broker_bp = Blueprint("broker", __name__, url_prefix="/broker")


@broker_bp.route("/")
def broker_home():
    status_service = current_app.config["status_service"]
    sessions = status_service._load_sessions()
    techs = status_service._load_techs()
    return render_template("broker.html", sessions=sessions, techs=techs, notification_count=0)


@broker_bp.route("/assign", methods=["POST"])
def assign_session():
    print("[DEBUG] /assign route hit")
    session_id = request.form.get("session_id")
    tech_id = request.form.get("tech_id")
    print(f"[DEBUG] form data: session_id={session_id}, tech_id={tech_id}")

    if not session_id or not tech_id:
        print("[DEBUG] Missing form data — redirecting")
        return redirect(url_for("broker.broker_home"))

    status_service = current_app.config["status_service"]
    status_service.assign(session_id, tech_id)

    return redirect(url_for("broker.broker_home"))

@broker_bp.route("/unassign", methods=["POST"])
def unassign_session():
    session_id = request.form.get("session_id")
    tech_id = request.form.get("tech_id")
    if not session_id or not tech_id:
        return redirect(url_for("broker.broker_home"))

    status_service = current_app.config["status_service"]
    status_service.unassign(session_id, tech_id)
    return redirect(url_for("broker.broker_home"))

# doesn't get called
@broker_bp.route("/preview/<session_id>")
def preview_session(session_id):
    status_service = current_app.config["status_service"]
    url = status_service.mark_in_review(session_id)
    return {"url": url}
