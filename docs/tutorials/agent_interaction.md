# Agent Interaction Guide

This guide explains how agents work together, when to use which agent, and how to communicate effectively with the autonomous system.

## Table of Contents

1. [Understanding the Agent Ecosystem](#understanding-the-agent-ecosystem)
2. [Agent Directory](#agent-directory)
3. [Agent Boundaries and Ownership](#agent-boundaries-and-ownership)
4. [Delegating Tasks](#delegating-tasks)
5. [Communication Patterns](#communication-patterns)
6. [Examples: Good vs Bad Requests](#examples-good-vs-bad-requests)
7. [Advanced Patterns](#advanced-patterns)

---

## Understanding the Agent Ecosystem

The MonolithicCoffeeMakerAgent system uses **specialized agents** that work together, each with clear responsibilities and boundaries.

### Key Principles

1. **Specialization**: Each agent has a specific domain of expertise
2. **Boundaries**: Agents respect file/directory ownership rules
3. **Delegation**: Agents delegate work outside their domain
4. **Read-Only by Default**: Most agents only read; few can modify

### The Flow

```
User Question/Request
    ↓
assistant (Documentation Expert + Dispatcher)
    ↓
Analyzes request and routes to:
    ├─→ Answers directly (simple questions)
    ├─→ code_developer (implementation)
    ├─→ project_manager (strategy/docs)
    ├─→ code-searcher (deep analysis)
    ├─→ ux-design-expert (design)
    └─→ memory-bank-synchronizer (doc sync)
```

---

## Agent Directory

### assistant (You start here!)

**Role**: Documentation Expert + Intelligent Dispatcher

**Capabilities**:
- Deep knowledge of ALL project documentation
- Keeps ROADMAP in great detail in mind
- Answers quick questions directly
- Routes complex requests to specialized agents
- Uses Grep/Glob for simple code searches (1-2 files)
- Can demonstrate features with Puppeteer (demos only)

**Boundaries**:
- READ-ONLY access to everything
- NEVER modifies code or docs
- Delegates ALL changes to appropriate agents

**When to use**:
- "Where is X implemented?"
- "How does Y work?"
- "What's the status of feature Z?"
- "Show me the dashboard"
- "I need help with..."

**Example**:
```bash
poetry run assistant "How does the prompt loading system work?"
```

---

### code_developer

**Role**: Autonomous Software Developer

**Capabilities**:
- Writes and modifies ALL code
- Implements features from ROADMAP
- Runs tests and creates PRs
- Updates ROADMAP status (Planned → In Progress → Complete)
- Verifies Definition of Done during implementation

**Owns**:
- `coffee_maker/` - All implementation code
- `tests/` - All test code
- `scripts/` - Utility scripts
- `pyproject.toml` - Dependencies

**Boundaries**:
- Does NOT modify docs/ directory (use project_manager)
- Does NOT make strategic ROADMAP decisions (use project_manager)
- Does NOT monitor GitHub health (use project_manager)

**When to use**:
- "Implement feature X"
- "Fix the bug in file.py"
- "Add tests for authentication"
- "Update dependencies in pyproject.toml"
- "Create a PR for PRIORITY 12"

**Example**:
```bash
# Via assistant delegation
poetry run assistant "Please implement PRIORITY 15 from the ROADMAP"

# Or directly via daemon
poetry run code-developer --auto-approve
```

---

### project_manager

**Role**: Project Coordinator + Strategic Planner

**Capabilities**:
- Creates and updates technical specifications
- Makes strategic ROADMAP decisions
- Monitors GitHub (PRs, issues, CI/CD)
- Verifies completed work (post-implementation)
- Manages agent configurations
- Sends notifications and warnings

**Owns**:
- `docs/` - ALL documentation
- `.claude/agents/` - Agent definitions
- `.claude/commands/` - Prompt templates
- Strategic ROADMAP planning

**Boundaries**:
- Does NOT write code (use code_developer)
- Does NOT create PRs (use code_developer)
- Can only update ROADMAP status via code_developer

**When to use**:
- "Create a technical spec for PRIORITY 20"
- "What's the project status?"
- "Update the ROADMAP with new priorities"
- "Is feature X complete?"
- "What should we work on next?"

**Example**:
```bash
# View roadmap
poetry run project-manager /roadmap

# Check project status
poetry run project-manager developer-status

# View metrics
poetry run project-manager /metrics
```

---

### code-searcher

**Role**: Deep Codebase Analysis Specialist

**Capabilities**:
- Profound knowledge of entire codebase structure
- Security audits and vulnerability detection
- Dependency tracing and impact analysis
- Pattern detection and code reuse identification
- Architectural consistency checks
- Refactoring opportunity analysis

**Owns**:
- Deep code analysis
- Forensic code examination
- "Chain of Draft" methodology

**Boundaries**:
- READ-ONLY access (never modifies anything)
- Does NOT write documentation directly
- Prepares findings → assistant → project_manager → docs

**When to use**:
- "Find all authentication code"
- "Analyze security vulnerabilities"
- "Map the daemon architecture"
- "Trace dependencies for feature X"
- "Find potential refactoring opportunities"

**Document Output**:
```
docs/
├── security_audit_2025-10-14.md
├── dependency_analysis_2025-10-14.md
└── architecture_analysis_2025-10-14.md
```

**Example**:
```bash
# Via assistant delegation
poetry run assistant "Perform a security audit of the authentication system"
```

---

### ux-design-expert

**Role**: UI/UX Design + Tailwind CSS Specialist

**Capabilities**:
- Premium UI/UX design guidance
- Tailwind CSS utility expertise
- Highcharts configuration and styling
- Design systems architecture
- Component design specifications

**Owns**:
- All design decisions
- UI/UX patterns
- Color schemes and spacing
- Chart design specifications

**Boundaries**:
- Provides design specs, does NOT implement
- Implementation delegated to code_developer

**When to use**:
- "Design a dashboard layout"
- "What colors should I use for this component?"
- "How should I structure the navigation?"
- "Create a chart design for analytics"
- "What Tailwind classes should I use?"

**Example**:
```bash
# Via assistant delegation
poetry run assistant "Design a user analytics dashboard with charts"
```

---

### memory-bank-synchronizer

**Role**: Documentation Synchronization Agent

**Capabilities**:
- Keeps `.claude/CLAUDE.md` files current with code
- Analyzes code changes and updates documentation
- Ensures memory bank reflects reality

**Owns**:
- `.claude/CLAUDE.md` synchronization

**Boundaries**:
- Limited to CLAUDE.md files only
- Does NOT modify code

**When to use**:
- "Sync CLAUDE.md with the current codebase"
- "Memory bank is outdated"
- "Update agent instructions to reflect new architecture"

**Example**:
```bash
# Via assistant delegation
poetry run assistant "Please sync the CLAUDE.md file with current code"
```

---

## Agent Boundaries and Ownership

### File/Directory Ownership Matrix

This table shows who can modify what:

| File/Directory | Owner | Can Modify? | Others |
|----------------|-------|-------------|--------|
| `docs/` | project_manager | YES | assistant: READ-ONLY, code_developer: READ-ONLY |
| `docs/roadmap/ROADMAP.md` | project_manager (strategy), code_developer (status) | BOTH | assistant: READ-ONLY |
| `.claude/agents/` | project_manager | YES | All others: READ-ONLY |
| `.claude/CLAUDE.md` | project_manager, memory-bank-synchronizer | YES | Others: READ-ONLY |
| `.claude/commands/` | project_manager | YES | Others: READ-ONLY |
| `coffee_maker/` | code_developer | YES | All others: READ-ONLY |
| `tests/` | code_developer | YES | All others: READ-ONLY |
| `scripts/` | code_developer | YES | All others: READ-ONLY |
| `pyproject.toml` | code_developer | YES | All others: READ-ONLY |

### Tool Ownership Matrix

This table shows which agent uses which tools:

| Tool/Capability | Owner | Others |
|----------------|-------|--------|
| Code editing | code_developer | assistant: READ-ONLY |
| GitHub PR creation | code_developer | - |
| GitHub monitoring | project_manager | assistant delegates |
| Puppeteer (DoD during impl) | code_developer | - |
| Puppeteer (DoD post-impl) | project_manager | - |
| Puppeteer (demos) | assistant | NOT for verification |
| Code search (simple) | assistant | 1-2 files only |
| Code search (complex) | code-searcher | Full forensics |
| Design decisions | ux-design-expert | Others delegate |
| Doc sync | memory-bank-synchronizer | - |

---

## Delegating Tasks

### The Delegation Decision Tree

Use this tree for EVERY request:

```
Your Request
    ↓
1. Is it a code change/implementation?
   YES → code_developer
   NO → Continue

2. Is it documentation update (docs/, .claude/)?
   YES → project_manager
   NO → Continue

3. Is it complex code analysis?
   YES → code-searcher
   NO → Continue

4. Is it a design decision?
   YES → ux-design-expert
   NO → Continue

5. Is it project status/planning?
   YES → project_manager
   NO → Continue

6. Is it doc sync (CLAUDE.md outdated)?
   YES → memory-bank-synchronizer
   NO → Continue

7. Is it a simple question?
   YES → assistant answers directly
   NO → Ask assistant for clarification
```

### How to Delegate

**Option 1: Via assistant (Recommended)**
```bash
# The assistant will analyze and route appropriately
poetry run assistant "Implement authentication feature"
```

**Option 2: Direct to agent**
```bash
# Start autonomous daemon (code_developer)
poetry run code-developer --auto-approve

# Use project_manager CLI
poetry run project-manager /roadmap
```

---

## Communication Patterns

### Pattern 1: Simple Question

**User**: "How do I run tests?"

**Flow**:
```
User → assistant
    ↓
    assistant answers directly using documentation knowledge
```

**Response**:
```bash
"You can run tests with pytest:

pytest                    # All tests
pytest tests/unit/        # Unit tests only
pytest -v                 # Verbose output
```

---

### Pattern 2: Code Implementation

**User**: "Implement user authentication"

**Flow**:
```
User → assistant
    ↓
    assistant analyzes: "Code implementation needed"
    ↓
    Delegates to code_developer
    ↓
    code_developer:
      1. Reads ROADMAP for priority
      2. Creates technical spec (via project_manager)
      3. Implements feature
      4. Runs tests
      5. Creates PR
```

**Response**:
```
"This requires code implementation. I'll delegate to code_developer, who will:
1. Review the ROADMAP
2. Create a technical spec
3. Implement authentication
4. Write tests
5. Create a PR"
```

---

### Pattern 3: Complex Analysis

**User**: "Find all security vulnerabilities in authentication"

**Flow**:
```
User → assistant
    ↓
    assistant analyzes: "Complex code analysis needed"
    ↓
    Delegates to code-searcher
    ↓
    code-searcher:
      1. Performs deep security audit
      2. Identifies vulnerabilities
      3. Prepares findings
      4. Presents to assistant
    ↓
    assistant delegates to project_manager
    ↓
    project_manager creates docs/security_audit_2025-10-14.md
```

**Response**:
```
"This requires comprehensive security analysis. I'll delegate to code-searcher,
who will perform a deep security audit and document findings."
```

---

### Pattern 4: Design Decision

**User**: "What colors should I use for the dashboard?"

**Flow**:
```
User → assistant
    ↓
    assistant analyzes: "Design decision needed"
    ↓
    Delegates to ux-design-expert
    ↓
    ux-design-expert provides design specification
    ↓
    (Optional) Delegate to code_developer for implementation
```

**Response**:
```
"This is a UI/UX design decision. I'll delegate to ux-design-expert,
who will provide design guidance for your dashboard."
```

---

### Pattern 5: Strategic Planning

**User**: "What should we work on next?"

**Flow**:
```
User → assistant
    ↓
    assistant analyzes: "Strategic planning needed"
    ↓
    Delegates to project_manager
    ↓
    project_manager:
      1. Analyzes ROADMAP
      2. Checks dependencies
      3. Evaluates priorities
      4. Provides recommendations
```

**Response**:
```
"This requires strategic analysis. I'll delegate to project_manager,
who will analyze the ROADMAP and provide recommendations."
```

---

## Examples: Good vs Bad Requests

### Good Requests (Clear, Direct, Appropriate Agent)

**Excellent**:
```
"Implement PRIORITY 15 from the ROADMAP"
→ Clear, references ROADMAP, code_developer knows what to do
```

**Excellent**:
```
"Find all places where we handle authentication"
→ Clear scope, appropriate for code-searcher
```

**Excellent**:
```
"Create a technical spec for OAuth integration"
→ Clear deliverable, project_manager owns specs
```

**Excellent**:
```
"Design a user analytics dashboard with charts and metrics"
→ Clear scope, design decision, ux-design-expert
```

**Excellent**:
```
"How does the daemon work?"
→ Simple question, assistant can answer directly
```

### Bad Requests (Unclear, Wrong Agent, Conflicting)

**Problematic**:
```
"Make it better"
→ Too vague, no clear scope or deliverable
```

**Better version**:
```
"Improve error handling in the daemon by adding try-catch blocks
and logging for all external API calls"
```

---

**Problematic**:
```
"Fix everything and update all the docs"
→ Multiple agents needed, no priorities
```

**Better version**:
```
"Fix the authentication bug in coffee_maker/auth.py, then update
docs/AUTHENTICATION.md to reflect the fix"
```

---

**Problematic**:
```
"assistant, please modify roadmap_cli.py"
→ Wrong agent! assistant is READ-ONLY
```

**Better version**:
```
"Please delegate to code_developer to fix the bug in roadmap_cli.py"
```

---

**Problematic**:
```
"code_developer, update the ROADMAP with new priorities"
→ Wrong agent! code_developer doesn't own docs/
```

**Better version**:
```
"project_manager, please add OAuth integration as PRIORITY 25 in the ROADMAP"
```

---

**Problematic**:
```
"Design and implement a dashboard"
→ Two different agents needed
```

**Better version**:
```
"First, ux-design-expert: design a dashboard layout.
Then, code_developer: implement the design."
```

---

### Checklist: Is My Request Good?

Before sending a request, check:

- [ ] **Clear scope**: What exactly needs to be done?
- [ ] **Correct agent**: Who should handle this?
- [ ] **Necessary context**: Have I provided enough information?
- [ ] **Appropriate boundaries**: Am I respecting agent ownership?
- [ ] **Reasonable size**: Is this one task or multiple?

---

## Advanced Patterns

### Multi-Agent Workflows

Some requests require multiple agents working in sequence:

**Example: Complete Feature Implementation**

```
User: "Add OAuth authentication with Google"

Workflow:
1. assistant receives request
2. assistant delegates to project_manager:
   - "Create technical spec for PRIORITY 25: OAuth"
3. project_manager creates docs/PRIORITY_25_TECHNICAL_SPEC.md
4. assistant delegates to ux-design-expert:
   - "Design OAuth login flow UI"
5. ux-design-expert provides design specs
6. assistant delegates to code_developer:
   - "Implement PRIORITY 25 using the spec and design"
7. code_developer implements, tests, creates PR
8. assistant delegates to project_manager:
   - "Update ROADMAP: PRIORITY 25 Complete"
```

---

### Autonomous Mode vs. Interactive Mode

**Autonomous Mode** (Daemon):
```bash
poetry run code-developer --auto-approve
```

The daemon works independently:
- Reads ROADMAP automatically
- Implements priorities in order
- Creates PRs without approval
- Continues until all work is done

**Interactive Mode** (Manual):
```bash
poetry run assistant "your request here"
```

You direct the workflow:
- Specify exactly what to do
- Review and approve work
- Control the pace
- Delegate explicitly

---

### When to Ask for Help

If you're unsure about:
- Which agent to use
- How to phrase a request
- Whether something is possible
- What the current status is

**Always start with assistant**:
```bash
poetry run assistant "I need help with [your situation]"
```

The assistant will:
- Clarify what you need
- Explain which agent should handle it
- Route the request appropriately
- Provide guidance and examples

---

## Summary

### Quick Reference

**Start here**:
- assistant - Documentation expert + intelligent dispatcher

**Code changes**:
- code_developer - ALL code modifications

**Documentation**:
- project_manager - ALL docs/ directory changes

**Analysis**:
- code-searcher - Deep code analysis and security audits

**Design**:
- ux-design-expert - UI/UX guidance and specifications

**Doc sync**:
- memory-bank-synchronizer - Keep CLAUDE.md current

### Remember

1. **Respect boundaries** - Don't ask agents to work outside their domain
2. **Be specific** - Clear requests get better results
3. **Start with assistant** - It will route appropriately
4. **One task at a time** - Break complex work into steps
5. **Check ownership** - Use the right agent for the right files

---

**Next Steps**:
- Try making requests to different agents
- Observe how they delegate to each other
- Read agent definitions in `.claude/agents/`
- Experiment with the autonomous daemon

---

**Last Updated**: 2025-10-14
**Version**: 1.0
