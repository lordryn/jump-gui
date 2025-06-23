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

## 💻 ConnectBox Client Script

`connectbox_client.sh` is a self-contained Bash script used on the ConnectBox device to automate connection with the jump server.

It performs the following:

- Generates an SSH keypair if not already present
- Sends its public key to `/api/request-auth` for approval
- Polls `/api/is-authed` until authorized
- Retrieves its assigned reverse SSH port from the server
- Begins sending heartbeat pings to `/api/ping/<hostname>` every 30 seconds
- Establishes a reverse SSH tunnel to the jump server on the approved port

> ⚠️ Note: The reverse shell behavior is not yet reconfigured for this flow. Further tuning is required to ensure shell access behaves as expected once the tunnel is up.

---

## 🚧 Roadmap

- [x] Device approval from web UI
- [x] `/api/ping` + timed expiration
- [ ] systemd service for client script
- [ ] Theming & customization panel
- [ ] Audit logging

---

---

## 🛠️ Authorship & Project Ownership

This project, **ConnectBox™** and associated programs, were designed and developed by Ryan "Lord Ryn" Wheeler.

All system architecture, core code, and workflow logic were authored and tested by the developer, with AI used as a supplementary tool for troubleshooting, formatting, and planning.

Unless otherwise stated, all code and design decisions originate from the project's creator. AI contributions were used only under human supervision and refinement.

For licensing, contributions, or attribution inquiries, contact: lordryn@yahoo.com