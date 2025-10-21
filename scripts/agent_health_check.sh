#!/bin/bash
# Health check for autonomous agents
#
# Returns:
#   0 - All agents healthy
#   1 - Some agents down
#   2 - All agents down

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Agent Health Check ==="
echo

# Check code_developer daemon
DAEMON_STATUS=0
if pgrep -f "code-developer" > /dev/null; then
    PID=$(pgrep -f "code-developer")
    UPTIME=$(ps -p $PID -o etime= | tr -d ' ')
    echo "✓ code_developer daemon: RUNNING"
    echo "  PID: $PID"
    echo "  Uptime: $UPTIME"
    DAEMON_STATUS=1
else
    echo "✗ code_developer daemon: STOPPED"
fi

echo

# Check daemon detailed status
if [ $DAEMON_STATUS -eq 1 ]; then
    echo "→ Daemon detailed status:"
    poetry run project-manager developer-status 2>/dev/null || echo "  (Status unavailable)"
fi

echo
echo "=== Health Summary ==="
echo

if [ $DAEMON_STATUS -eq 1 ]; then
    echo "✓ All agents healthy"
    exit 0
else
    echo "⚠️ Some agents down"
    echo
    echo "To start agents: ./scripts/start_agents.sh"
    exit 1
fi
