# GUIDELINE-015: Database Migration Pattern

**Category**: Best Practice

**Applies To**: Database schema changes, Alembic migrations

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: None

---

## Overview

This guideline describes how to create and manage database migrations using Alembic, including when to create migrations, migration structure, testing, and rollback procedures.

---

## When to Use

Create a migration when:
- Adding new tables to the database
- Adding/removing columns from existing tables
- Changing column types or constraints
- Adding/removing indexes
- Modifying foreign key relationships
- Making any structural change to the database schema

---

## When NOT to Use

Do NOT create a migration for:
- Data fixes (use data migration scripts instead)
- Changing configuration (use environment variables)
- Modifying application logic (doesn't affect schema)
- Testing (use test fixtures instead)

---

## The Pattern

### Explanation

Database migrations track schema changes over time and enable rollback if needed. We use Alembic for this.

Key concepts:
1. **Migration Files**: One file per schema change, numbered sequentially
2. **Upgrade**: Function that applies the migration (forward)
3. **Downgrade**: Function that reverses the migration (backward)
4. **Revision History**: Alembic tracks applied migrations
5. **Testing**: Migrations tested for both upgrade and downgrade

### Principles

1. **One Change Per Migration**: Each migration does one logical thing
2. **Atomic Operations**: Migrations are all-or-nothing
3. **Reversible**: Every migration must have a downgrade path
4. **Idempotent**: Can safely re-run without side effects
5. **Backward Compatible**: Old code works with new schema (or vice versa)
6. **Tested**: Both upgrade and downgrade tested

---

## How to Implement

### Step 1: Generate Migration File

```bash
# Navigate to project directory
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent

# Generate a new migration
alembic revision --autogenerate -m "Add users table"

# Output:
# Creating /alembic/versions/abc123_add_users_table.py
```

### Step 2: Review Generated Migration

```python
# alembic/versions/abc123_add_users_table.py

"""Add users table

Revision ID: abc123
Revises: xyz789
Create Date: 2025-10-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'abc123'
down_revision = 'xyz789'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration (forward direction)."""
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )


def downgrade() -> None:
    """Reverse the migration (backward direction)."""
    op.drop_table('users')
```

### Step 3: Update Models if Needed

If auto-generation missed something, update the migration manually:

```python
def upgrade() -> None:
    """Apply the migration."""
    # Create table
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )

    # Create indexes for performance
    op.create_index(
        'ix_sessions_user_id',
        'sessions',
        ['user_id']
    )
    op.create_index(
        'ix_sessions_token',
        'sessions',
        ['token']
    )


def downgrade() -> None:
    """Reverse the migration."""
    op.drop_index('ix_sessions_token', table_name='sessions')
    op.drop_index('ix_sessions_user_id', table_name='sessions')
    op.drop_table('sessions')
```

### Step 4: Test Upgrade

```bash
# Apply the migration to development database
alembic upgrade head

# Verify the change
psql coffee_maker_dev -c "\dt users;"
# Output:
#          List of relations
#  Schema | Name | Type  | Owner
# --------+------+-------+-------
#  public | users | table | user

psql coffee_maker_dev -c "DESCRIBE users;"
# Output: Column list with id, email, password_hash, created_at, updated_at
```

### Step 5: Test Downgrade

```bash
# Rollback the migration
alembic downgrade -1

# Verify the table is gone
psql coffee_maker_dev -c "\dt users;"
# Output: No relation found

# Re-apply the migration
alembic upgrade head
```

### Step 6: Write Migration Test

```python
# tests/integration/test_migrations.py

import pytest
from sqlalchemy import inspect
from coffee_maker.db.database import get_db_connection

def test_migration_add_users_table():
    """Test users table creation migration."""
    # Apply migration
    from alembic.config import Config
    from alembic.command import upgrade
    config = Config("alembic.ini")
    upgrade(config, "head")

    # Verify table exists
    connection = get_db_connection()
    inspector = inspect(connection)
    tables = inspector.get_table_names()
    assert 'users' in tables

    # Verify columns
    columns = inspector.get_columns('users')
    column_names = [col['name'] for col in columns]
    assert 'id' in column_names
    assert 'email' in column_names
    assert 'password_hash' in column_names
    assert 'created_at' in column_names
    assert 'updated_at' in column_names

    # Verify constraints
    constraints = inspector.get_unique_constraints('users')
    constraint_names = [c['name'] for c in constraints]
    assert 'uq_users_email' in constraint_names


def test_migration_rollback():
    """Test that downgrade works correctly."""
    from alembic.config import Config
    from alembic.command import upgrade, downgrade
    config = Config("alembic.ini")

    # Start from clean state
    downgrade(config, "base")

    # Apply migration
    upgrade(config, "head")

    # Verify table exists
    connection = get_db_connection()
    inspector = inspect(connection)
    assert 'users' in inspector.get_table_names()

    # Rollback
    downgrade(config, "-1")

    # Verify table gone
    inspector = inspect(connection)
    assert 'users' not in inspector.get_table_names()
```

---

## Anti-Patterns to Avoid

❌ **Don't create multiple unrelated changes in one migration**
```python
# BAD: Multiple unrelated changes
def upgrade():
    op.create_table('users', ...)  # ❌ Creating users
    op.drop_table('legacy_users')  # ❌ Dropping legacy
    op.add_column('accounts', ...)  # ❌ Modifying accounts
```
**Better**: One change per migration
```python
# GOOD: Single logical change
def upgrade():
    op.create_table('users', ...)
```

❌ **Don't skip downgrade implementation**
```python
# BAD: No downgrade path
def downgrade():
    pass  # ❌ Can't rollback!
```
**Better**: Always provide downgrade
```python
def downgrade():
    op.drop_table('users')
```

❌ **Don't make long-running migrations**
```python
# BAD: Iterating over data in migration
def upgrade():
    connection = op.get_bind()
    for row in connection.execute("SELECT * FROM users"):
        # ❌ Modifying data in migration
        update_row(row)
```
**Better**: Use separate data migration script
```python
def upgrade():
    # Just schema change
    op.add_column('users', sa.Column('new_field', sa.String()))

# Then run: python scripts/migrate_user_data.py
```

❌ **Don't use raw SQL without context**
```python
# BAD: Raw SQL with no explanation
def upgrade():
    op.execute("ALTER TABLE users ADD COLUMN status VARCHAR(50)")
```
**Better**: Use SQLAlchemy with comments
```python
def upgrade():
    op.add_column('users', sa.Column(
        'status',
        sa.String(50),
        nullable=False,
        server_default='active',
        comment='User account status'
    ))
```

❌ **Don't skip testing migrations**
```python
# BAD: Commit migration without testing downgrade
# Migration works forward, but downgrade is untested
```
**Better**: Test both directions
```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test re-upgrade
alembic upgrade head
```

---

## Testing Approach

### Test Upgrade

```bash
# Apply migration
alembic upgrade +1

# Verify with psql
psql -d coffee_maker_dev -c "\dt"  # List tables
psql -d coffee_maker_dev -c "\d+ table_name"  # Show table details
```

### Test Downgrade

```bash
# Rollback
alembic downgrade -1

# Verify rollback worked
psql -d coffee_maker_dev -c "\dt"
```

### Test with Pytest

```bash
pytest tests/integration/test_migrations.py -v
```

---

## Related Guidelines

- [GUIDELINE-016: Testing Strategy](./GUIDELINE-016-testing-strategy.md)

---

## Examples in Codebase

- `alembic/versions/` (migration files)
- `coffee_maker/db/models.py` (SQLAlchemy models)

---

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Column Types](https://docs.sqlalchemy.org/en/14/core/types.html)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial database migration pattern guideline |
