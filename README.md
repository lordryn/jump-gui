# ConnectBox + Jump Server Dashboard

A lightweight Flask-based remote device dashboard with SSH access, registration, and status management via a secure jump server.

## 🔧 Features

- 🔐 Login-authenticated web dashboard
- 💻 Device registration via `/api/register`
- 🟢 Online/offline status with timestamp
- 🧠 Auto-infers device type (e.g. "ConnectBook" vs "ConnectBox")
- 📥 Reverse SSH tunneling support with auto port binding
- 🔔 Notification bell with device approval requests
- ✅ Accept/reject device SSH keys from UI
- 🧹 Auto-purge expired entries (planned)
- 🛠 Theme customization and virtual console placeholders (planned)

## 📂 Project Structure

```
jump-gui/
│
├── app.py                  # Legacy entrypoint (wrapped by connect_app.py)
├── connect_app.py          # Main Flask application class
│
├── models/
│   └── device.py           # Device dataclass
│
├── services/
│   ├── device_service.py   # Device storage and logic (JSON-based)
│   └── notification_service.py  # Notification handling
│
├── routes/
│   ├── auth.py             # Login/logout views
│   └── device.py           # Main dashboard and device views
│
├── templates/
│   ├── base.html           # Layout with notification bell
│   ├── login.html
│   └── devices.html
│
├── static/                 # CSS/JS if needed
├── devices.json            # Persistent device list
├── users.json              # Login credentials
├── notifications.json      # UI alerts for approval etc.
└── pending_keys.json       # Temporary holding for SSH key requests
```

## 📦 Deployment

1. Clone the repo
2. Create and activate a Python virtual environment
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python connect_app.py
   ```

---

## 💻 Client Script (ConnectBox)

Deployable bash script that:
- Tries `ssh -R` on open ports
- Sends device registration to jump server
- Optionally requests SSH key approval

---

## 🚧 Roadmap

- [x] Device approval from web UI
- [ ] `/api/ping` + timed expiration
- [ ] systemd service for client script
- [ ] Theming & customization panel
- [ ] Audit logging

---

## 🧠 Credits

Maintained by Ryan ("lord ryn")  
Written with assistance from ChatGPT (code generation + architecture planning)
