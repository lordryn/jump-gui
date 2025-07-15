import time

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import os
import json

bp = Blueprint('api', __name__, url_prefix='/api')

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

    # Save binary video to /static/videos/
    static_video_dir = os.path.join(os.path.dirname(__file__), "..", "static", "videos")
    os.makedirs(static_video_dir, exist_ok=True)
    file_path = os.path.join(static_video_dir, filename)

    with open(file_path, "wb") as f:
        f.write(request.data)

    # Try to extract client ID from filename (e.g., HOST_2025_07_15_14_00_00.avi)
    base_name = os.path.splitext(filename)[0]
    client_id = base_name.split("_")[0] if "_" in base_name else "UnknownClient"

    session = {
        "id": f"sess{int(time.time())}",
        "client_id": client_id,
        "request_time": datetime.utcnow().isoformat(),
        "show_me_url": f"/static/videos/{filename}",
        "assigned_to": None
    }

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sessions_path = os.path.join(root_dir, "sessions.json")

    with open(sessions_path, "r") as f:
        sessions = json.load(f)

    sessions.append(session)

    with open(sessions_path, "w") as f:
        json.dump(sessions, f, indent=2)

    return jsonify({"status": "uploaded", "session_id": session["id"]})
