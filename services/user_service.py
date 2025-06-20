# services/user_service.py
import json
import os

USER_FILE = 'users.json'

class UserService:
    def __init__(self, filepath=USER_FILE):
        self.filepath = filepath
        self.users = self._load_users()

    def _load_users(self):
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def verify_credentials(self, username, password):
        for user in self.users:
            if user['username'] == username and user['password'] == password:
                return True
        return False
