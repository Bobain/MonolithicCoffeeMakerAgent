-- Migration 004c: Rename Tables in notifications.db
-- Created: 2025-10-28
-- SPEC: SPEC-115 - Database Table Renaming for Agent Ownership Clarity
-- Purpose: Rename tables specific to notifications.db
--
-- This is a companion migration to 004_rename_tables_agent_ownership.sql
-- Run this ONLY on notifications.db
--
-- ==============================================================================
-- IMPORTANT: Run this migration on notifications.db ONLY
-- ==============================================================================

BEGIN TRANSACTION;

-- ==============================================================================
-- Notifications Database Tables
-- ==============================================================================

-- notifications → shared_notifications
-- Issue: No prefix indicating cross-agent usage
-- Table used for inter-agent messaging and coordination
ALTER TABLE notifications RENAME TO shared_notifications;

-- ==============================================================================
-- Record Migration
-- ==============================================================================

-- Create migrations table if it doesn't exist
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Record this migration
-- Use INSERT OR IGNORE to make migration idempotent
INSERT OR IGNORE INTO migrations (name) VALUES ('004c_rename_notifications_tables');

COMMIT;

-- ==============================================================================
-- Post-Migration Verification Queries
-- ==============================================================================

/*
-- Verify table renamed:
SELECT name FROM sqlite_master WHERE type='table' AND name='shared_notifications';

-- Count records (sanity check):
SELECT COUNT(*) as record_count FROM shared_notifications;
*/

-- ==============================================================================
-- Rollback Instructions (Manual)
-- ==============================================================================

/*
-- If migration needs to be rolled back, run these commands:

BEGIN TRANSACTION;

-- Rename table back
ALTER TABLE shared_notifications RENAME TO notifications;

-- Remove migration record
DELETE FROM migrations WHERE name = '004c_rename_notifications_tables';

COMMIT;
*/
