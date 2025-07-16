import os
import json
from threading import Lock
from datetime import datetime

class StatusService:
    def __init__(self, file_path="sessions.json"):
        self.sessions_path = file_path
        self.techs_path = os.path.join(os.path.dirname(file_path), "techs.json")
        self.lock = Lock()
        if not os.path.exists(self.sessions_path):
            with open(self.sessions_path, "w") as f:
                json.dump([], f)
        if not os.path.exists(self.techs_path):
            with open(self.techs_path, "w") as f:
                json.dump([], f)

    def _load_sessions(self):
        with open(self.sessions_path, "r") as f:
            return json.load(f)

    def _save_sessions(self, sessions):
        with open(self.sessions_path, "w") as f:
            json.dump(sessions, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

    def _load_techs(self):
        with open(self.techs_path, "r") as f:
            return json.load(f)

    def _save_techs(self, techs):
        with open(self.techs_path, "w") as f:
            json.dump(techs, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

    def update_status(self, session_id, status):
        with self.lock:
            sessions = self._load_sessions()
            updated = False
            for session in sessions:
                if session.get("id") == session_id:
                    session["status"] = status
                    updated = True
                    break
            if updated:
                self._save_sessions(sessions)
            return updated

    def get_status(self, session_id):
        with self.lock:
            sessions = self._load_sessions()
            for session in sessions:
                if session.get("id") == session_id:
                    return session.get("status")
            return None

    def assign(self, session_id, tech_id):
        with self.lock:
            sessions = self._load_sessions()
            techs = self._load_techs()

            print(f"[DEBUG] Attempting to assign session_id={session_id} to tech_id={tech_id}")

            found_session = False
            for session in sessions:
                if session["id"] == session_id:
                    print(f"[DEBUG] Found session match: {session}")
                    session["assigned_to"] = tech_id
                    session["status"] = "assigned to tech"
                    found_session = True
                    break

            if not found_session:
                print(f"[ERROR] No matching session found for id: {session_id}")

            found_tech = False
            for tech in techs:
                if tech["tech_id"] == tech_id:
                    tech["sessions_assigned"] = tech.get("sessions_assigned", 0) + 1
                    found_tech = True
                    break

            if not found_tech:
                print(f"[ERROR] No matching tech found for id: {tech_id}")

            self._save_sessions(sessions)
            self._save_techs(techs)

            print(f"[DEBUG] Sessions saved: {sessions}")

    def unassign(self, session_id, tech_id):
        with self.lock:
            sessions = self._load_sessions()
            techs = self._load_techs()
            for session in sessions:
                if session["id"] == session_id and session["assigned_to"] == tech_id:
                    session["assigned_to"] = None
                    session["status"] = "pending"
                    break
            for tech in techs:
                if tech["tech_id"] == tech_id:
                    tech["sessions_assigned"] = max(tech.get("sessions_assigned", 1) - 1, 0)
                    break
            self._save_sessions(sessions)
            self._save_techs(techs)

    def mark_in_review(self, session_id):
        with self.lock:
            sessions = self._load_sessions()
            for session in sessions:
                if session["id"] == session_id:
                    print(f"[DEBUG] Marking session {session_id} in review.")
                    session["status"] = "in review"
                    self._save_sessions(sessions)
                    return session.get("show_me_url")
            print(f"[ERROR] Session ID {session_id} not found in mark_in_review()")
            return None
