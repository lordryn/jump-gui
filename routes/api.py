from flask import Blueprint, jsonify, request, current_app
from datetime import datetime

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
