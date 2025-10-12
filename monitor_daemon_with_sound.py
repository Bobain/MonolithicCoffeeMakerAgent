#!/usr/bin/env python3
"""Monitor daemon progress and play sound on changes."""

import json
import time
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from coffee_maker.cli.notifications import NotificationDB


def monitor_daemon():
    """Monitor daemon and notify with sound on progress."""
    db = NotificationDB()
    status_file = Path("data/developer_status.json")

    last_progress = None
    last_step = None
    check_count = 0

    print("🔍 Démarrage surveillance daemon...")
    print("🔔 Son joué à chaque progression\n")

    while True:
        check_count += 1

        try:
            if not status_file.exists():
                print(f"[Check #{check_count}] ⚠️  Status file not found")
                time.sleep(10)
                continue

            with open(status_file) as f:
                data = json.load(f)

            task = data.get("current_task", {})
            progress = task.get("progress", 0)
            step = task.get("current_step", "Unknown")
            priority = task.get("name", "Unknown")

            # Display current status
            print(f"[Check #{check_count}] Progress: {progress}% | Step: {step}")

            # Detect changes
            if last_progress is None:
                # First check
                last_progress = progress
                last_step = step
                print(f"📊 Status initial: {priority} @ {progress}%\n")

            elif progress != last_progress or step != last_step:
                # Progress detected!
                print(f"\n🎉 PROGRESSION DÉTECTÉE!")
                print(f"   De: {last_progress}% ({last_step})")
                print(f"   À:  {progress}% ({step})\n")

                # Create notification with sound
                notif_id = db.create_notification(
                    type="daemon_progress",
                    title=f"🤖 Daemon Progress: {progress}%",
                    message=f"{priority}\n\n{step}",
                    priority="normal",
                    context={"progress": progress, "step": step, "previous_progress": last_progress},
                    play_sound=True,  # 🔔 PLAY SOUND!
                )

                print(f"🔔 Notification créée (ID: {notif_id}) avec son!")

                # Update tracking
                last_progress = progress
                last_step = step

                # Check for critical milestones
                if progress == 60:
                    print("⚠️  MILESTONE: Implementation complete, checking changes...")
                elif progress == 70:
                    print("🚨 CRITICAL: Committing changes (previous failure point!)")
                elif progress == 80:
                    print("✅ SUCCESS: Commit passed! Creating PR...")
                elif progress == 100:
                    print("🎉 COMPLETE: Priority finished!")
                    break

                print()

            # Check for errors
            last_activity = data.get("last_activity", {})
            if last_activity.get("type") == "error_encountered":
                error_desc = last_activity.get("description", "Unknown error")
                print(f"\n❌ ERROR DETECTED: {error_desc}")

                # Create error notification with sound
                db.create_notification(
                    type="daemon_error",
                    title="❌ Daemon Error",
                    message=error_desc,
                    priority="critical",
                    play_sound=True,
                )
                print("🔔 Error notification sent!\n")
                break

        except Exception as e:
            print(f"[Check #{check_count}] ⚠️  Error reading status: {e}")

        # Wait before next check
        time.sleep(30)


if __name__ == "__main__":
    try:
        monitor_daemon()
    except KeyboardInterrupt:
        print("\n\n👋 Surveillance arrêtée")
