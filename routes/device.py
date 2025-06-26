import json
import base64
import hashlib
import os
import threading
import time
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, current_app
from services.notification_service import NotificationService

heartbeat_threads = {}

device_bp = Blueprint('device', __name__)

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function

def find_next_available_port(start=22222, end=22300):
    device_service = current_app.config["device_service"]
    used_ports = {d.port for d in device_service.get_all_devices() if d.port}
    for port in range(start, end):
        if port not in used_ports:
            return port
    raise Exception("No available ports in range")

@device_bp.route("/", methods=["GET"])
@login_required
def index():
    device_service = current_app.config["device_service"]
    devices = device_service.get_all_devices()
    notif_service = current_app.config["notif_service"]
    notifications = notif_service.get_all()
    notification_count = len(notifications)

    return render_template("devices.html", devices=devices, notifications=notifications,
                           notification_count=notification_count)


@device_bp.route("/api/is-authed", methods=["GET"])
def is_authed():
    hostname = request.args.get("hostname")
    device_service = current_app.config["device_service"]
    device = device_service.get_device(hostname)
    if device:
        return jsonify({"status": "authed", "port": device.port})
    return jsonify({"status": "pending"})\

@device_bp.route("/api/request-auth", methods=["POST"])
def request_auth():
    data = request.get_json()
    hostname = data.get("hostname")
    pubkey = data.get("public_key")

    if not hostname or not pubkey:
        return jsonify({"error": "hostname and public_key are required"}), 400

    pending_file = "pending_keys.json"

    try:
        if os.path.exists(pending_file):
            with open(pending_file, "r") as f:
                pending = json.load(f)
        else:
            pending = {}

        pending[hostname] = pubkey

        with open(pending_file, "w") as f:
            json.dump(pending, f, indent=2)

        notif_service = current_app.config["notif_service"]
        notif_service.add_notification(
            type_="auth_request",
            message=f"New device requesting auth: {hostname}",
            data={"hostname": hostname}
        )

        print(f"[REQUEST-AUTH] Key saved for {hostname}")
        return jsonify({"status": "pending"}), 200

    except Exception as e:
        print(f"[REQUEST-AUTH] Failed: {e}")
        return jsonify({"error": str(e)}), 500


@device_bp.route("/heartbeat/start/<hostname>", methods=["POST"])
@login_required
def start_heartbeat(hostname):
    if hostname in heartbeat_threads:
        return jsonify({"status": "already running"}), 200

    def heartbeat_loop():
        while True:
            try:
                requests.post(f"http://{hostname}:5000/api/ping/{hostname}")
                print(f"[Heartbeat] Ping sent to {hostname} at {datetime.utcnow().isoformat()}")
                time.sleep(30)
            except Exception as e:
                print(f"[Heartbeat] Error: {e}")
                break

    thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_threads[hostname] = thread
    thread.start()
    return jsonify({"status": "started"}), 200

@device_bp.route("/heartbeat/stop/<hostname>", methods=["POST"])
@login_required
def stop_heartbeat(hostname):
    # Simplified stop logic (to be replaced with a smarter signal system)
    if hostname in heartbeat_threads:
        del heartbeat_threads[hostname]  # Future versions should use an event flag
        return jsonify({"status": "stopped"}), 200
    return jsonify({"status": "not running"}), 404

@device_bp.route("/ping/<hostname>", methods=["GET"])
@login_required
def ping(hostname):
    print(f"[PING] Simulated ping to {hostname}")
    return redirect(url_for("device.index"))

@device_bp.route("/delete/<hostname>", methods=["POST"])
@login_required
def delete_device(hostname):
    device_service = current_app.config["device_service"]
    notif_service = current_app.config["notif_service"]

    # 1. Try removing from authorized_keys
    key_path = os.path.expanduser("~/.ssh/authorized_keys")
    try:
        with open(key_path, "r") as f:
            lines = f.readlines()

        updated_lines = [line for line in lines if hostname not in line]

        if len(updated_lines) == len(lines):
            print(f"[DELETE] No SSH key found for {hostname}. Aborting delete.")
            return redirect(url_for("device.index"))

        with open(key_path, "w") as f:
            f.writelines(updated_lines)
        print(f"[DELETE] SSH key for {hostname} removed.")

    except Exception as e:
        print(f"[DELETE] Error removing key for {hostname}: {e}")
        return redirect(url_for("device.index"))

    # 2. Remove from pending_keys.json if present
    try:
        with open("pending_keys.json", "r+") as f:
            pending = json.load(f)
            if hostname in pending:
                del pending[hostname]
                f.seek(0)
                json.dump(pending, f, indent=2)
                f.truncate()
                print(f"[DELETE] {hostname} removed from pending_keys.")
    except FileNotFoundError:
        pass

    # 3. Remove from devices.json
    device_service.delete_device(hostname)

    # 4. Clear associated notifications
    notif_service.clear_by_hostname(hostname)

    print(f"[DELETE] Device {hostname} fully removed.")
    return redirect(url_for("device.index"))


@device_bp.route("/console/<hostname>")
@login_required
def console(hostname):
    print(f"[Console] Placeholder for {hostname}")
    return redirect(url_for("device.index"))

@device_bp.route("/approve/<hostname>", methods=["POST"])
@login_required
def approve_key(hostname):
    key_path = os.path.expanduser("~/.ssh/authorized_keys")
    with open("pending_keys.json", "r+") as f:
        pending = json.load(f)
        pubkey = pending.get(hostname)
        if not pubkey:
            print(f"[APPROVE] No pending key for {hostname}", "error")
            return redirect(url_for("device.index"))

        with open(key_path, "a") as authf:
            authf.write(pubkey.strip() + "\n")

        del pending[hostname]
        f.seek(0)
        json.dump(pending, f, indent=2)
        f.truncate()

    device_service = current_app.config["device_service"]
    if not device_service.get_device(hostname):
        assigned_port = find_next_available_port()
        device_service.add_device({
            "hostname": hostname,
            "port": assigned_port,
            "status": "approved",
            "notes": "Auto-added via approval",
            "device_type": "laptop" if "connectbook" in hostname.lower() else "pi"
        })

    notif_service = current_app.config["notif_service"]
    notif_service.clear_by_hostname(hostname)

    print(f"[APPROVE] {hostname} approved and added.")
    return redirect(url_for("device.index"))

@device_bp.route("/reject/<hostname>", methods=["POST"])
@login_required
def reject_key(hostname):
    with open("pending_keys.json", "r+") as f:
        pending = json.load(f)
        if hostname in pending:
            del pending[hostname]
            f.seek(0)
            json.dump(pending, f, indent=2)
            f.truncate()

    notif_service = current_app.config["notif_service"]
    notif_service.clear_by_hostname(hostname)

    print(f"[REJECT] {hostname} rejected and removed from pending.")
    return redirect(url_for("device.index"))
