#!/bin/bash
# connectbox_client.sh - Auto-register + heartbeat + reverse tunnel ConnectBox client

JUMP_SERVER="wcserv.local"
API_PORT=5000
SSH_USER="ryn"
START_PORT=22222
HOSTNAME=$(hostname)
KEY_PATH="$HOME/.ssh/id_ed25519"
REGISTERED=false
AUTHPORT=0

log() {
  echo "[$(date)] $1"
}

# Generate key if missing
if [ ! -f "$KEY_PATH" ]; then
  log "Generating SSH key..."
  ssh-keygen -t ed25519 -f "$KEY_PATH" -N ""
fi

PUBKEY=$(cat "$KEY_PATH.pub")

# Request auth with public key
log "Requesting authorization..."
curl -s -X POST "http://$JUMP_SERVER:$API_PORT/api/request-auth" \
  -H "Content-Type: application/json" \
  -d "{\"hostname\": \"$HOSTNAME\", \"port\": $START_PORT, \"public_key\": \"$PUBKEY\"}"

# Poll until authorized
while true; do
  RESPONSE=$(curl -s "http://$JUMP_SERVER:$API_PORT/api/is-authed?hostname=$HOSTNAME")
  STATUS=$(echo $RESPONSE | grep -o '"status":"[^"]*' | cut -d'"' -f4)
  if [ "$STATUS" == "authed" ]; then
    AUTHPORT=$(echo $RESPONSE | grep -o '"port":[0-9]*' | cut -d':' -f2)
    log "Authorized! Assigned port: $AUTHPORT"
    break
  else
    log "Waiting for approval..."
    sleep 5
  fi
done

# Start heartbeat loop in background
(while true; do
  curl -s -o /dev/null -X POST "http://$JUMP_SERVER:$API_PORT/api/ping/$HOSTNAME"
  log "Ping sent."
  sleep 30
done) &

# Launch reverse SSH tunnel
log "Starting reverse SSH tunnel on port $AUTHPORT..."
ssh -i "$KEY_PATH" -N -R $AUTHPORT:localhost:22 $SSH_USER@$JUMP_SERVER
