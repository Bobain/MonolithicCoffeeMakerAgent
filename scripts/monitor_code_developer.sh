#!/bin/bash
# Monitor code_developer daemon with live status updates
#
# This script displays the code_developer status every minute with
# a progress bar, current task, and recent activity.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
UPDATE_INTERVAL=${1:-60}  # Default: 60 seconds
CLEAR_SCREEN=${CLEAR_SCREEN:-true}

echo "=== code_developer Monitor ==="
echo "Update interval: ${UPDATE_INTERVAL}s"
echo "Press Ctrl+C to stop"
echo

while true; do
    if [ "$CLEAR_SCREEN" = "true" ]; then
        clear
    fi

    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║              code_developer Status Monitor                         ║"
    echo "║              Updated: $(date '+%Y-%m-%d %H:%M:%S')                        ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo

    # Get daemon status
    poetry run project-manager developer-status 2>/dev/null || echo "⚠️ Daemon not responding"

    echo
    echo "────────────────────────────────────────────────────────────────────"
    echo "Next update in ${UPDATE_INTERVAL}s... (Press Ctrl+C to stop)"
    echo

    sleep "$UPDATE_INTERVAL"
done
