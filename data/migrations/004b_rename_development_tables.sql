-- Migration 004b: Rename Tables in development.db
-- Created: 2025-10-28
-- SPEC: SPEC-115 - Database Table Renaming for Agent Ownership Clarity
-- Purpose: Rename tables specific to development.db
--
-- This is a companion migration to 004_rename_tables_agent_ownership.sql
-- Run this ONLY on development.db
--
-- ==============================================================================
-- IMPORTANT: Run this migration on development.db ONLY
-- ==============================================================================

BEGIN TRANSACTION;

-- ==============================================================================
-- Development Database Tables
-- ==============================================================================

-- command_token_usage → developer_token_usage
-- Issue: No agent prefix, unclear ownership
-- Table tracks token usage for developer commands (CFR-018 compliance)
ALTER TABLE command_token_usage RENAME TO developer_token_usage;

-- ==============================================================================
-- Update Views to Reference Renamed Table
-- ==============================================================================

-- Drop old views that reference command_token_usage
DROP VIEW IF EXISTS v_token_usage_by_command;
DROP VIEW IF EXISTS v_recent_token_usage;
DROP VIEW IF EXISTS v_token_budget_violations;

-- Recreate views with new table name
CREATE VIEW v_token_usage_by_command AS
SELECT
    agent_type,
    command_name,
    COUNT(*) as executions,
    AVG(estimated_input_tokens) as avg_estimated_input,
    AVG(actual_input_tokens) as avg_actual_input,
    AVG(actual_output_tokens) as avg_actual_output,
    AVG(total_tokens) as avg_total,
    AVG(duration_seconds) as avg_duration,
    AVG(estimate_accuracy_percent) as avg_accuracy,
    SUM(CASE WHEN within_budget = 0 THEN 1 ELSE 0 END) as over_budget_count,
    MAX(executed_at) as last_executed
FROM developer_token_usage
GROUP BY agent_type, command_name
ORDER BY avg_total DESC;

CREATE VIEW v_recent_token_usage AS
SELECT
    agent_type || '.' || command_name as command,
    executed_at,
    duration_seconds,
    estimated_input_tokens,
    actual_input_tokens,
    actual_output_tokens,
    total_tokens,
    usage_percent,
    estimate_accuracy_percent,
    CASE
        WHEN within_budget = 1 THEN '✅'
        ELSE '❌'
    END as status,
    task_id,
    success
FROM developer_token_usage
ORDER BY executed_at DESC
LIMIT 50;

CREATE VIEW v_token_budget_violations AS
SELECT
    agent_type,
    command_name,
    executed_at,
    estimated_input_tokens,
    budget_tokens,
    estimated_input_tokens - budget_tokens as tokens_over,
    usage_percent,
    task_id
FROM developer_token_usage
WHERE within_budget = 0
ORDER BY tokens_over DESC;

-- ==============================================================================
-- Record Migration
-- ==============================================================================

-- Record this migration
-- Use INSERT OR IGNORE to make migration idempotent
INSERT OR IGNORE INTO migrations (name) VALUES ('004b_rename_development_tables');

COMMIT;

-- ==============================================================================
-- Post-Migration Verification Queries
-- ==============================================================================

/*
-- Verify table renamed:
SELECT name FROM sqlite_master WHERE type='table' AND name='developer_token_usage';

-- Verify views recreated:
SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;

-- Count records (sanity check):
SELECT COUNT(*) as record_count FROM developer_token_usage;
*/

-- ==============================================================================
-- Rollback Instructions (Manual)
-- ==============================================================================

/*
-- If migration needs to be rolled back, run these commands:

BEGIN TRANSACTION;

-- Drop recreated views
DROP VIEW IF EXISTS v_token_usage_by_command;
DROP VIEW IF EXISTS v_recent_token_usage;
DROP VIEW IF EXISTS v_token_budget_violations;

-- Rename table back
ALTER TABLE developer_token_usage RENAME TO command_token_usage;

-- Recreate original views (from 003_token_tracking.sql)
CREATE VIEW v_token_usage_by_command AS
SELECT
    agent_type,
    command_name,
    COUNT(*) as executions,
    AVG(estimated_input_tokens) as avg_estimated_input,
    AVG(actual_input_tokens) as avg_actual_input,
    AVG(actual_output_tokens) as avg_actual_output,
    AVG(total_tokens) as avg_total,
    AVG(duration_seconds) as avg_duration,
    AVG(estimate_accuracy_percent) as avg_accuracy,
    SUM(CASE WHEN within_budget = 0 THEN 1 ELSE 0 END) as over_budget_count,
    MAX(executed_at) as last_executed
FROM command_token_usage
GROUP BY agent_type, command_name
ORDER BY avg_total DESC;

CREATE VIEW v_recent_token_usage AS
SELECT
    agent_type || '.' || command_name as command,
    executed_at,
    duration_seconds,
    estimated_input_tokens,
    actual_input_tokens,
    actual_output_tokens,
    total_tokens,
    usage_percent,
    estimate_accuracy_percent,
    CASE
        WHEN within_budget = 1 THEN '✅'
        ELSE '❌'
    END as status,
    task_id,
    success
FROM command_token_usage
ORDER BY executed_at DESC
LIMIT 50;

CREATE VIEW v_token_budget_violations AS
SELECT
    agent_type,
    command_name,
    executed_at,
    estimated_input_tokens,
    budget_tokens,
    estimated_input_tokens - budget_tokens as tokens_over,
    usage_percent,
    task_id
FROM command_token_usage
WHERE within_budget = 0
ORDER BY tokens_over DESC;

-- Remove migration record
DELETE FROM migrations WHERE name = '004b_rename_development_tables';

COMMIT;
*/
