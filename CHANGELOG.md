# Changelog

## [0.2.0] - 2025-06-23

### Added
- `connectbox_client.sh` script for headless ConnectBox clients
- Public key registration and polling via `/api/is-authed`
- Heartbeat ping system via `/api/ping/<hostname>`
- Automatic reverse SSH tunnel setup after approval

### Fixed
- Flask route `/api/is-authed` now properly uses `current_app.config["device_service"]`

### Notes
- Reverse shell interaction still pending refactor
