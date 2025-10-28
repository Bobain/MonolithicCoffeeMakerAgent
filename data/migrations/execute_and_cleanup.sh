#!/bin/bash
# Master Migration Script
# 1. Consolidates databases into ONE (roadmap.db)
# 2. Renames tables for agent ownership clarity
# 3. Deletes ALL migration scripts including itself
#
# RUN ONCE AND FORGET

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================================================"
echo "MASTER MIGRATION: Consolidate + Rename + Cleanup"
echo "================================================================================"
echo ""

# ============================================================================
# PHASE 1: Consolidate databases
# ============================================================================

echo "PHASE 1: Database Consolidation"
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""

# Check if consolidation already done
if [ ! -f "$DATA_DIR/development.db" ] && [ ! -f "$DATA_DIR/notifications.db" ]; then
    echo "✓ Already consolidated (development.db and notifications.db don't exist)"
else
    echo "Running consolidation..."
    "$SCRIPT_DIR/run_consolidation.sh"
fi

echo ""

# ============================================================================
# PHASE 2: Rename tables
# ============================================================================

echo "PHASE 2: Table Renaming (SPEC-115)"
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""

# Check if already renamed (check for new table name)
TABLE_CHECK=$(sqlite3 "$DATA_DIR/roadmap.db" "SELECT name FROM sqlite_master WHERE type='table' AND name='developer_commit';" || echo "")

if [ -n "$TABLE_CHECK" ]; then
    echo "✓ Already renamed (developer_commit table exists)"
else
    echo "Running table renaming..."
    sqlite3 "$DATA_DIR/roadmap.db" < "$SCRIPT_DIR/rename_tables.sql"
    echo "✓ 20 tables renamed successfully"
fi

echo ""

# ============================================================================
# PHASE 3: Cleanup - DELETE ALL MIGRATION SCRIPTS
# ============================================================================

echo "PHASE 3: Cleanup"
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""

echo "Deleting all migration scripts..."

# Count files before deletion
FILE_COUNT=$(ls -1 "$SCRIPT_DIR"/*.sql "$SCRIPT_DIR"/*.sh "$SCRIPT_DIR"/*.md 2>/dev/null | wc -l || echo 0)

if [ "$FILE_COUNT" -gt 0 ]; then
    rm -f "$SCRIPT_DIR"/*.sql
    rm -f "$SCRIPT_DIR"/*.sh
    rm -f "$SCRIPT_DIR"/*.md
    rm -f "$SCRIPT_DIR"/README*

    echo "✓ Deleted $FILE_COUNT migration files (including this script)"
else
    echo "✓ No migration files to delete"
fi

echo ""

# ============================================================================
# SUCCESS
# ============================================================================

echo "================================================================================"
echo "✅ MIGRATION COMPLETE"
echo "================================================================================"
echo ""
echo "Results:"
echo "  • ONE database: data/roadmap.db"
echo "  • 20 tables renamed with agent-based prefixes"
echo "  • All migration scripts deleted"
echo ""
echo "Next steps:"
echo "  1. Update Python code to use new table names (TASK-115-3)"
echo "  2. Update documentation (TASK-115-4)"
echo "  3. Run tests (TASK-115-6)"
echo ""
