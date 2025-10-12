#!/bin/bash
# Start autonomous agents for MonolithicCoffeeMakerAgent
#
# This script ensures code_developer daemon is running in the background
# and provides instructions for making project_manager always available.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Starting MonolithicCoffeeMakerAgent Agents ==="
echo

# Check if code_developer daemon is already running
if pgrep -f "code-developer" > /dev/null; then
    echo "✓ code_developer daemon already running"
    PID=$(pgrep -f "code-developer")
    echo "  PID: $PID"
else
    echo "→ Starting code_developer daemon..."
    nohup poetry run code-developer --auto-approve > daemon.log 2>&1 &
    DAEMON_PID=$!
    sleep 2

    if ps -p $DAEMON_PID > /dev/null; then
        echo "✓ code_developer daemon started (PID: $DAEMON_PID)"
        echo "  Log: daemon.log"
    else
        echo "✗ Failed to start code_developer daemon"
        exit 1
    fi
fi

echo
echo "→ Checking daemon status..."
poetry run project-manager developer-status

echo
echo "=== Agent Status ==="
echo
echo "✓ code_developer: Running in background (autonomous)"
echo "✓ project_manager: Available in Claude CLI sessions"
echo
echo "Usage:"
echo "  • Check daemon: poetry run project-manager developer-status"
echo "  • View logs: tail -f daemon.log"
echo "  • Stop daemon: pkill -f code-developer"
echo "  • Use project_manager: /agent-project-manager (in Claude CLI)"
echo
