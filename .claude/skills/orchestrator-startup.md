# Orchestrator Agent Startup Skill

**Name**: `orchestrator-startup`
**Owner**: orchestrator agent
**Purpose**: Load necessary context for orchestrator agent startup (CFR-007 compliant)
**Priority**: CRITICAL - Used at EVERY orchestrator session start

---

## When to Use This Skill

**MANDATORY** at startup:
- Every time orchestrator agent starts a new session
- Before launching any sub-agents
- Before responding to any user request

**Example Trigger**:
```python
# In orchestrator agent startup sequence
from coffee_maker.skills import StartupSkillLoader, StartupError

loader = StartupSkillLoader()
result = loader.execute_startup_skill("orchestrator")

if not result.success:
    raise StartupError(result.error_message)
```

---

## Skill Execution Steps

## Step 1: Load Required Context

- [ ] Read docs/roadmap/ROADMAP.md
- [ ] Read .claude/CLAUDE.md
- [ ] Read .claude/agents/orchestrator.md
- [ ] Read docs/architecture/decisions/ADR-*.md (list of ADRs for agent coordination patterns)

## Step 2: Validate CFR-007 Compliance

- [ ] Calculate total context budget:
  - Agent prompt (orchestrator.md): ~10K tokens
  - Required docs (ROADMAP, CLAUDE.md): ~15K tokens
  - ADRs (list only): ~2K tokens
  - Total: ~27K tokens
- [ ] Check against context window (200K tokens)
- [ ] Verify <30% (60K tokens max)
- [ ] Log warning if >25% (50K tokens)

## Step 3: Health Checks

- [ ] Verify file access:
  - coffee_maker/autonomous/ (readable - agent modules)
  - docs/roadmap/ (readable - work queue)
  - .claude/agents/ (readable - sub-agent definitions)
- [ ] Check dependencies:
  - python >= 3.9
  - poetry command available
- [ ] API keys:
  - ANTHROPIC_API_KEY (required for Claude agent execution)

## Step 4: Initialize Agent Resources

- [ ] Load agent registry (verify AgentRegistry module exists)
- [ ] Verify sub-agent definition files:
  - .claude/agents/architect.md
  - .claude/agents/code_developer.md
  - .claude/agents/project_manager.md
  - .claude/agents/assistant.md
  - .claude/agents/ux-design-expert.md
  - .claude/agents/code_reviewer.md
- [ ] Register with AgentRegistry (singleton enforcement)

## Success Criteria

- All files readable
- Context budget <30%
- Health checks passed
- Agent registered
- Sub-agent definitions available
