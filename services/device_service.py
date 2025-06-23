# services/device_service.py
import json
import os
from models.device import Device

DEVICE_FILE = 'devices.json'

class DeviceService:
    def __init__(self, filepath=DEVICE_FILE):
        self.filepath = filepath
        self.devices = self._load_devices()

    def _load_devices(self):
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        return [Device.from_dict(d) for d in data]

    def _save_devices(self):
        with open(self.filepath, 'w') as f:
            json.dump([d.to_dict() for d in self.devices], f, indent=2)

    def get_all_devices(self):
        return self.devices

    def get_device_by_id(self, device_id):
        return next((d for d in self.devices if d.id == device_id), None)

    def get_device(self, hostname):
        return next((d for d in self.devices if d.hostname == hostname), None)

    def register_device(self, hostname, port, notes=''):
        new_id = max((d.id for d in self.devices), default=0) + 1
        device = Device(id=new_id, hostname=hostname, port=int(port), notes=notes)
        self.devices.append(device)
        self._save_devices()

    def delete_device(self, hostname):
        self.devices = [d for d in self.devices if d.hostname != hostname]
        self._save_devices()

    def ping_device(self, device_id):
        device = self.get_device_by_id(device_id)
        if device:
            device.status = 'Online'
            self._save_devices()

    def add_device(self, data):
        new_id = max((d.id for d in self.devices), default=0) + 1
        device = Device(
            id=new_id,
            hostname=data["hostname"],
            port=data.get("port"),
            status=data.get("status", "Pending"),
            notes=data.get("notes", ""),
            device_type=data.get("device_type", "pi")
        )
        self.devices.append(device)
        self._save_devices()

    def save(self, device):
        for i, d in enumerate(self.devices):
            if d.id == device.id:
                self.devices[i] = device
                break
        self._save_devices()
