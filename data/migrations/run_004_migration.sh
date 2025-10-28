#!/bin/bash
# Migration 004 - Automated Execution Script
# SPEC: SPEC-115
# Run all three migration scripts and verify results

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent"
DATA_DIR="$PROJECT_ROOT/data"
MIGRATIONS_DIR="$DATA_DIR/migrations"

echo "=========================================="
echo "Migration 004: Database Table Renaming"
echo "SPEC: SPEC-115"
echo "=========================================="
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if databases exist
echo "Step 1: Checking databases..."
if [ ! -f "$DATA_DIR/roadmap.db" ]; then
    print_error "roadmap.db not found!"
    exit 1
fi
if [ ! -f "$DATA_DIR/development.db" ]; then
    print_error "development.db not found!"
    exit 1
fi
if [ ! -f "$DATA_DIR/notifications.db" ]; then
    print_error "notifications.db not found!"
    exit 1
fi
print_success "All databases found"
echo ""

# Create backups
echo "Step 2: Creating backups..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp "$DATA_DIR/roadmap.db" "$DATA_DIR/roadmap.db.backup_$TIMESTAMP"
cp "$DATA_DIR/development.db" "$DATA_DIR/development.db.backup_$TIMESTAMP"
cp "$DATA_DIR/notifications.db" "$DATA_DIR/notifications.db.backup_$TIMESTAMP"
print_success "Backups created with timestamp: $TIMESTAMP"
echo ""

# Check for running agents
echo "Step 3: Checking for running agents..."
RUNNING_AGENTS=$(ps aux | grep "poetry run" | grep -v grep | wc -l)
if [ $RUNNING_AGENTS -gt 0 ]; then
    print_warning "Found $RUNNING_AGENTS running agent(s)"
    echo "Running agents:"
    ps aux | grep "poetry run" | grep -v grep
    echo ""
    read -p "Stop agents and continue? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "poetry run" || true
        sleep 2
        print_success "Agents stopped"
    else
        print_error "Migration cancelled"
        exit 1
    fi
else
    print_success "No running agents detected"
fi
echo ""

# Run migrations
echo "Step 4: Running migrations..."
echo ""

# Migration 1: roadmap.db
echo "4a. Migrating roadmap.db..."
if sqlite3 "$DATA_DIR/roadmap.db" < "$MIGRATIONS_DIR/004_rename_tables_agent_ownership.sql" 2>&1; then
    print_success "roadmap.db migration complete"
else
    print_error "roadmap.db migration failed!"
    exit 1
fi
echo ""

# Migration 2: development.db
echo "4b. Migrating development.db..."
if sqlite3 "$DATA_DIR/development.db" < "$MIGRATIONS_DIR/004b_rename_development_tables.sql" 2>&1; then
    print_success "development.db migration complete"
else
    print_error "development.db migration failed!"
    exit 1
fi
echo ""

# Migration 3: notifications.db
echo "4c. Migrating notifications.db..."
if sqlite3 "$DATA_DIR/notifications.db" < "$MIGRATIONS_DIR/004c_rename_notifications_tables.sql" 2>&1; then
    print_success "notifications.db migration complete"
else
    print_error "notifications.db migration failed!"
    exit 1
fi
echo ""

# Verify migrations
echo "Step 5: Verifying migrations..."
echo ""

# Check roadmap.db
echo "5a. Verifying roadmap.db..."
EXPECTED_TABLES=(
    "developer_commit"
    "orchestrator_agent_lifecycle"
    "shared_notifications"
    "architect_schema_metadata"
    "shared_notification_user"
    "shared_notification_state"
    "shared_audit"
    "assistant_bug_reports"
    "assistant_demo_sessions"
    "assistant_delegation_log"
    "ux_component_library"
    "ux_design_debt"
    "ux_design_specs"
    "ux_design_tokens"
    "listener_conversation_context"
    "listener_intent_classification"
    "listener_routing_log"
    "shared_agent_message"
    "manager_metrics_subtask"
)

MISSING_TABLES=0
for table in "${EXPECTED_TABLES[@]}"; do
    if sqlite3 "$DATA_DIR/roadmap.db" "SELECT name FROM sqlite_master WHERE type='table' AND name='$table';" | grep -q "$table"; then
        echo "  ✓ $table exists"
    else
        print_error "  Table $table not found!"
        MISSING_TABLES=$((MISSING_TABLES + 1))
    fi
done

if [ $MISSING_TABLES -eq 0 ]; then
    print_success "All 19 tables renamed in roadmap.db"
else
    print_error "$MISSING_TABLES table(s) missing in roadmap.db!"
    exit 1
fi
echo ""

# Check development.db
echo "5b. Verifying development.db..."
if sqlite3 "$DATA_DIR/development.db" "SELECT name FROM sqlite_master WHERE type='table' AND name='developer_token_usage';" | grep -q "developer_token_usage"; then
    print_success "developer_token_usage table exists"
else
    print_error "developer_token_usage table not found!"
    exit 1
fi
echo ""

# Check notifications.db
echo "5c. Verifying notifications.db..."
if sqlite3 "$DATA_DIR/notifications.db" "SELECT name FROM sqlite_master WHERE type='table' AND name='shared_notifications';" | grep -q "shared_notifications"; then
    print_success "shared_notifications table exists"
else
    print_error "shared_notifications table not found!"
    exit 1
fi
echo ""

# Check foreign keys
echo "Step 6: Checking foreign key integrity..."
FK_ERRORS=$(sqlite3 "$DATA_DIR/roadmap.db" "PRAGMA foreign_key_check;" | wc -l)
if [ $FK_ERRORS -eq 0 ]; then
    print_success "No foreign key violations"
else
    print_warning "$FK_ERRORS foreign key violation(s) found"
    sqlite3 "$DATA_DIR/roadmap.db" "PRAGMA foreign_key_check;"
fi
echo ""

# Check migration records
echo "Step 7: Verifying migration records..."
ROADMAP_MIGRATION=$(sqlite3 "$DATA_DIR/roadmap.db" "SELECT name FROM migrations WHERE name='004_rename_tables_agent_ownership';" | wc -l)
DEV_MIGRATION=$(sqlite3 "$DATA_DIR/development.db" "SELECT name FROM migrations WHERE name='004b_rename_development_tables';" | wc -l)
NOTIF_MIGRATION=$(sqlite3 "$DATA_DIR/notifications.db" "SELECT name FROM migrations WHERE name='004c_rename_notifications_tables';" | wc -l)

if [ $ROADMAP_MIGRATION -eq 1 ] && [ $DEV_MIGRATION -eq 1 ] && [ $NOTIF_MIGRATION -eq 1 ]; then
    print_success "All migration records created"
else
    print_error "Migration records incomplete!"
    exit 1
fi
echo ""

# Summary
echo "=========================================="
echo "Migration 004 Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - roadmap.db: 19 tables renamed ✅"
echo "  - development.db: 1 table + 3 views updated ✅"
echo "  - notifications.db: 1 table renamed ✅"
echo "  - Backups: $DATA_DIR/*.backup_$TIMESTAMP ✅"
echo ""
echo "Next steps:"
echo "  1. Update Python code to use new table names (TASK-115-3)"
echo "  2. Run tests: pytest"
echo "  3. Update documentation (TASK-115-4)"
echo ""
print_success "Migration successful!"
