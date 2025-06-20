import json
import base64
import hashlib
import os
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, current_app

device_bp = Blueprint('device', __name__)


# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@device_bp.route("/")
@login_required
def index():
    device_service = current_app.config["device_service"]
    notif_service = current_app.config["notif_service"]

    devices = device_service.get_all_devices()
    notifications = notif_service.get_all()
    return render_template("devices.html", devices=devices,
                           notifications=notifications,
                           notification_count=len(notifications))


@device_bp.route("/register", methods=["POST"])
@login_required
def register():
    device_service = current_app.config["device_service"]
    hostname = request.form["hostname"]
    port = request.form["port"]
    notes = request.form.get("notes", "")
    device_service.register_device(hostname, port, notes)
    return redirect(url_for("device.index"))


@device_bp.route("/ping/<hostname>")
@login_required
def ping(hostname):
    device_service = current_app.config["device_service"]
    device_service.ping_device(hostname)
    return redirect(url_for("device.index"))


@device_bp.route("/delete/<hostname>", methods=["POST"])
@login_required
def delete(hostname):
    device_service = current_app.config["device_service"]
    device_service.delete_device(hostname)
    return redirect(url_for("device.index"))


@device_bp.route("/console/<hostname>")
@login_required
def console(hostname):
    return f"Virtual console for {hostname} not implemented yet"


@device_bp.route("/approve/<hostname>", methods=["POST"])
@login_required
def approve_key(hostname):
    # Load pending keys
    with open("pending_keys.json", "r+") as f:
        pending = json.load(f)
        pubkey = pending.get(hostname)
        if not pubkey:
            print("No pending key for that hostname", "error")
            return redirect(url_for("device.index"))

        # Append to authorized_keys
        with open("/home/dark_phlegm/.ssh/authorized_keys", "a") as authf:
            authf.write(pubkey.strip() + "\n")

        # Remove from pending
        del pending[hostname]
        f.seek(0)
        json.dump(pending, f, indent=2)
        f.truncate()

    # Add to devices if not already in list
    device_service = current_app.config["device_service"]
    existing = device_service.get_device(hostname)
    if not existing:
        device_service.add_device({
            "hostname": hostname,
            "port": None,
            "status": "approved",
            "notes": "Auto-added via approval",
            "device_type": "laptop" if "connectbook" in hostname.lower() else "pi"
        })

    # Remove related notification
    notif_service = current_app.config["notif_service"]
    notif_service.clear_by_hostname(hostname)

    print(f"{hostname} approved and added.", "success")
    return redirect(url_for("device.index"))



@device_bp.route("/reject/<hostname>", methods=["POST"])
@login_required
def reject_key(hostname):
    notif_service = current_app.config["notif_service"]

    with open("pending_keys.json") as f:
        pending = json.load(f)
    pending.pop(hostname, None)
    with open("pending_keys.json", "w") as f:
        json.dump(pending, f, indent=2)

    notif_service.notifications = [
        n for n in notif_service.get_all()
        if not (n["type"] == "auth_request" and n["data"]["hostname"] == hostname)
    ]
    notif_service._save()

    return redirect(url_for("device.index"))


@device_bp.route("/api/request-auth", methods=["POST"])
def request_auth():
    notif_service = current_app.config["notif_service"]
    data = request.get_json()
    hostname = data.get("hostname")
    pubkey = data.get("public_key")

    if not hostname or not pubkey:
        return jsonify({"error": "hostname and public_key required"}), 400

    with open("pending_keys.json", "r+") as f:
        keys = json.load(f)
        keys[hostname] = pubkey
        f.seek(0)
        json.dump(keys, f, indent=2)
        f.truncate()

    key_bytes = base64.b64decode(pubkey.split()[1])
    fingerprint = "SHA256:" + base64.b64encode(hashlib.sha256(key_bytes).digest()).decode().rstrip("=")

    # Avoid duplicate notifications
    if any(n["type"] == "auth_request" and n["data"]["hostname"] == hostname for n in notif_service.get_all()):
        return jsonify({"status": "pending", "note": "already requested"}), 200

    notif_service.add_notification(
        type_='auth_request',
        message=f"New device auth request: {hostname}",
        data={
            "hostname": hostname,
            "public_key": pubkey,
            "submitted": datetime.utcnow().isoformat(),
            "fingerprint": fingerprint
        }
    )

    return jsonify({"hostname": hostname, "status": "pending"}), 200


@device_bp.route("/api/is-authed")
def is_authed():
    hostname = request.args.get("hostname")
    if not hostname:
        return jsonify({"error": "Missing hostname"}), 400

    # Ensure file exists
    if not os.path.exists("pending_keys.json"):
        with open("pending_keys.json", "w") as f:
            json.dump({}, f)

    with open("/home/dark_phlegm/.ssh/authorized_keys") as f:
        authorized = f.read()
    with open("pending_keys.json") as f:
        pending = json.load(f)

    if hostname in pending:
        return jsonify({"status": "pending"}), 200

    if any(hostname in line for line in authorized.splitlines()):
        return jsonify({"status": "approved"}), 200

    return jsonify({"status": "unknown"}), 404
