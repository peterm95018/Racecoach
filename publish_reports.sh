#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTIVE_EVENT_FILE="$PROJECT_DIR/active_event.txt"
DRUPAL_DIR="/var/www/html/drupal10/web/sites/default/files/racecoach/events/current"

if [[ $# -gt 1 ]]; then
    echo "Usage: $0 [event-directory]"
    exit 2
fi

if [[ $# -eq 1 ]]; then
    EVENT_DIR="$1"

    if [[ "$EVENT_DIR" != /* ]]; then
        EVENT_DIR="$PROJECT_DIR/$EVENT_DIR"
    fi

    if [[ ! -d "$EVENT_DIR" ]]; then
        echo "ERROR: Event directory not found: $EVENT_DIR"
        exit 1
    fi

    ACTIVE_EVENT="$(basename "$EVENT_DIR")"
else
    if [[ ! -f "$ACTIVE_EVENT_FILE" ]]; then
        echo "ERROR: active_event.txt not found"
        exit 1
    fi

    ACTIVE_EVENT="$(tr -d '[:space:]' < "$ACTIVE_EVENT_FILE")"

    if [[ -z "$ACTIVE_EVENT" ]]; then
        echo "ERROR: active event is empty"
        exit 1
    fi

    EVENT_DIR="$PROJECT_DIR/events/$ACTIVE_EVENT"
fi

REPORT_DIR="$EVENT_DIR/reports"

GRID_SOURCE="$REPORT_DIR/grid_report.html"
LATEST_SOURCE="$REPORT_DIR/latest_report.html"

if [[ ! -f "$GRID_SOURCE" ]]; then
    echo "ERROR: Missing $GRID_SOURCE"
    exit 1
fi

if [[ ! -f "$LATEST_SOURCE" ]]; then
    echo "ERROR: Missing $LATEST_SOURCE"
    exit 1
fi

if [[ ! -d "$(dirname "$DRUPAL_DIR")" ]]; then
    echo "Publishing skipped: Drupal destination is not available on this host."
    exit 0
fi

mkdir -p "$DRUPAL_DIR"

# Copy atomically so Drupal never serves a partially written report.
cp "$GRID_SOURCE" "$DRUPAL_DIR/grid_report.html.tmp"
mv "$DRUPAL_DIR/grid_report.html.tmp" "$DRUPAL_DIR/grid_report.html"

cp "$LATEST_SOURCE" "$DRUPAL_DIR/latest_report.html.tmp"
mv "$DRUPAL_DIR/latest_report.html.tmp" "$DRUPAL_DIR/latest_report.html"

chmod 644 \
    "$DRUPAL_DIR/grid_report.html" \
    "$DRUPAL_DIR/latest_report.html"

echo "Published RaceCoach reports"
echo "Active event: $ACTIVE_EVENT"
ls -l \
    "$DRUPAL_DIR/grid_report.html" \
    "$DRUPAL_DIR/latest_report.html"
