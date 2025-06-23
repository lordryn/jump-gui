# models/device.py
from datetime import datetime

class Device:
    def __init__(self, id, hostname, port, status='unknown', registered=None, notes='', device_type=None, last_seen=None):
        self.id = id
        self.hostname = hostname
        self.port = port
        self.status = status
        self.registered = registered or datetime.utcnow().isoformat()
        self.notes = notes
        self.device_type = device_type or self._infer_type()
        self.last_seen = last_seen or self.registered

    def _infer_type(self):
        return 'laptop' if self.hostname.lower().startswith('connectbook') else 'pi'

    def to_dict(self):
        return {
            'id': self.id,
            'hostname': self.hostname,
            'port': self.port,
            'status': self.status,
            'registered': self.registered,
            'last_seen': self.last_seen,
            'notes': self.notes,
            'device_type': self.device_type
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            hostname=data['hostname'],
            port=data['port'],
            status=data.get('status', 'unknown'),
            registered=data.get('registered'),
            notes=data.get('notes', ''),
            device_type=data.get('device_type', 'pi'),
            last_seen=data.get('last_seen')
        )
