#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/racecoach"
SERVICE="$HOME/.config/systemd/user/racecoach-watch.service"

ACTIVE_EVENT=$(cat "$APP_DIR/active_event.txt")
EVENT_DIR="$APP_DIR/events/$ACTIVE_EVENT"

mkdir -p "$HOME/.config/systemd/user"
 
cat > "$SERVICE" <<EOF
[Unit]
Description=RaceCoach upload watcher

[Service]
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/python -m racecoach.watch_uploads \
  --uploads $EVENT_DIR/uploads \
  --processed $EVENT_DIR/processed \
  --reports $EVENT_DIR/reports \
  --event $EVENT_DIR
Restart=always
RestartSec=3



[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable racecoach-watch.service
systemctl --user restart racecoach-watch.service

echo "Installed and started user service: racecoach-watch.service"
echo "Check status with:"
echo "systemctl --user status racecoach-watch.service"
