-- SPEC-115: Database Table Renaming for Agent Ownership Clarity
-- ONE DATABASE: roadmap.db only
-- NO migrations table tracking
-- This script DELETES ITSELF after execution

BEGIN TRANSACTION;

-- ============================================================================
-- RENAME TABLES TO AGENT-BASED PREFIXES
-- ============================================================================

-- Code Developer (2 tables)
ALTER TABLE review_commit RENAME TO developer_commit;
ALTER TABLE command_token_usage RENAME TO developer_token_usage;

-- Orchestrator (1 table)
ALTER TABLE agent_lifecycle RENAME TO orchestrator_agent_lifecycle;

-- Architect (1 table)
ALTER TABLE system_schema_metadata RENAME TO architect_schema_metadata;

-- Shared Infrastructure (5 tables)
ALTER TABLE notifications RENAME TO shared_notifications;
ALTER TABLE notification_user RENAME TO shared_notification_user;
ALTER TABLE notification_system_state RENAME TO shared_notification_state;
ALTER TABLE system_audit RENAME TO shared_audit;
ALTER TABLE agent_message RENAME TO shared_agent_message;

-- Assistant (3 tables)
ALTER TABLE ui_bug_reports RENAME TO assistant_bug_reports;
ALTER TABLE ui_demo_sessions RENAME TO assistant_demo_sessions;
ALTER TABLE ui_delegation_log RENAME TO assistant_delegation_log;

-- UX Design Expert (4 tables)
ALTER TABLE ui_component_library RENAME TO ux_component_library;
ALTER TABLE ui_design_debt RENAME TO ux_design_debt;
ALTER TABLE ui_design_specs RENAME TO ux_design_specs;
ALTER TABLE ui_design_tokens RENAME TO ux_design_tokens;

-- User Listener (3 tables)
ALTER TABLE ui_conversation_context RENAME TO listener_conversation_context;
ALTER TABLE ui_intent_classification RENAME TO listener_intent_classification;
ALTER TABLE ui_routing_log RENAME TO listener_routing_log;

-- Project Manager (1 table)
ALTER TABLE metrics_subtask RENAME TO manager_metrics_subtask;

COMMIT;

-- Success message
SELECT 'Table renaming complete - 20 tables renamed' as status;
