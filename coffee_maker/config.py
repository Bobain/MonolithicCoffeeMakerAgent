"""
Coffee Maker Agent - Global Configuration

This module contains global configuration constants used throughout the project.

⚠️ CRITICAL PATHS - DO NOT MODIFY THESE WITHOUT UNDERSTANDING IMPACT
"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# ============================================================================
# ROADMAP CONFIGURATION - SINGLE SOURCE OF TRUTH
# ============================================================================

# THE ONE AND ONLY ROADMAP FILE
# This path is used by:
# - Autonomous Daemon (reads and implements features)
# - Project Manager CLI (reads and updates status)
# - All automated tools and scripts
#
# ⚠️ NEVER create alternative roadmap files!
# ⚠️ NEVER change this path!
# ⚠️ ALWAYS use this constant when accessing the roadmap!
ROADMAP_PATH = PROJECT_ROOT / "docs" / "ROADMAP.md"

# File lock for concurrent roadmap access
# Both daemon and project manager use this lock to prevent conflicts
ROADMAP_LOCK_PATH = "/tmp/roadmap.lock"

# Validate that roadmap exists
if not ROADMAP_PATH.exists():
    raise FileNotFoundError(
        f"ROADMAP.md not found at {ROADMAP_PATH}. "
        f"This is the SINGLE SOURCE OF TRUTH for the project. "
        f"Never create alternative roadmap files!"
    )

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Shared data directory (used by both user and daemon)
# All databases MUST be stored here for proper synchronization
DATA_DIR = PROJECT_ROOT / "data"

# Database paths (shared between user environment and daemon)
DATABASE_PATHS = {
    "analytics": DATA_DIR / "analytics.db",
    "notifications": DATA_DIR / "notifications.db",
    "langfuse_export": DATA_DIR / "langfuse_export.db",
}

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# ============================================================================
# DOCUMENTATION CONFIGURATION
# ============================================================================

# Documentation directory
DOCS_DIR = PROJECT_ROOT / "docs"

# Documentation organization guide
DOCS_README = DOCS_DIR / "README_DOCS.md"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log directory
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Default log file
DEFAULT_LOG_FILE = LOG_DIR / "coffee_maker.log"

# ============================================================================
# DEVELOPMENT CONFIGURATION
# ============================================================================

# Test directory
TEST_DIR = PROJECT_ROOT / "tests"

# Scripts directory
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================


def validate_single_roadmap() -> None:
    """Validate that only ONE roadmap file exists.

    Raises:
        RuntimeError: If multiple roadmap files are detected

    This function ensures that no alternative roadmap files have been created.
    It's called during import to catch issues early.

    Allowed roadmap-related files:
    - ROADMAP.md (the single source of truth)
    - ROADMAP_OVERVIEW.md (high-level summary documentation)
    """

    # Search for any file with "roadmap" in the name (case insensitive)
    roadmap_files = list(DOCS_DIR.glob("*[Rr][Oo][Aa][Dd][Mm][Aa][Pp]*.md"))

    # Whitelist of allowed roadmap-related files
    allowed_roadmap_files = {
        ROADMAP_PATH,  # The single source of truth
        DOCS_DIR / "ROADMAP_OVERVIEW.md",  # High-level summary documentation
    }

    # Filter out allowed files
    unofficial_roadmaps = [f for f in roadmap_files if f not in allowed_roadmap_files]

    if unofficial_roadmaps:
        files_list = "\n".join(f"  - {f.relative_to(PROJECT_ROOT)}" for f in unofficial_roadmaps)
        raise RuntimeError(
            f"ERROR: Unauthorized roadmap files detected!\n\n"
            f"Only these files are allowed:\n"
            f"  - docs/ROADMAP.md (source of truth)\n"
            f"  - docs/ROADMAP_OVERVIEW.md (summary documentation)\n\n"
            f"Found unauthorized roadmap files:\n{files_list}\n\n"
            f"Please delete these files and use only the official files.\n"
            f"See docs/README_DOCS.md for documentation guidelines."
        )


def validate_database_paths() -> None:
    """Validate that all database paths use the shared DATA_DIR.

    This ensures proper synchronization between user and daemon environments.
    """
    for db_name, db_path in DATABASE_PATHS.items():
        if not str(db_path).startswith(str(DATA_DIR)):
            raise RuntimeError(
                f"ERROR: Database '{db_name}' is not in shared DATA_DIR!\n"
                f"Path: {db_path}\n"
                f"Expected: {DATA_DIR}/...\n\n"
                f"All databases must be in DATA_DIR for proper daemon synchronization.\n"
                f"See docs/PRIORITY_1.5_DATABASE_SYNC_DESIGN.md for details."
            )


# ============================================================================
# RUN VALIDATIONS ON IMPORT
# ============================================================================

# Validate single roadmap (catches issues early)
validate_single_roadmap()

# Validate database paths (ensures proper sync)
validate_database_paths()

# ============================================================================
# EXPORT PUBLIC API
# ============================================================================

__all__ = [
    # Roadmap
    "ROADMAP_PATH",
    "ROADMAP_LOCK_PATH",
    # Databases
    "DATA_DIR",
    "DATABASE_PATHS",
    # Directories
    "PROJECT_ROOT",
    "DOCS_DIR",
    "LOG_DIR",
    "TEST_DIR",
    "SCRIPTS_DIR",
    # Validation
    "validate_single_roadmap",
    "validate_database_paths",
]
