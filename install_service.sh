#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/racecoach"
SERVICE="$HOME/.config/systemd/user/racecoach-watch.service"

mkdir -p "$HOME/.config/systemd/user"

cat > "$SERVICE" <<EOF
[Unit]
Description=RaceCoach upload watcher

[Service]
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/python -m racecoach.watch_uploads --event $APP_DIR/events/sample_event
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
