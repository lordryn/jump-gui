from flask import Blueprint, render_template, current_app, request, redirect, url_for
import json
import os

broker_bp = Blueprint("broker", __name__, url_prefix="/broker")


@broker_bp.route("/")
def broker_home():
    notif_service = current_app.config["notif_service"]
    notification_count = notif_service.get_unread_count()

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Load sessions
    with open(os.path.join(root_dir, "sessions.json"), "r") as f:
        sessions = json.load(f)

    # Load techs
    with open(os.path.join(root_dir, "techs.json"), "r") as f:
        techs = json.load(f)

    # Split sessions
    unassigned = [s for s in sessions if not s.get("assigned_to")]
    active = [s for s in sessions if s.get("assigned_to")]

    return render_template(
        "broker.html",
        notification_count=notification_count,
        sessions=unassigned,
        active_sessions=active,
        techs=techs
    )


@broker_bp.route("/assign", methods=["POST"])
def assign_session():
    session_id = request.form.get("session_id")
    tech_id = request.form.get("tech_id")

    if not session_id or not tech_id:
        return redirect(url_for("broker.broker_home"))

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sessions_path = os.path.join(root_dir, "sessions.json")
    techs_path = os.path.join(root_dir, "techs.json")

    # Update session assignment
    with open(sessions_path, "r") as f:
        sessions = json.load(f)

    for session in sessions:
        if session["id"] == session_id:
            session["assigned_to"] = tech_id
            break

    with open(sessions_path, "w") as f:
        json.dump(sessions, f, indent=2)

    # Increment assigned tech session count
    with open(techs_path, "r") as f:
        techs = json.load(f)

    for tech in techs:
        if tech["tech_id"] == tech_id:
            tech["sessions_assigned"] = tech.get("sessions_assigned", 0) + 1
            break

    with open(techs_path, "w") as f:
        json.dump(techs, f, indent=2)

    return redirect(url_for("broker.broker_home"))
@broker_bp.route("/unassign", methods=["POST"])
def unassign_session():
    session_id = request.form.get("session_id")

    if not session_id:
        return redirect(url_for("broker.broker_home"))

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sessions_path = os.path.join(root_dir, "sessions.json")
    techs_path = os.path.join(root_dir, "techs.json")

    # Load sessions
    with open(sessions_path, "r") as f:
        sessions = json.load(f)

    tech_id = None
    for session in sessions:
        if session["id"] == session_id and session.get("assigned_to"):
            tech_id = session["assigned_to"]
            session["assigned_to"] = None
            break

    with open(sessions_path, "w") as f:
        json.dump(sessions, f, indent=2)

    # Decrement tech counter
    if tech_id:
        with open(techs_path, "r") as f:
            techs = json.load(f)

        for tech in techs:
            if tech["tech_id"] == tech_id:
                tech["sessions_assigned"] = max(tech.get("sessions_assigned", 1) - 1, 0)
                break

        with open(techs_path, "w") as f:
            json.dump(techs, f, indent=2)

    return redirect(url_for("broker.broker_home"))
@broker_bp.route("/close", methods=["POST"])
def close_session():
    session_id = request.form.get("session_id")

    if not session_id:
        return redirect(url_for("broker.broker_home"))

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sessions_path = os.path.join(root_dir, "sessions.json")
    techs_path = os.path.join(root_dir, "techs.json")

    # Load + remove session
    with open(sessions_path, "r") as f:
        sessions = json.load(f)

    updated_sessions = []
    tech_id = None

    for session in sessions:
        if session["id"] == session_id:
            tech_id = session.get("assigned_to")
            continue  # skip this one (deleting)
        updated_sessions.append(session)

    with open(sessions_path, "w") as f:
        json.dump(updated_sessions, f, indent=2)

    # Decrement tech count if assigned
    if tech_id:
        with open(techs_path, "r") as f:
            techs = json.load(f)

        for tech in techs:
            if tech["tech_id"] == tech_id:
                tech["sessions_assigned"] = max(tech.get("sessions_assigned", 1) - 1, 0)
                break

        with open(techs_path, "w") as f:
            json.dump(techs, f, indent=2)

    return redirect(url_for("broker.broker_home"))


