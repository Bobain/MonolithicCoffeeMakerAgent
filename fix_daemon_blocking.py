#!/usr/bin/env python3
"""Quick fix for daemon blocking on missing specs.

The daemon currently loops infinitely on PRIORITY 25 because:
1. PRIORITY 25 has no spec
2. Daemon blocks, sends notification to architect
3. Sleeps 30s and loops back to PRIORITY 25 again
4. Never tries PRIORITY 26, 27, etc.

Solution: Add a helper method to get next AVAILABLE priority (skip blocked ones).
"""

from pathlib import Path

# Read the daemon code
daemon_file = Path("coffee_maker/autonomous/daemon.py")
content = daemon_file.read_text()

# Find the location where we need to add blocked priority tracking
init_location = content.find("self.specific_priority = specific_priority")

if init_location == -1:
    print("❌ Could not find __init__ location")
    exit(1)

# Add blocked priorities tracking to __init__
init_addition = """
        # Track priorities blocked waiting for specs (to skip them temporarily)
        self.blocked_priorities = set()  # Set of priority numbers blocked waiting for specs
        self.blocked_priority_check_time = {}  # Track when we last checked each blocked priority
"""

# Insert after self.specific_priority line
insertion_point = content.find("\n", init_location) + 1
new_content = content[:insertion_point] + init_addition + content[insertion_point:]

# Now find the location where we call get_next_planned_priority
get_next_location = new_content.find("next_priority = self.parser.get_next_planned_priority()")

if get_next_location == -1:
    print("❌ Could not find get_next_planned_priority call")
    exit(1)

# Replace with a loop that skips blocked priorities
replacement = """# Get next planned priority (skip blocked ones temporarily)
                    next_priority = None
                    attempts = 0
                    max_attempts = 10  # Try up to 10 priorities

                    while attempts < max_attempts:
                        candidate = self.parser.get_next_planned_priority()

                        if not candidate:
                            break  # No more planned priorities

                        # Check if this priority is in our blocked list
                        priority_num = candidate.get('number')
                        if priority_num and priority_num in self.blocked_priorities:
                            # Check if we should retry this priority (after 5 minutes)
                            import time
                            last_check = self.blocked_priority_check_time.get(priority_num, 0)
                            if time.time() - last_check > 300:  # 5 minutes
                                # Try again - maybe architect created the spec
                                self.blocked_priorities.remove(priority_num)
                                del self.blocked_priority_check_time[priority_num]
                                next_priority = candidate
                                break
                            else:
                                # Still blocked, mark this priority as '⏸️ Blocked' temporarily
                                # and try to get the next priority
                                logger.info(f"⏸️  PRIORITY {priority_num} still blocked (waiting for spec), trying next priority...")

                                # HACK: Temporarily mark it as in-progress to skip it
                                # This is not ideal but works for MVP
                                # TODO: Implement proper priority skipping in RoadmapParser
                                attempts += 1
                                continue  # Try next priority
                        else:
                            # Not blocked, use this priority
                            next_priority = candidate
                            break

                    if not next_priority and attempts >= max_attempts:
                        logger.warning(f"⚠️  Tried {max_attempts} priorities, all blocked waiting for specs")
                        logger.warning("⚠️  Entering idle state - waiting for architect to create specs")
                        self.status.update_status(DeveloperState.IDLE, current_step="All priorities blocked")
                        time.sleep(300)  # Wait 5 minutes before trying again
                        continue"""

# This is getting complex. Let me instead create a simpler patch.
# The issue is that RoadmapParser needs to be updated to skip priorities.

print("=" * 60)
print("ANALYSIS: The fix requires modifying RoadmapParser")
print("=" * 60)
print()
print("Current issue:")
print("- get_next_planned_priority() always returns PRIORITY 25")
print("- daemon blocks, sleeps, loops back to PRIORITY 25")
print()
print("Solution needed:")
print("1. Update RoadmapParser.get_next_planned_priority() to accept skip_list")
print("2. Daemon tracks blocked priorities in a set")
print("3. Pass blocked set to get_next_planned_priority(skip=blocked_set)")
print("4. Parser skips priorities in the skip list")
print()
print("Alternative quick fix:")
print("- Manually change PRIORITY 25 status to '⏸️ Blocked' in ROADMAP.md")
print("- Then get_next_planned_priority() will skip it and return PRIORITY 26")
print()
print("Let me implement the manual fix first...")
