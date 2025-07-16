import time
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import os
import json
from services.status_service import StatusService

bp = Blueprint('api', __name__, url_prefix='/api')
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sessions_path = os.path.join(root_dir, "sessions.json")
status_service = StatusService(sessions_path)

@bp.route('/ping/<hostname>', methods=['POST'])
def ping(hostname):
    device_service = current_app.config["device_service"]
    device = device_service.get_device(hostname)
    if device:
        device.status = "Online"
        device.last_seen = datetime.utcnow().isoformat()
        device_service.save(device)
        return jsonify({"status": "ok"}), 200
    return jsonify({"error": "device not found"}), 404

@bp.route("/request-session", methods=["POST"])
def request_session_binary():
    filename = request.args.get("filename")
    if not filename or not request.data:
        return jsonify({"error": "Missing filename or data"}), 400

    static_video_dir = os.path.join(os.path.dirname(__file__), "..", "static", "videos")
    os.makedirs(static_video_dir, exist_ok=True)
    file_path = os.path.join(static_video_dir, filename)

    with open(file_path, "wb") as f:
        f.write(request.data)

    base_name = os.path.splitext(filename)[0]
    parts = base_name.split("_")
    identifier = parts[0] if len(parts) > 1 else "UnknownClient"
    client_id = parts[1] if len(parts) > 1 else base_name

    session_id = f"sess{int(time.time())}"
    session = {
        "id": session_id,
        "client_id": client_id,
        "identifier": identifier,
        "request_time": datetime.utcnow().isoformat(),
        "show_me_url": f"/static/videos/{filename}",
        "assigned_to": None,
        "status": "pending"
    }

    with open(sessions_path, "r") as f:
        sessions = json.load(f)

    sessions.append(session)

    with open(sessions_path, "w") as f:
        json.dump(sessions, f, indent=2)

    status_service.update_status(session_id, "pending")

    return jsonify({"status": "uploaded", "session_id": session_id})

@bp.route('/status/<ticket_id>', methods=['GET'])
def get_ticket_status(ticket_id):
    status = status_service.get_status(ticket_id)
    if not status:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({"id": ticket_id, "status": status})

@bp.route('/status/<ticket_id>', methods=['POST'])
def update_ticket_status(ticket_id):
    data = request.json
    status = data.get("status")
    assigned_to = data.get("assigned_to")
    if not status:
        return jsonify({"error": "Missing status"}), 400
    status_service.update_status(ticket_id, status, assigned_to)
    return jsonify({"message": "Status updated"}), 200
@bp.route('/sessions', methods=['GET'])
def get_sessions_by_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    sessions = status_service._load_sessions()
    filtered = [s for s in sessions if s.get("identifier") == user_id]

    if not filtered:
        return jsonify({"latest": None, "total": 0})

    latest = max(filtered, key=lambda s: s.get("request_time", ""))

    return jsonify({
        "latest": {
            "id": latest.get("id"),
            "status": latest.get("status"),
            "client_id": latest.get("client_id")
        },
        "total": len(filtered)
    })

