#!/bin/bash
# Install auto-start for MonolithicCoffeeMakerAgent agents
#
# This script sets up agents to start automatically when your system boots.
# Supports: macOS (launchd), Linux (systemd)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM=$(uname -s)

echo "=== Installing Auto-Start for Agents ==="
echo "Platform: $PLATFORM"
echo "Project: $PROJECT_ROOT"
echo

case "$PLATFORM" in
    Darwin)
        echo "→ Installing macOS launchd service..."

        # Create launchd plist
        PLIST_FILE="$HOME/Library/LaunchAgents/com.coffemaker.agents.plist"

        cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.coffeemaker.agents</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_ROOT/scripts/start_agents.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>$HOME/.coffee_maker/agents.log</string>

    <key>StandardErrorPath</key>
    <string>$HOME/.coffee_maker/agents.error.log</string>

    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>
</dict>
</plist>
EOF

        echo "✓ Created launchd plist: $PLIST_FILE"

        # Load the service
        launchctl load "$PLIST_FILE" 2>/dev/null || true

        echo "✓ Loaded launchd service"
        echo
        echo "Commands:"
        echo "  • Start: launchctl start com.coffeemaker.agents"
        echo "  • Stop: launchctl stop com.coffeemaker.agents"
        echo "  • Uninstall: launchctl unload $PLIST_FILE && rm $PLIST_FILE"
        ;;

    Linux)
        echo "→ Installing systemd service..."

        # Create systemd service file
        SERVICE_FILE="$HOME/.config/systemd/user/coffeemaker-agents.service"
        mkdir -p "$(dirname "$SERVICE_FILE")"

        cat > "$SERVICE_FILE" << EOF
[Unit]
Description=MonolithicCoffeeMakerAgent Autonomous Agents
After=network.target

[Service]
Type=forking
ExecStart=$PROJECT_ROOT/scripts/start_agents.sh
ExecStop=$PROJECT_ROOT/scripts/stop_agents.sh
WorkingDirectory=$PROJECT_ROOT
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=default.target
EOF

        echo "✓ Created systemd service: $SERVICE_FILE"

        # Reload systemd and enable service
        systemctl --user daemon-reload
        systemctl --user enable coffeemaker-agents.service
        systemctl --user start coffeemaker-agents.service

        echo "✓ Enabled and started systemd service"
        echo
        echo "Commands:"
        echo "  • Start: systemctl --user start coffeemaker-agents"
        echo "  • Stop: systemctl --user stop coffeemaker-agents"
        echo "  • Status: systemctl --user status coffeemaker-agents"
        echo "  • Logs: journalctl --user -u coffeemaker-agents -f"
        echo "  • Uninstall: systemctl --user disable coffeemaker-agents && rm $SERVICE_FILE"
        ;;

    *)
        echo "✗ Unsupported platform: $PLATFORM"
        echo "Supported: macOS (Darwin), Linux"
        exit 1
        ;;
esac

echo
echo "=== Auto-Start Installed ==="
echo
echo "Agents will now start automatically on boot!"
echo "Current status:"
echo
$PROJECT_ROOT/scripts/agent_health_check.sh
