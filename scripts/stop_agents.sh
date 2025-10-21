#!/bin/bash
# Stop autonomous agents for MonolithicCoffeeMakerAgent

set -e

echo "=== Stopping MonolithicCoffeeMakerAgent Agents ==="
echo

# Stop code_developer daemon
if pgrep -f "code-developer" > /dev/null; then
    echo "→ Stopping code_developer daemon..."
    pkill -f "code-developer"
    sleep 1

    if pgrep -f "code-developer" > /dev/null; then
        echo "⚠️ Daemon still running, force killing..."
        pkill -9 -f "code-developer"
    fi

    echo "✓ code_developer daemon stopped"
else
    echo "✓ code_developer daemon not running"
fi

echo
echo "=== All Agents Stopped ==="
echo
