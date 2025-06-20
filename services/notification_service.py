# services/notification_service.py
import json
import os
from datetime import datetime

NOTIF_FILE = "notifications.json"

class NotificationService:
    def __init__(self, filepath=NOTIF_FILE):
        self.filepath = filepath
        self.notifications = self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.notifications, f, indent=2)

    def get_all(self):
        return self.notifications

    def get_unread_count(self):
        return len(self.notifications)

    def add_notification(self, type_, message, data=None):
        note = {
            "type": type_,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        self.notifications.append(note)
        self._save()

    def clear_by_type(self, type_):
        self.notifications = [n for n in self.notifications if n["type"] != type_]
        self._save()

    def clear_by_hostname(self, hostname):
        self.notifications = [
            n for n in self.notifications
            if n.get("data", {}).get("hostname") != hostname
        ]
        self._save()

