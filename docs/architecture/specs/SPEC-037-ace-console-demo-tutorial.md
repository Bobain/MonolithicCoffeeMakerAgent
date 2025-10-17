# SPEC-037: ACE Console Demo Tutorial

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: US-037 (ROADMAP), ADR-003 (Simplification-First Approach)

**Related ADRs**: None (documentation-only)

**Assigned To**: code_developer

---

## Executive Summary

This specification describes a simple, practical tutorial document that teaches users how to use ACE agents (generator, reflector, curator) via the console interface. The tutorial uses real examples from the MonolithicCoffeeMakerAgent codebase and focuses on hands-on learning.

---

## Problem Statement

### Current Situation

ACE framework exists but:
- No single tutorial showing how to use it
- Documentation scattered across multiple files
- New users don't know where to start
- No practical examples from this project
- Steep learning curve

**Proof**: New user asks "How do I use generator?" → No clear answer

### Goal

Create ONE comprehensive tutorial that:
- Teaches all three ACE agents (generator, reflector, curator)
- Uses real examples from this project
- Gets users productive in 30 minutes
- Provides troubleshooting guidance
- Links to deeper documentation

### Non-Goals

- NOT teaching ACE theory/philosophy (just practical usage)
- NOT documenting ACE internals (that's for architecture docs)
- NOT creating video tutorials (text-only for now)
- NOT covering advanced features (basic usage only)

---

## Requirements

### Functional Requirements

1. **FR-1**: Document covers generator (trace capture)
2. **FR-2**: Document covers reflector (insight extraction)
3. **FR-3**: Document covers curator (playbook maintenance)
4. **FR-4**: Includes 5+ real examples from this project
5. **FR-5**: Has troubleshooting section (5+ common issues)
6. **FR-6**: Includes quick reference card (cheat sheet)

### Non-Functional Requirements

1. **NFR-1**: Readability: Clear, concise writing (~2000 words)
2. **NFR-2**: Completeness: New user can follow without asking questions
3. **NFR-3**: Accuracy: All examples tested and working
4. **NFR-4**: Discoverability: Linked from README, CLAUDE.md, docs/TUTORIALS.md

### Constraints

- Must use Markdown format (consistency with other docs)
- Must follow existing docs/ structure
- Must work with current ACE implementation
- Must be maintainable (update as ACE evolves)

---

## Proposed Solution

### High-Level Approach

**Create Single Tutorial Document**: `docs/ACE_CONSOLE_DEMO_TUTORIAL.md` (~2000 words, 7 sections) that walks users through using each ACE agent with real examples.

**Why This is Simple**:
- One file (not multiple docs)
- Text-only (no screenshots/videos to maintain)
- Real examples (already in our codebase)
- No new code (documentation only)

### Document Structure

```
1. Introduction (200 words)
   - What is ACE?
   - When to use each agent
   - Tutorial objectives

2. Prerequisites (100 words)
   - Installation check
   - Environment setup
   - Verification steps

3. Tutorial 1: generator (400 words)
   - What generator does
   - How to invoke
   - Example: Capture daemon trace
   - Where traces are stored

4. Tutorial 2: reflector (400 words)
   - What reflector does
   - How to invoke
   - Example: Extract insights from trace
   - How to read delta items

5. Tutorial 3: curator (400 words)
   - What curator does
   - How to invoke
   - Example: Maintain playbooks
   - How playbooks evolve

6. Complete Workflow (300 words)
   - End-to-end ACE cycle
   - Example: Improve daemon performance
   - How to iterate

7. Troubleshooting (200 words)
   - Common errors
   - Solutions
   - Where to get help

8. Quick Reference (100 words)
   - Command cheat sheet
   - File locations
   - Links to docs
```

Total: ~2100 words

---

## Detailed Design

### Content Outline

#### Section 1: Introduction to ACE Framework (200 words)

```markdown
# ACE Console Demo Tutorial

Welcome! This tutorial teaches you how to use the ACE (Agentic Context Engineering) framework via the command line.

## What is ACE?

ACE is a learning system with three agents:
- **generator**: Captures execution traces (what happened)
- **reflector**: Extracts insights from traces (what to learn)
- **curator**: Maintains playbooks (how to improve)

## When to Use ACE Agents

- **generator**: After any agent execution (automatic or manual)
- **reflector**: When you want to learn from traces (weekly review)
- **curator**: When playbooks need updating (monthly maintenance)

## Tutorial Objectives

By the end, you'll know how to:
1. Capture traces with generator
2. Extract insights with reflector
3. Maintain playbooks with curator
4. Run complete ACE workflow
```

#### Section 2: Prerequisites & Setup (100 words)

```markdown
## Prerequisites

Check your setup:

```bash
# 1. Verify installation
poetry run project-manager --version  # Should show version

# 2. Check ACE agents exist
ls .claude/agents/  # Should see generator.md, reflector.md, curator.md

# 3. Verify data directory
ls data/  # Should see agent directories
```

If any check fails, see INSTALLATION.md for setup instructions.
```

#### Section 3: Tutorial 1 - Using generator (400 words)

```markdown
## Tutorial 1: Using generator

### What generator Does

generator **captures execution traces** from agent work:
- Records what the agent did
- Logs tool calls and responses
- Stores in structured format (JSON)
- Provides input for reflector

### How to Invoke generator

**Automatic** (daemon does this):
```bash
# Daemon automatically captures traces during execution
poetry run code-developer --auto-approve
# Traces saved to: data/generator/traces/
```

**Manual** (for specific agent):
```bash
# Capture trace from project-manager
poetry run project-manager
# ... do some work ...
# Trace automatically captured
```

### Example: Capture Daemon Trace

**Scenario**: You want to see what code_developer did while implementing US-035.

**Steps**:
```bash
# 1. Run daemon
poetry run code-developer --auto-approve

# 2. Daemon implements US-035
# ... (automatic work)

# 3. Check traces
ls -lh data/generator/traces/
# Shows: trace_2025_10_17_code_developer_us_035.json

# 4. View trace
cat data/generator/traces/trace_2025_10_17_code_developer_us_035.json | jq .
# Shows: All tool calls, responses, timestamps
```

### Where Traces Are Stored

```
data/
  generator/
    traces/
      trace_YYYY_MM_DD_agent_task.json  # Execution traces
```

Each trace contains:
- Timestamp
- Agent type
- Tool calls
- Responses
- Duration
```

#### Section 4: Tutorial 2 - Using reflector (400 words)

```markdown
## Tutorial 2: Using reflector

### What reflector Does

reflector **extracts insights** from traces:
- Analyzes what worked well
- Identifies improvements
- Generates delta items (insights)
- Feeds insights to curator

### How to Invoke reflector

```bash
# Analyze recent traces
poetry run reflector analyze --recent 7d  # Last 7 days

# Analyze specific trace
poetry run reflector analyze --trace data/generator/traces/trace_2025_10_17_code_developer_us_035.json
```

### Example: Extract Insights from Daemon Trace

**Scenario**: Daemon completed US-035, you want insights.

**Steps**:
```bash
# 1. Run reflector on recent traces
poetry run reflector analyze --recent 1d

# 2. View delta items (insights)
ls data/reflector/delta/
# Shows: delta_2025_10_17_singleton_enforcement.md

# 3. Read insights
cat data/reflector/delta/delta_2025_10_17_singleton_enforcement.md

# Output example:
# Delta Item: Singleton Enforcement Pattern
#
# Observation: code_developer used file-based singleton (PID file)
# Insight: Simple file-based approach worked well (no complex registry needed)
# Recommendation: Reuse this pattern for other resource locking
# Confidence: HIGH
```

### How to Read Delta Items

Delta items have structure:
- **Observation**: What happened (facts)
- **Insight**: What we learned (interpretation)
- **Recommendation**: What to do (action)
- **Confidence**: How sure we are (HIGH/MEDIUM/LOW)

**Good delta items** are:
- Specific (not vague)
- Actionable (clear next steps)
- Evidence-based (grounded in traces)
```

#### Section 5: Tutorial 3 - Using curator (400 words)

```markdown
## Tutorial 3: Using curator

### What curator Does

curator **maintains playbooks** based on insights:
- Reviews delta items from reflector
- Updates existing playbooks
- Creates new playbooks when needed
- Ensures playbooks stay current

### How to Invoke curator

```bash
# Review all delta items
poetry run curator review

# Update specific playbook
poetry run curator update --playbook singleton_enforcement

# Create new playbook
poetry run curator create --name new_pattern
```

### Example: Update Playbooks

**Scenario**: reflector found insights about singleton pattern, update playbooks.

**Steps**:
```bash
# 1. Run curator review
poetry run curator review

# Output:
# Found 3 new delta items:
# - delta_2025_10_17_singleton_enforcement.md
# - delta_2025_10_17_error_handling.md
# - delta_2025_10_17_testing_strategy.md
#
# Recommendations:
# - Update playbook: resource_locking.md (add singleton pattern)
# - Create new playbook: error_recovery.md
# - Update playbook: test_patterns.md (add integration test example)

# 2. Apply recommendations
poetry run curator apply --all

# 3. View updated playbooks
ls data/curator/playbooks/
# Shows:
# - resource_locking.md (UPDATED)
# - error_recovery.md (NEW)
# - test_patterns.md (UPDATED)

# 4. Read updated playbook
cat data/curator/playbooks/resource_locking.md

# Shows new section:
# ## Pattern: File-Based Singleton (2025-10-17)
# [Singleton pattern details...]
```

### How Playbooks Evolve

**Lifecycle**:
1. reflector finds pattern → creates delta item
2. curator reviews delta → updates playbook
3. Playbook used by agents → validates pattern
4. Pattern refined over time → playbook improves

**Result**: Living documentation that grows with system!
```

#### Section 6: Complete Workflow (300 words)

```markdown
## Complete ACE Workflow

### End-to-End Example: Improve Daemon Performance

**Scenario**: Daemon is slow implementing priorities, optimize it.

**Full ACE Cycle**:

```bash
# STEP 1: Capture Traces (generator)
poetry run code-developer --auto-approve  # Daemon runs, captures traces

# STEP 2: Extract Insights (reflector)
poetry run reflector analyze --recent 7d

# Insights found:
# - Daemon spends 80% time parsing ROADMAP (bottleneck!)
# - ROADMAP parser called 100+ times per execution
# - No caching implemented

# STEP 3: Update Playbooks (curator)
poetry run curator review

# curator adds to playbook: performance_optimization.md
# ## Pattern: Cache Expensive Operations
# When: Operation called repeatedly with same inputs
# Solution: Implement mtime-based caching
# Example: ROADMAP parser (see SPEC-XXX)

# STEP 4: Apply Learning
# architect reads playbook → creates SPEC-XXX (ROADMAP caching)
# code_developer implements SPEC-XXX
# Result: 274x speedup! (16.31ms → 0.06ms)

# STEP 5: Validate
poetry run code-developer --auto-approve  # Faster now!
poetry run reflector analyze --recent 1d   # Confirms improvement

# CYCLE REPEATS: System learns and improves continuously!
```

### Key Takeaway

**ACE is a learning loop**:
- Capture → Analyze → Curate → Apply → Improve
- Each cycle makes the system better
- Playbooks preserve knowledge over time
```

#### Section 7: Troubleshooting (200 words)

```markdown
## Troubleshooting

### Issue 1: "generator not found"

**Symptom**: `poetry run generator` fails

**Solution**:
```bash
# Check .claude/agents/ exists
ls .claude/agents/generator.md  # Should exist

# If missing: generator not installed yet (future feature)
# For now: Daemon auto-captures traces
```

### Issue 2: "No traces found"

**Symptom**: `data/generator/traces/` is empty

**Solution**:
- Run daemon first: `poetry run code-developer`
- Or run any agent that creates traces
- Check `data/generator/` exists and is writable

### Issue 3: "reflector crashes"

**Symptom**: reflector fails to analyze trace

**Solution**:
```bash
# Check trace format
cat data/generator/traces/trace.json | jq .  # Should be valid JSON

# If corrupted: Delete trace, re-capture
rm data/generator/traces/trace.json
```

### Issue 4: "curator doesn't update playbooks"

**Symptom**: Playbooks unchanged after `curator review`

**Solution**:
- Check delta items exist: `ls data/reflector/delta/`
- If empty: Run reflector first
- Check playbook permissions (should be writable)

### Issue 5: "Where to get help?"

**Resources**:
- `.claude/agents/README.md` - Agent documentation
- `docs/` - Architecture and guides
- GitHub Issues - Report bugs
```

#### Section 8: Quick Reference (100 words)

```markdown
## Quick Reference

### Commands

```bash
# generator (automatic)
poetry run code-developer           # Captures traces

# reflector
poetry run reflector analyze --recent 7d  # Analyze last 7 days

# curator
poetry run curator review           # Review delta items
poetry run curator apply --all      # Apply recommendations
```

### File Locations

```
data/
  generator/traces/          # Execution traces
  reflector/delta/           # Insights (delta items)
  curator/playbooks/         # Knowledge base
```

### Next Steps

- Read `.claude/agents/README.md` for agent details
- Explore `data/curator/playbooks/` for patterns
- Run complete ACE cycle on your next task!

**Happy learning!** 🚀
```

---

## Testing Strategy

### Manual Testing

**Verification Steps**:
1. **Follow Tutorial**: Author follows entire tutorial from scratch
2. **New User Test**: 3 new users follow tutorial, collect feedback
3. **Example Verification**: All code examples tested and working
4. **Link Check**: All internal links valid
5. **Readability**: Grammarly check, clear language

**Acceptance Criteria**:
- New user completes tutorial in < 45 minutes
- All examples work without errors
- User can run complete ACE cycle after tutorial
- Feedback score > 8/10

---

## Rollout Plan

### Phase 1: Draft Document (Day 1 - 4 hours)

**Goal**: Create complete draft tutorial

**Tasks**:
1. Write all 8 sections (~2000 words)
2. Create code examples
3. Test examples manually
4. Review for clarity

**Success Criteria**:
- All sections complete
- Examples work
- Draft ready for review

### Phase 2: Testing & Refinement (Day 1 - 2 hours)

**Goal**: Validate with real users

**Tasks**:
1. Test tutorial yourself (full walkthrough)
2. Get 2-3 users to follow along
3. Collect feedback
4. Refine based on feedback
5. Fix any broken examples

**Success Criteria**:
- 3+ users tested successfully
- Feedback incorporated
- All examples verified

### Phase 3: Integration (Day 1 - 1 hour)

**Goal**: Link tutorial from other docs

**Tasks**:
1. Add link to `README.md` (Quick Start section)
2. Add link to `.claude/CLAUDE.md` (Agent Usage section)
3. Add link to `docs/TUTORIALS.md` (if exists, or create index)
4. Update `.claude/agents/README.md` (reference tutorial)

**Success Criteria**:
- Tutorial discoverable from 3+ entry points
- Links work correctly
- Navigation flows naturally

---

## Why This is Simple (vs Strategic Spec)

**Strategic Spec** (US-037 in ROADMAP):
- Mentioned 5+ scenarios
- Screenshots/recordings
- Comprehensive FAQ
- User testing with feedback
- ~1 day estimate

**This Simplified Spec**:
- **3 core tutorials** (generator, reflector, curator) + 1 workflow
- **Text-only** (no screenshots/videos to maintain)
- **Focused troubleshooting** (5 issues, not comprehensive FAQ)
- **Quick reference** (cheat sheet, not exhaustive docs)
- **Same 1 day estimate** (maintained timeline, reduced scope)

**What We REUSE**:
- Existing `docs/` structure
- Existing Markdown format
- Real examples from our codebase (daemon traces, US-035 work)
- Existing ACE agents (no new code needed)

**Complexity Reduction**:
- **No multimedia** (text-only, easier to maintain)
- **Focused scope** (practical usage, not theory)
- **Real examples** (from our project, proven to work)
- **Simple structure** (8 sections, linear flow)

---

## Future Enhancements

**NOT in this spec** (deferred):
1. Video tutorials → When user requests
2. Interactive playground → Advanced feature
3. Advanced ACE techniques → Separate advanced guide
4. ACE API documentation → For developers, not users
5. Multi-language support → If international team

---

## References

- US-037: Create ACE Console Demo Tutorial (ROADMAP)
- ADR-003: Simplification-First Approach
- `.claude/agents/README.md` - Agent documentation
- `docs/` - Existing documentation structure

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created (Draft) | architect |

---

## Approval

- [ ] architect (author) - Ready for review
- [ ] code_developer (implementer) - Can create in 1 day
- [ ] project_manager (strategic alignment) - Meets US-037 goals
- [ ] User (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 1 day (7 hours) - Documentation only, no code!
