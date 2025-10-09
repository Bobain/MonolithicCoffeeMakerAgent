#!/usr/bin/env python3
"""DEPRECATED: Use run_daemon.py instead.

This script has been deprecated in favor of run_daemon.py which includes
critical session detection to prevent the daemon from hanging when run
from within Claude Code sessions.

Please use:
    python run_daemon.py

instead of this script.
"""

import sys

print("=" * 70)
print("⚠️  DEPRECATED SCRIPT")
print("=" * 70)
print()
print("This script (run_dev_daemon.py) has been deprecated.")
print()
print("Please use 'run_daemon.py' instead, which includes:")
print("  - Critical Claude session detection")
print("  - Improved error handling")
print("  - Better logging and output")
print()
print("Usage:")
print("  python run_daemon.py              # Interactive mode")
print("  python run_daemon.py --auto-approve   # Auto-approve mode")
print("  python run_daemon.py --help        # Show help")
print()
print("=" * 70)
print()

response = input("Continue anyway? (NOT recommended) [y/N]: ").strip().lower()
if response not in ["y", "yes"]:
    print("\n✅ Good! Please use run_daemon.py instead.\n")
    sys.exit(0)

print("\n⚠️  Loading old script... (deprecated)\n")

# Load the actual implementation from run_daemon.py
import subprocess

result = subprocess.run([sys.executable, "run_daemon.py"] + sys.argv[1:])
sys.exit(result.returncode)
