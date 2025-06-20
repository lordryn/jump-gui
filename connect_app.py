from flask import Flask
from routes.auth import auth_bp
from routes.device import device_bp
from services.device_service import DeviceService
from services.user_service import UserService
from services.notification_service import NotificationService


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

    def run(self, **kwargs):
        self.app.run(**kwargs)


if __name__ == "__main__":
    app_instance = ConnectApp()
    app_instance.run()
