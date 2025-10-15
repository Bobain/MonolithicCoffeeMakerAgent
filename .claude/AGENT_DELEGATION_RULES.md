# Agent Delegation Rules

**Purpose**: Clear guidelines for when to use which agent and how agents should delegate to each other.

**Last Updated**: 2025-10-12

---

## Agent Quick Reference

| Agent | Primary Role | Use When |
|-------|--------------|----------|
| **assistant** | First-line support & triage | Quick questions, simple debugging, concept explanations |
| **project_manager** | ROADMAP & strategic planning | Project status, priorities, DoD verification, GitHub status |
| **code-searcher** | Deep codebase analysis | Find code, analyze patterns, security audits, forensics |
| **code_developer** | Autonomous implementation | Implement features, create specs, autonomous development |
| **ux-design-expert** | UI/UX design guidance | Design systems, layouts, data viz, Tailwind CSS |

---

## Delegation Decision Tree

```
User Question
    ↓
Is it a QUICK question? (< 2 min answer)
    ├─ YES → assistant (handle directly)
    └─ NO  → Is it specialized?
        ↓
        ├─ Code analysis? → code-searcher
        ├─ Project/ROADMAP? → project_manager
        ├─ Design/UX? → ux-design-expert
        └─ Implementation? → code_developer
```

---

## Detailed Delegation Rules

### 1. assistant (First-Line Support)

**When to Use**:
- ✅ Quick factual questions
- ✅ Concept explanations (high-level)
- ✅ Documentation pointers
- ✅ Simple debugging (read logs, check config)
- ✅ Tool usage help

**When to Delegate**:
- ⏩ Complex code analysis → **code-searcher**
- ⏩ ROADMAP/strategy questions → **project_manager**
- ⏩ Design questions → **ux-design-expert**
- ⏩ Implementation requests → **code_developer**

**Examples**:

```
✅ HANDLE: "How do I run tests?"
→ Direct answer with commands

❌ DELEGATE: "Find all authentication code"
→ Use code-searcher (complex search)

✅ HANDLE: "What's in the ROADMAP?"
→ Read ROADMAP.md and summarize

❌ DELEGATE: "What should we prioritize next?"
→ Use project_manager (strategic analysis)
```

---

### 2. project_manager (Strategic Planning)

**When to Use**:
- ✅ ROADMAP analysis and management
- ✅ Project health and status
- ✅ Strategic recommendations
- ✅ DoD verification (formal)
- ✅ GitHub PR/issue status
- ✅ Warning users about blockers

**When to Delegate**:
- ⏩ Deep code analysis → **code-searcher**
- ⏩ Design decisions → **ux-design-expert**
- ⏩ Implementation work → **code_developer**

**Examples**:

```
✅ HANDLE: "What's the project status?"
→ Analyze ROADMAP, check GitHub, provide summary

✅ HANDLE: "Is feature X complete?"
→ Check ROADMAP status, verify with Puppeteer

⏩ DELEGATE: "How is feature X implemented?"
→ Use code-searcher (find implementation details)

⏩ DELEGATE: "Implement feature Y"
→ Use code_developer (autonomous implementation)
```

**Warning Capability**:
```python
# project_manager can warn users
service.warn_user(
    title="🚨 BLOCKER: PR #121 failing",
    message="Version check failing. Bump version in pyproject.toml",
    priority="critical"
)
```

---

### 3. code-searcher (Codebase Analysis)

**When to Use**:
- ✅ Find specific functions/classes/code
- ✅ Analyze code patterns
- ✅ Security vulnerability analysis
- ✅ Architectural mapping
- ✅ Forensic code examination
- ✅ Chain of Draft (CoD) analysis

**When to Delegate**:
- ⏩ Strategic recommendations → **project_manager**
- ⏩ Design improvements → **ux-design-expert**
- ⏩ Actual code changes → **code_developer**

**Examples**:

```
✅ HANDLE: "Where is authentication implemented?"
→ Search, find, map all auth code with line numbers

✅ HANDLE: "Analyze error handling patterns"
→ Use CoD methodology for efficient analysis

❌ DON'T: Make ROADMAP recommendations
→ Provide findings, let project_manager recommend

❌ DON'T: Implement changes
→ Find and explain, let code_developer implement
```

---

### 4. code_developer (Autonomous Implementation)

**When to Use**:
- ✅ Implement features from ROADMAP
- ✅ Create technical specifications
- ✅ Autonomous development (background daemon)
- ✅ Fix bugs and create PRs
- ✅ Verify DoD with Puppeteer

**When to Delegate**:
- ⏩ Understand existing code → **code-searcher**
- ⏩ Design guidance → **ux-design-expert**
- ⏩ Strategic decisions → **project_manager**

**Examples**:

```
✅ HANDLE: "Implement PRIORITY 5"
→ Read spec, implement, test, commit, create PR

⏩ DELEGATE: "How is X currently implemented?"
→ Use code-searcher (find before implementing)

⏩ DELEGATE: "Should this be a button or link?"
→ Use ux-design-expert (design decision)

✅ HANDLE: "Verify dashboard is working"
→ Use Puppeteer to test and verify DoD
```

---

### 5. ux-design-expert (Design Guidance)

**When to Use**:
- ✅ UI/UX design recommendations
- ✅ Component design and layout
- ✅ Design systems and tokens
- ✅ Data visualization (Highcharts)
- ✅ Tailwind CSS implementation
- ✅ Accessibility guidance

**When to Delegate**:
- ⏩ Code implementation → **code_developer**
- ⏩ Existing design analysis → **code-searcher**
- ⏩ Strategic priority → **project_manager**

**Examples**:

```
✅ HANDLE: "Design a dashboard layout"
→ Provide mockup, Tailwind classes, component structure

✅ HANDLE: "Best chart type for this data?"
→ Recommend chart, provide Highcharts config

❌ DON'T: Implement the code
→ Provide design, let code_developer implement

⏩ DELEGATE: "Find existing design patterns"
→ Use code-searcher (analyze current code)
```

---

## Inter-Agent Communication

### How Agents Delegate

**Using Task Tool**:

```python
# assistant delegating to code-searcher
Task(
    subagent_type="code-searcher",
    description="Find authentication code",
    prompt="Locate all authentication-related code. "
           "Find login, JWT validation, session management. "
           "Provide file paths with line numbers."
)

# project_manager delegating to code-searcher
Task(
    subagent_type="code-searcher",
    description="Analyze PRIORITY 5 implementation",
    prompt="Find all code related to PRIORITY 5 implementation. "
           "Check what's been done, what remains."
)
```

### Delegation Patterns

**Pattern 1: Investigate then Warn**
```
project_manager
  ↓ delegates
code-searcher (find issue)
  ↓ returns findings
project_manager
  ↓ uses findings
warn_user(blocker details)
```

**Pattern 2: Design then Implement**
```
user → ux-design-expert (design)
  ↓ provides mockup
user → code_developer (implement design)
```

**Pattern 3: Search then Explain**
```
user → assistant (question)
  ↓ delegates if complex
code-searcher (find code)
  ↓ returns details
assistant (explain to user)
```

---

## Common Delegation Scenarios

### Scenario 1: User asks "Where is X?"

**Simple (1-2 files)**:
- assistant → Use Grep/Read directly

**Complex (many files, patterns)**:
- assistant → Delegate to code-searcher

### Scenario 2: User asks "What should we work on next?"

**Always**:
- Any agent → Delegate to project_manager
- project_manager analyzes ROADMAP, dependencies, risks

### Scenario 3: User asks "Implement feature X"

**Flow**:
1. project_manager → Check if in ROADMAP, strategic fit
2. code_developer → Create spec if needed
3. code-searcher → Understand existing code
4. ux-design-expert → Design if UI involved
5. code_developer → Implement

### Scenario 4: User asks "Design a dashboard"

**Flow**:
1. ux-design-expert → Create design, mockup, Tailwind
2. code_developer → Implement the design

**Not**:
- ❌ assistant trying to design (delegate!)
- ❌ ux-design-expert implementing (design only!)

---

## Agent Scope Boundaries

### What Each Agent Should NOT Do

**assistant**:
- ❌ Deep codebase analysis
- ❌ Strategic ROADMAP decisions
- ❌ UI/UX design
- ❌ Code implementation
- ❌ Formal DoD verification

**project_manager**:
- ❌ Deep code analysis (use code-searcher)
- ❌ Design decisions (use ux-design-expert)
- ❌ Code implementation (use code_developer)

**code-searcher**:
- ❌ Strategic recommendations
- ❌ Design suggestions
- ❌ Code implementation
- ❌ ROADMAP changes

**code_developer**:
- ❌ Strategic priority decisions (defer to project_manager)
- ❌ Design from scratch (get from ux-design-expert)

**ux-design-expert**:
- ❌ Code implementation
- ❌ Strategic decisions
- ❌ Code analysis

---

## Best Practices

### For All Agents

1. **Recognize limitations**: Know when a task is outside your scope
2. **Delegate explicitly**: Tell user "I'm delegating to X because..."
3. **Chain results**: Use findings from specialized agents
4. **Acknowledge expertise**: "code-searcher specializes in..."

### For Users

1. **Start with assistant**: For general questions
2. **Be specific**: "Use code-searcher to..." for explicit agent selection
3. **Trust delegation**: Agents know when to delegate
4. **Use /agent-X**: Explicit agent invocation when needed

---

## Delegation Examples

### Example 1: Multi-Agent Workflow

**User**: "I want to add a new analytics feature"

**Flow**:
```
1. assistant → Triage
   └─ "This needs strategic planning and design"

2. project_manager → Analyze impact
   - Check ROADMAP fit
   - Assess dependencies
   - Provide recommendation

3. ux-design-expert → Design UI
   - Dashboard layout
   - Chart types
   - Component structure

4. code_developer → Implement
   - Use design from ux-design-expert
   - Implement feature
   - Create PR

5. project_manager → Verify
   - Check DoD with Puppeteer
   - Update ROADMAP
```

### Example 2: Investigation Workflow

**User**: "Why is authentication slow?"

**Flow**:
```
1. assistant → Initial triage
   └─ "This needs code analysis"

2. code-searcher → Find auth code
   - Locate all auth functions
   - Map call chains
   - Identify bottlenecks

3. assistant → Explain findings
   - Summarize issues found
   - Suggest fixes

4. code_developer → Implement fix (if requested)
```

---

## Quick Decision Guide

**"Can I handle this in < 2 minutes with direct tools?"**
- YES → assistant handles it
- NO → Delegate to specialist

**"Does this require code analysis?"**
- YES → code-searcher

**"Does this require strategic decision?"**
- YES → project_manager

**"Does this require design?"**
- YES → ux-design-expert

**"Does this require implementation?"**
- YES → code_developer

---

## Related Documentation

- **Agent Definitions**: `.claude/agents/*.md`
- **Agent Management**: `docs/AGENT_MANAGEMENT.md`
- **Project Instructions**: `.claude/CLAUDE.md`

---

**Version**: 1.0
**Status**: Active - All delegation rules in effect
