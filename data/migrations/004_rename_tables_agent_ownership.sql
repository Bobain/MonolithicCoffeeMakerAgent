-- Migration 004: Rename Tables for Agent Ownership Clarity
-- Created: 2025-10-28
-- SPEC: SPEC-115 - Database Table Renaming for Agent Ownership Clarity
-- Purpose: Rename 20 tables with proper agent-based prefixes for improved clarity
--
-- SIMPLIFIED APPROACH: Direct rename without backward compatibility views
-- All code must be updated immediately after running this migration
--
-- ==============================================================================
-- IMPORTANT: This migration modifies table names across multiple databases
-- Run on ALL databases: roadmap.db, development.db, notifications.db
-- ==============================================================================

BEGIN TRANSACTION;

-- ==============================================================================
-- Category 1: Misleading Prefix (1 table)
-- ==============================================================================

-- review_commit → developer_commit
-- Issue: 'review_' prefix implies code_reviewer ownership, but code_developer owns it
-- Table stores commits made by code_developer agent, not review data
ALTER TABLE review_commit RENAME TO developer_commit;

-- ==============================================================================
-- Category 2: Missing Prefix (3 tables)
-- ==============================================================================

-- command_token_usage → developer_token_usage
-- Issue: No agent prefix, unclear ownership
-- Table tracks token usage for developer commands (CFR-018 compliance)
-- NOTE: Only in development.db - see 004b_rename_development_tables.sql
-- (Commented out for roadmap.db)

-- agent_lifecycle → orchestrator_agent_lifecycle
-- Issue: Generic 'agent_' prefix, should match orchestrator_* pattern
-- Table tracks agent spawning/shutdown lifecycle managed by orchestrator
ALTER TABLE agent_lifecycle RENAME TO orchestrator_agent_lifecycle;

-- notifications → shared_notifications
-- Issue: No prefix indicating cross-agent usage
-- Table used for inter-agent messaging and coordination
ALTER TABLE notifications RENAME TO shared_notifications;

-- ==============================================================================
-- Category 3: Generic/Vague Prefix (4 tables)
-- ==============================================================================

-- system_schema_metadata → architect_schema_metadata
-- Issue: 'system_' too generic, architect owns schema documentation
-- Table stores database schema metadata maintained by architect
ALTER TABLE system_schema_metadata RENAME TO architect_schema_metadata;

-- notification_user → shared_notification_user
-- Issue: Should be explicitly marked as shared infrastructure
-- Table stores user notification preferences (cross-agent)
ALTER TABLE notification_user RENAME TO shared_notification_user;

-- notification_system_state → shared_notification_state
-- Issue: Should be explicitly marked as shared infrastructure
-- Table stores notification system state (cross-agent)
ALTER TABLE notification_system_state RENAME TO shared_notification_state;

-- system_audit → shared_audit
-- Issue: 'system_' too generic, this is shared audit infrastructure
-- Table stores audit logs from all agents
ALTER TABLE system_audit RENAME TO shared_audit;

-- ==============================================================================
-- Category 4: Wrong Prefix - Assistant Tables (3 tables)
-- ==============================================================================

-- ui_bug_reports → assistant_bug_reports
-- Issue: 'ui_' prefix outdated, assistant owns bug tracking
-- Table stores bug reports managed by assistant agent
ALTER TABLE ui_bug_reports RENAME TO assistant_bug_reports;

-- ui_demo_sessions → assistant_demo_sessions
-- Issue: 'ui_' prefix outdated, assistant owns demo creation
-- Table stores demo sessions created by assistant agent
ALTER TABLE ui_demo_sessions RENAME TO assistant_demo_sessions;

-- ui_delegation_log → assistant_delegation_log
-- Issue: 'ui_' prefix outdated, assistant owns delegation routing
-- Table logs delegation decisions made by assistant agent
ALTER TABLE ui_delegation_log RENAME TO assistant_delegation_log;

-- ==============================================================================
-- Category 5: Wrong Prefix - UX Design Expert Tables (4 tables)
-- ==============================================================================

-- ui_component_library → ux_component_library
-- Issue: 'ui_' generic, ux_design_expert owns component library
-- Table stores reusable UI components managed by ux_design_expert
ALTER TABLE ui_component_library RENAME TO ux_component_library;

-- ui_design_debt → ux_design_debt
-- Issue: 'ui_' generic, ux_design_expert tracks design debt
-- Table tracks design debt identified by ux_design_expert
ALTER TABLE ui_design_debt RENAME TO ux_design_debt;

-- ui_design_specs → ux_design_specs
-- Issue: 'ui_' generic, ux_design_expert owns design specifications
-- Table stores design specs created by ux_design_expert
ALTER TABLE ui_design_specs RENAME TO ux_design_specs;

-- ui_design_tokens → ux_design_tokens
-- Issue: 'ui_' generic, ux_design_expert owns design tokens
-- Table stores design tokens (colors, spacing, etc.) managed by ux_design_expert
ALTER TABLE ui_design_tokens RENAME TO ux_design_tokens;

-- ==============================================================================
-- Category 6: Wrong Prefix - User Listener Tables (3 tables)
-- ==============================================================================

-- ui_conversation_context → listener_conversation_context
-- Issue: 'ui_' generic, user_listener owns conversation tracking
-- Table stores conversation context managed by user_listener agent
ALTER TABLE ui_conversation_context RENAME TO listener_conversation_context;

-- ui_intent_classification → listener_intent_classification
-- Issue: 'ui_' generic, user_listener owns intent classification
-- Table stores classified user intents by user_listener agent
ALTER TABLE ui_intent_classification RENAME TO listener_intent_classification;

-- ui_routing_log → listener_routing_log
-- Issue: 'ui_' generic, user_listener owns routing decisions
-- Table logs routing decisions made by user_listener agent
ALTER TABLE ui_routing_log RENAME TO listener_routing_log;

-- ==============================================================================
-- Category 7: Other Unmapped Tables (2 tables)
-- ==============================================================================

-- agent_message → shared_agent_message
-- Issue: Generic prefix, this is shared inter-agent messaging infrastructure
-- Table stores messages between agents (cross-agent coordination)
ALTER TABLE agent_message RENAME TO shared_agent_message;

-- metrics_subtask → manager_metrics_subtask
-- Issue: No prefix, project_manager owns metrics tracking
-- Table tracks subtask metrics for roadmap items managed by project_manager
ALTER TABLE metrics_subtask RENAME TO manager_metrics_subtask;

-- ==============================================================================
-- Record Migration
-- ==============================================================================

-- Create migrations table if it doesn't exist
-- (idempotent - safe to run multiple times)
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Record this migration
-- Use INSERT OR IGNORE to make migration idempotent
INSERT OR IGNORE INTO migrations (name) VALUES ('004_rename_tables_agent_ownership');

COMMIT;

-- ==============================================================================
-- Post-Migration Verification Queries
-- ==============================================================================

/*
-- Verify all tables renamed successfully:
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- Verify foreign keys still work:
PRAGMA foreign_key_check;

-- Verify indexes renamed automatically:
SELECT name, tbl_name FROM sqlite_master WHERE type='index' ORDER BY tbl_name;

-- Count records in renamed tables (sanity check):
SELECT 'developer_commit' as table_name, COUNT(*) as record_count FROM developer_commit
UNION ALL
SELECT 'developer_token_usage', COUNT(*) FROM developer_token_usage
UNION ALL
SELECT 'orchestrator_agent_lifecycle', COUNT(*) FROM orchestrator_agent_lifecycle
UNION ALL
SELECT 'shared_notifications', COUNT(*) FROM shared_notifications
UNION ALL
SELECT 'architect_schema_metadata', COUNT(*) FROM architect_schema_metadata
UNION ALL
SELECT 'shared_notification_user', COUNT(*) FROM shared_notification_user
UNION ALL
SELECT 'shared_notification_state', COUNT(*) FROM shared_notification_state
UNION ALL
SELECT 'shared_audit', COUNT(*) FROM shared_audit
UNION ALL
SELECT 'assistant_bug_reports', COUNT(*) FROM assistant_bug_reports
UNION ALL
SELECT 'assistant_demo_sessions', COUNT(*) FROM assistant_demo_sessions
UNION ALL
SELECT 'assistant_delegation_log', COUNT(*) FROM assistant_delegation_log
UNION ALL
SELECT 'ux_component_library', COUNT(*) FROM ux_component_library
UNION ALL
SELECT 'ux_design_debt', COUNT(*) FROM ux_design_debt
UNION ALL
SELECT 'ux_design_specs', COUNT(*) FROM ux_design_specs
UNION ALL
SELECT 'ux_design_tokens', COUNT(*) FROM ux_design_tokens
UNION ALL
SELECT 'listener_conversation_context', COUNT(*) FROM listener_conversation_context
UNION ALL
SELECT 'listener_intent_classification', COUNT(*) FROM listener_intent_classification
UNION ALL
SELECT 'listener_routing_log', COUNT(*) FROM listener_routing_log
UNION ALL
SELECT 'shared_agent_message', COUNT(*) FROM shared_agent_message
UNION ALL
SELECT 'manager_metrics_subtask', COUNT(*) FROM manager_metrics_subtask;
*/

-- ==============================================================================
-- Rollback Instructions (Manual)
-- ==============================================================================

/*
-- If migration needs to be rolled back, run these commands:
-- (Reverse all renames)

BEGIN TRANSACTION;

ALTER TABLE developer_commit RENAME TO review_commit;
ALTER TABLE developer_token_usage RENAME TO command_token_usage;
ALTER TABLE orchestrator_agent_lifecycle RENAME TO agent_lifecycle;
ALTER TABLE shared_notifications RENAME TO notifications;
ALTER TABLE architect_schema_metadata RENAME TO system_schema_metadata;
ALTER TABLE shared_notification_user RENAME TO notification_user;
ALTER TABLE shared_notification_state RENAME TO notification_system_state;
ALTER TABLE shared_audit RENAME TO system_audit;
ALTER TABLE assistant_bug_reports RENAME TO ui_bug_reports;
ALTER TABLE assistant_demo_sessions RENAME TO ui_demo_sessions;
ALTER TABLE assistant_delegation_log RENAME TO ui_delegation_log;
ALTER TABLE ux_component_library RENAME TO ui_component_library;
ALTER TABLE ux_design_debt RENAME TO ui_design_debt;
ALTER TABLE ux_design_specs RENAME TO ui_design_specs;
ALTER TABLE ux_design_tokens RENAME TO ui_design_tokens;
ALTER TABLE listener_conversation_context RENAME TO ui_conversation_context;
ALTER TABLE listener_intent_classification RENAME TO ui_intent_classification;
ALTER TABLE listener_routing_log RENAME TO ui_routing_log;
ALTER TABLE shared_agent_message RENAME TO agent_message;
ALTER TABLE manager_metrics_subtask RENAME TO metrics_subtask;

-- Remove migration record
DELETE FROM migrations WHERE name = '004_rename_tables_agent_ownership';

COMMIT;
*/
