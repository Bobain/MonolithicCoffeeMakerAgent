-- Migration 003: Token Usage Tracking
-- Created: 2025-10-28
-- Purpose: Track command execution token usage for CFR-018 compliance

-- ==============================================================================
-- command_token_usage: Runtime token tracking for all command executions
-- ==============================================================================

CREATE TABLE IF NOT EXISTS command_token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Command identification
    agent_type TEXT NOT NULL,           -- e.g., "code_developer", "architect"
    command_name TEXT NOT NULL,         -- e.g., "implement", "design"

    -- Timing
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL,              -- Command execution time

    -- Pre-execution estimates (from token_counter.py)
    estimated_input_tokens INTEGER,     -- Total estimated before execution
    command_tokens INTEGER,             -- Just the command file
    readme_tokens INTEGER,              -- Just the agent README
    skills_tokens INTEGER DEFAULT 2000, -- Auto-loaded skills (estimated)

    -- Actual usage (from Anthropic API response)
    actual_input_tokens INTEGER,        -- response.usage.input_tokens
    actual_output_tokens INTEGER,       -- response.usage.output_tokens
    total_tokens INTEGER GENERATED ALWAYS AS (actual_input_tokens + actual_output_tokens) VIRTUAL,

    -- Budget validation
    budget_tokens INTEGER DEFAULT 60000,    -- 30% of 200K context
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

    -- Context (optional linkage)
    task_id TEXT,                       -- Link to specs_task if applicable
    session_id TEXT,                    -- Session identifier

    -- Metadata
    model TEXT DEFAULT 'claude-sonnet-4.5',  -- AI model used
    success BOOLEAN DEFAULT TRUE,       -- Did command complete successfully?
    error_message TEXT                  -- Error details if failed
);

-- ==============================================================================
-- Indexes for efficient querying
-- ==============================================================================

-- Query by agent/command
CREATE INDEX IF NOT EXISTS idx_token_usage_agent_command
ON command_token_usage(agent_type, command_name);

-- Query by timestamp (for trending)
CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp
ON command_token_usage(executed_at);

-- Query budget violations
CREATE INDEX IF NOT EXISTS idx_token_usage_budget
ON command_token_usage(estimated_input_tokens)
WHERE estimated_input_tokens > budget_tokens;

-- Query by task
CREATE INDEX IF NOT EXISTS idx_token_usage_task
ON command_token_usage(task_id)
WHERE task_id IS NOT NULL;

-- ==============================================================================
-- Useful Views
-- ==============================================================================

-- Average token usage per command
CREATE VIEW IF NOT EXISTS v_token_usage_by_command AS
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

-- Recent executions with details
CREATE VIEW IF NOT EXISTS v_recent_token_usage AS
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

-- Budget violations
CREATE VIEW IF NOT EXISTS v_token_budget_violations AS
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

-- ==============================================================================
-- Example Queries
-- ==============================================================================

/*
-- Average usage per agent/command
SELECT * FROM v_token_usage_by_command;

-- Recent executions
SELECT * FROM v_recent_token_usage;

-- Budget violations
SELECT * FROM v_token_budget_violations;

-- Token usage trending over time
SELECT
    DATE(executed_at) as date,
    agent_type,
    AVG(actual_input_tokens) as avg_input,
    AVG(actual_output_tokens) as avg_output,
    COUNT(*) as executions
FROM command_token_usage
WHERE executed_at >= DATE('now', '-30 days')
GROUP BY date, agent_type
ORDER BY date DESC, agent_type;

-- Estimate accuracy trending
SELECT
    DATE(executed_at) as date,
    agent_type,
    AVG(estimate_accuracy_percent) as avg_accuracy,
    COUNT(*) as executions
FROM command_token_usage
WHERE actual_input_tokens IS NOT NULL
GROUP BY date, agent_type
ORDER BY date DESC, agent_type;

-- Most expensive commands (by total tokens)
SELECT
    agent_type || '.' || command_name as command,
    AVG(total_tokens) as avg_total_tokens,
    COUNT(*) as executions
FROM command_token_usage
GROUP BY agent_type, command_name
ORDER BY avg_total_tokens DESC
LIMIT 10;
*/
