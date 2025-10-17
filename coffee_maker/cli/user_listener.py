"""User Listener CLI - Primary user interface for MonolithicCoffeeMakerAgent.

This module provides the standalone `poetry run user-listener` command that serves
as the PRIMARY USER INTERFACE for the MonolithicCoffeeMakerAgent system.

SPEC-010: User-Listener UI Command (SIMPLIFIED)
- Reuses 100% of ChatSession infrastructure from project-manager chat
- Enforces singleton pattern via AgentRegistry
- Minimal code: ~250 lines, mostly copy-paste from roadmap_cli.py

Architecture:
    User runs: poetry run user-listener
       ↓
    user_listener.py main()
       ↓
    Register as USER_LISTENER (singleton)
       ↓
    Create ChatSession (REUSED from project_manager)
       ↓
    Start chat loop

Key Features:
    - Interactive REPL for user input
    - Rich terminal output with markdown and syntax highlighting
    - Singleton enforcement (only one instance at a time)
    - Same functionality as project-manager chat
    - All existing commands work (/add, /update, /view, /analyze, etc.)

References:
    - SPEC-010: User-Listener UI Command
    - ADR-003: Simplification-First Approach
    - roadmap_cli.py: Source for cmd_chat() function (REUSED)
"""

import logging
import os
import shutil
import sys

from coffee_maker.autonomous.agent_registry import (
    AgentAlreadyRunningError,
    AgentRegistry,
    AgentType,
)
from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.chat_interface import ChatSession
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.config import ROADMAP_PATH, ConfigManager

# Configure logging BEFORE imports that might fail
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for user-listener CLI.

    Command: poetry run user-listener

    This function:
    1. Registers as USER_LISTENER singleton
    2. Sets up ChatSession with AI service
    3. Starts interactive REPL loop
    4. Handles errors gracefully

    Returns:
        0 on success, 1 on error

    SPEC-010 Implementation:
        - Copy cmd_chat() logic from roadmap_cli.py
        - Add singleton registration (AgentType.USER_LISTENER)
        - Update welcome banner ("User Listener · Primary Interface")
        - Reuse all ChatSession infrastructure
    """

    try:
        # US-035: Register user_listener in singleton registry
        with AgentRegistry.register(AgentType.USER_LISTENER):
            logger.info("✅ user_listener registered in singleton registry")

            # Check if we're ALREADY running inside Claude CLI (Claude Code)
            # If so, we MUST use API mode to avoid nesting
            inside_claude_cli = bool(os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"))

            if inside_claude_cli:
                logger.info("Detected running inside Claude Code - forcing API mode to avoid nesting")

            # Auto-detect mode: CLI vs API (same logic as daemon)
            claude_path = "/opt/homebrew/bin/claude"
            has_cli = shutil.which("claude") or os.path.exists(claude_path)
            has_api_key = ConfigManager.has_anthropic_api_key()

            use_claude_cli = False

            if inside_claude_cli:
                # We're already in Claude CLI - MUST use API to avoid nesting
                if has_api_key:
                    print("=" * 70)
                    print("ℹ️  Detected: Running inside Claude Code")
                    print("=" * 70)
                    print("🔄 Using Anthropic API to avoid CLI nesting")
                    print("💡 TIP: CLI nesting is not recommended")
                    print("=" * 70 + "\n")
                    use_claude_cli = False
                else:
                    # No API key - can't proceed
                    print("=" * 70)
                    print("❌ ERROR: Running inside Claude Code without API key")
                    print("=" * 70)
                    print("\nYou're running user-listener from within Claude Code.")
                    print("To avoid CLI nesting, we need to use API mode.")
                    print("\n🔧 SOLUTION:")
                    print("  1. Get your API key from: https://console.anthropic.com/")
                    print("  2. Set the environment variable:")
                    print("     export ANTHROPIC_API_KEY='your-api-key-here'")
                    print("  3. Or add it to your .env file")
                    print("\n💡 ALTERNATIVE: Run from a regular terminal (not Claude Code)")
                    print("=" * 70 + "\n")
                    return 1
            elif has_cli:
                # CLI available - use it as default (free with subscription!)
                print("=" * 70)
                print("ℹ️  Auto-detected: Using Claude CLI (default)")
                print("=" * 70)
                print("💡 TIP: Claude CLI is free with your subscription!")
                print("=" * 70 + "\n")
                use_claude_cli = True
            elif has_api_key:
                # No CLI but has API key - use API
                print("=" * 70)
                print("ℹ️  Auto-detected: Using Anthropic API (no CLI found)")
                print("=" * 70)
                print("💡 TIP: Install Claude CLI for free usage!")
                print("    Get it from: https://claude.ai/")
                print("=" * 70 + "\n")
                use_claude_cli = False
            else:
                # Neither available - error
                print("=" * 70)
                print("❌ ERROR: No Claude access available!")
                print("=" * 70)
                print("\nThe chat requires either:")
                print("  1. Claude CLI installed (recommended - free with subscription), OR")
                print("  2. Anthropic API key (requires credits)")
                print("\n🔧 SOLUTION 1 (CLI Mode - Recommended):")
                print("  1. Install Claude CLI from: https://claude.ai/")
                print("  2. Run: poetry run user-listener")
                print("\n🔧 SOLUTION 2 (API Mode):")
                print("  1. Get your API key from: https://console.anthropic.com/")
                print("  2. Set the environment variable:")
                print("     export ANTHROPIC_API_KEY='your-api-key-here'")
                print("  3. Run: poetry run user-listener")
                print("\n" + "=" * 70 + "\n")
                return 1

            # Initialize components (REUSED from project-manager chat)
            editor = RoadmapEditor(ROADMAP_PATH)
            ai_service = AIService(use_claude_cli=use_claude_cli, claude_cli_path=claude_path)

            # Check AI service availability
            if not ai_service.check_available():
                print("❌ AI service not available")
                print("\nPlease check:")
                if use_claude_cli:
                    print("  - Claude CLI is installed and working")
                else:
                    print("  - ANTHROPIC_API_KEY is valid")
                print("  - Internet connection is active")
                return 1

            # Display welcome banner (SPEC-010: Update to identify as user_listener)
            print("\n" + "=" * 70)
            print("User Listener · Primary Interface")
            print("=" * 70)
            print("Powered by Claude AI\n")

            # Start chat session (REUSED from project-manager chat)
            session = ChatSession(ai_service, editor)
            session.start()

            return 0

    except AgentAlreadyRunningError as e:
        print(f"\n❌ Error: {e}\n")
        return 1

    except KeyboardInterrupt:
        print("\n\nGoodbye!\n")
        return 0

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        if "ANTHROPIC_API_KEY" in str(e):
            print("\n💡 TIP: Install Claude CLI for free usage (no API key needed)!")
            print("   Get it from: https://claude.ai/")
        return 1

    except Exception as e:
        logger.error(f"Chat session failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
