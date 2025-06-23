from flask import Flask
from routes.auth import auth_bp
from routes.device import device_bp
from routes.api import bp as api_bp
from services.device_service import DeviceService
from services.user_service import UserService
from services.notification_service import NotificationService
from datetime import datetime, timedelta

class ConnectApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "supersecret"

        # Shared services
        self.device_service = DeviceService()
        self.user_service = UserService()
        self.notification_service = NotificationService()

        # Inject shared service into app config
        self.app.config["device_service"] = self.device_service
        self.app.config["user_service"] = self.user_service
        self.app.config["notif_service"] = self.notification_service

        # Register routes
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(device_bp)
        self.app.register_blueprint(api_bp)

        # Auto-offline device timeout logic
        @self.app.before_request
        def update_device_statuses():
            now = datetime.utcnow()
            threshold = timedelta(minutes=2)
            for device in self.device_service.get_all_devices():
                if device.last_seen:
                    last_seen = datetime.fromisoformat(device.last_seen)
                    if now - last_seen > threshold:
                        device.status = "Offline"
            self.device_service._save_devices()

    def run(self, **kwargs):
        self.app.run(**kwargs)


if __name__ == "__main__":
    app_instance = ConnectApp()
    app_instance.run()
