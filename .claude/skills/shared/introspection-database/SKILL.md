---
name: database-schema-guide
version: 1.0.0
agent: shared
scope: shared
description: Database schema awareness skill that provides instant access to database table information, usage patterns, and prevents architectural mistakes
triggers:
  - "implementing database features"
  - "creating new tables"
  - "writing migration scripts"
  - "uncertain about file vs database storage"
requires: []
---

# Database Schema Guide Skill

This skill provides instant access to database schema information and usage patterns to prevent architectural mistakes.

## Purpose

Prevents errors like:
- Creating files when data should be stored in database
- Bypassing database columns and using filesystem
- Misunderstanding table purposes

## Usage

```python
from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

# Load the skill
skill = load_skill(SkillNames.INTROSPECTION_DATABASE)

# Check if should use files for a table
result = skill.execute(action="should_use_files", table="technical_specs")
# Returns: {"result": False, "reason": "Store content in database, not files"}

# Get table information
info = skill.execute(action="get_table_info", table="technical_specs")
# Returns table purpose, content column, usage info

# Get usage examples
example = skill.execute(action="get_example", table="technical_specs", spec_type="hierarchical")
# Returns code examples for correct usage

# List all documented tables
tables = skill.execute(action="list_tables")
# Returns: ["technical_specs", "implementation_tasks"]
```

## Available Actions

1. **get_table_info** - Get table purpose and metadata
   - Parameters: `table` (required)
   - Returns: Dict with purpose, content_column, content_type, use_files, related_tables

2. **should_use_files** - Check if files should be used for a table
   - Parameters: `table` (required)
   - Returns: Dict with result (bool), reason, content_column

3. **get_example** - Get usage examples for a table
   - Parameters: `table` (required), `spec_type` (optional)
   - Returns: Dict with code examples and description

4. **list_tables** - Get all documented tables
   - Parameters: None
   - Returns: List of table names

## When to Use

- ✅ **BEFORE** creating any new database table
- ✅ **BEFORE** adding features that interact with existing tables
- ✅ **BEFORE** writing migration scripts
- ✅ **WHEN** uncertain whether to use files vs database

## Error Prevention

This skill was created to prevent the error where technical specs were implemented as files when they should have been stored entirely in the database (technical_specs.content column).

## See Also

- Database Introspection: This skill provides dynamic introspection
- Database Schema Skill: `database_schema_skill.py` (implementation)
