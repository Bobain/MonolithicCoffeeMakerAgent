-- Database Consolidation Script
-- Consolidates development.db and notifications.db into roadmap.db
-- Then deletes the separate databases and this script
-- ONE DATABASE TO RULE THEM ALL: roadmap.db

-- This script is designed to be run ONCE and then DELETE ITSELF

BEGIN TRANSACTION;

-- ============================================================================
-- STEP 1: Add command_token_usage table to roadmap.db (from development.db)
-- ============================================================================

CREATE TABLE IF NOT EXISTS command_token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Command identification
    agent_type TEXT NOT NULL,
    command_name TEXT NOT NULL,

    -- Timing
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL,

    -- Pre-execution estimates
    estimated_input_tokens INTEGER,
    command_tokens INTEGER,
    readme_tokens INTEGER,
    skills_tokens INTEGER DEFAULT 2000,

    -- Actual usage (from API response)
    actual_input_tokens INTEGER,
    actual_output_tokens INTEGER,
    total_tokens INTEGER GENERATED ALWAYS AS (actual_input_tokens + actual_output_tokens) VIRTUAL,

    -- Budget validation
    budget_tokens INTEGER DEFAULT 60000,
    usage_percent REAL GENERATED ALWAYS AS (
        (estimated_input_tokens * 100.0) / budget_tokens
    ) VIRTUAL,
    within_budget BOOLEAN GENERATED ALWAYS AS (
        estimated_input_tokens <= budget_tokens
    ) VIRTUAL,

    -- Accuracy tracking
    estimate_accuracy_percent REAL GENERATED ALWAYS AS (
        CASE
            WHEN actual_input_tokens > 0 THEN
                (estimated_input_tokens * 100.0) / actual_input_tokens
            ELSE NULL
        END
    ) VIRTUAL,

    -- Context
    task_id TEXT,
    session_id TEXT,

    -- Metadata
    model TEXT DEFAULT 'claude-sonnet-4.5',
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_token_usage_agent_command
ON command_token_usage(agent_type, command_name);

CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp
ON command_token_usage(executed_at);

CREATE INDEX IF NOT EXISTS idx_token_usage_budget
ON command_token_usage(estimated_input_tokens)
WHERE estimated_input_tokens > budget_tokens;

CREATE INDEX IF NOT EXISTS idx_token_usage_task
ON command_token_usage(task_id)
WHERE task_id IS NOT NULL;

-- ============================================================================
-- STEP 2: Drop migrations table (we don't track migrations, we delete them)
-- ============================================================================

DROP TABLE IF EXISTS migrations;

COMMIT;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Database consolidation complete!' as status;
SELECT 'All tables now in roadmap.db' as result;
