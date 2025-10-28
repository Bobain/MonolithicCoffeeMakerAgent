#!/bin/bash
# Database Consolidation Script
# Consolidates all databases into ONE: roadmap.db
# Then deletes separate databases and all migration scripts
#
# Run once, deletes itself

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================================================"
echo "DATABASE CONSOLIDATION - ONE DATABASE TO RULE THEM ALL"
echo "================================================================================"
echo ""
echo "Target: roadmap.db (single source of truth)"
echo "Removing: development.db, notifications.db"
echo "Cleaning: All migration scripts"
echo ""

# ============================================================================
# STEP 1: Backup existing databases
# ============================================================================

echo "Step 1: Creating backups..."
BACKUP_DIR="$DATA_DIR/backups/pre-consolidation-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "$DATA_DIR/roadmap.db" ]; then
    cp "$DATA_DIR/roadmap.db" "$BACKUP_DIR/"
    echo "  ✓ Backed up roadmap.db"
fi

if [ -f "$DATA_DIR/development.db" ]; then
    cp "$DATA_DIR/development.db" "$BACKUP_DIR/"
    echo "  ✓ Backed up development.db"
fi

if [ -f "$DATA_DIR/notifications.db" ]; then
    cp "$DATA_DIR/notifications.db" "$BACKUP_DIR/"
    echo "  ✓ Backed up notifications.db"
fi

echo ""

# ============================================================================
# STEP 2: Merge notifications from notifications.db into roadmap.db
# ============================================================================

echo "Step 2: Merging notifications data..."

if [ -f "$DATA_DIR/notifications.db" ]; then
    # Attach notifications.db and merge data
    sqlite3 "$DATA_DIR/roadmap.db" <<SQL
ATTACH DATABASE '$DATA_DIR/notifications.db' AS notif_db;

-- Merge notifications (avoid duplicates by checking created_at + message)
INSERT OR IGNORE INTO notifications (
    target_agent, source_agent, notification_type,
    item_id, message, status, created_at,
    processed_at, processed_by, notes
)
SELECT
    target_agent, source_agent, notification_type,
    item_id, message, status, created_at,
    processed_at, processed_by, notes
FROM notif_db.notifications;

DETACH DATABASE notif_db;

SELECT '  ✓ Merged ' || changes() || ' notifications' as result;
SQL
fi

echo ""

# ============================================================================
# STEP 3: Run consolidation SQL script
# ============================================================================

echo "Step 3: Running consolidation SQL..."
sqlite3 "$DATA_DIR/roadmap.db" < "$SCRIPT_DIR/000_consolidate_databases.sql"
echo "  ✓ command_token_usage table added"
echo "  ✓ migrations table removed"
echo ""

# ============================================================================
# STEP 4: Delete separate databases
# ============================================================================

echo "Step 4: Deleting separate databases..."

if [ -f "$DATA_DIR/development.db" ]; then
    rm "$DATA_DIR/development.db"
    echo "  ✓ Deleted development.db"
fi

if [ -f "$DATA_DIR/notifications.db" ]; then
    rm "$DATA_DIR/notifications.db"
    echo "  ✓ Deleted notifications.db"
fi

echo ""

# ============================================================================
# STEP 5: Delete all migration scripts (including this one)
# ============================================================================

echo "Step 5: Cleaning up migration scripts..."

# Delete all migration SQL and shell scripts
rm -f "$SCRIPT_DIR"/*.sql
rm -f "$SCRIPT_DIR"/*.sh
rm -f "$SCRIPT_DIR"/*.md
rm -f "$SCRIPT_DIR"/README*

echo "  ✓ Deleted all migration scripts"
echo ""

# ============================================================================
# SUCCESS
# ============================================================================

echo "================================================================================"
echo "✅ CONSOLIDATION COMPLETE"
echo "================================================================================"
echo ""
echo "Result:"
echo "  • ONE database: data/roadmap.db"
echo "  • Contains ALL tables (including command_token_usage)"
echo "  • No migrations table (migrations are one-time scripts)"
echo "  • No separate development.db or notifications.db"
echo "  • All migration scripts deleted (including this one)"
echo ""
echo "Backups saved to: $BACKUP_DIR"
echo ""
echo "Next: Run SPEC-115 table renaming migration"
echo ""
