#!/usr/bin/env python3
"""DEPRECATED: Use run_code_developer.py instead.

This script has been deprecated in favor of run_code_developer.py which includes
critical session detection to prevent the daemon from hanging when run
from within Claude Code sessions.

Please use:
    python run_code_developer.py

instead of this script.
"""

import sys

print("=" * 70)
print("⚠️  DEPRECATED SCRIPT")
print("=" * 70)
print()
print("This script (run_dev_daemon.py) has been deprecated.")
print()
print("Please use 'run_code_developer.py' instead, which includes:")
print("  - Critical Claude session detection")
print("  - Improved error handling")
print("  - Better logging and output")
print()
print("Usage:")
print("  python run_code_developer.py              # Interactive mode")
print("  python run_code_developer.py --auto-approve   # Auto-approve mode")
print("  python run_code_developer.py --help        # Show help")
print()
print("=" * 70)
print()

response = input("Continue anyway? (NOT recommended) [y/N]: ").strip().lower()
if response not in ["y", "yes"]:
    print("\n✅ Good! Please use run_code_developer.py instead.\n")
    sys.exit(0)

print("\n⚠️  Loading old script... (deprecated)\n")

# Load the actual implementation from run_code_developer.py
import subprocess

result = subprocess.run([sys.executable, "run_code_developer.py"] + sys.argv[1:])
sys.exit(result.returncode)
