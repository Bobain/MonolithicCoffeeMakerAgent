# System Requirements - MonolithicCoffeeMakerAgent

**Version**: 1.0
**Created**: 2025-10-15
**Status**: Active
**Maintained By**: project_manager

---

## Table of Contents

- [Quick Reference](#quick-reference)
- [1. Ownership Requirements](#1-ownership-requirements-critical)
- [2. Git Workflow Requirements](#2-git-workflow-requirements-critical)
- [3. Agent Boundaries Requirements](#3-agent-boundaries-requirements)
- [4. ACE Framework Requirements](#4-ace-framework-requirements)
- [5. Dependency Management Requirements](#5-dependency-management-requirements)
- [6. Testing Requirements](#6-testing-requirements)
- [7. Documentation Requirements](#7-documentation-requirements)
- [8. Code Quality Requirements](#8-code-quality-requirements)
- [9. Prompt Management Requirements](#9-prompt-management-requirements)
- [10. Security Requirements](#10-security-requirements)
- [Enforcement Mechanisms](#enforcement-mechanisms)
- [Version History](#version-history)

---

## Quick Reference

**CRITICAL RULES** - These MUST be followed:

1. **NO OWNERSHIP OVERLAPS**: No agent can own a parent directory when subdirectories have different owners
2. **SINGLE BRANCH**: ALL agents work on `roadmap` branch ONLY (no branch switching)
3. **ARCHITECT OWNS DEPENDENCIES**: ONLY architect can run `poetry add` (requires user approval)
4. **34+ TESTS VERIFY OWNERSHIP**: Runtime validation crashes system if overlaps detected
5. **USER_LISTENER IS PRIMARY UI**: ONLY agent with UI, all others are backend-only
6. **CODE_DEVELOPER WRITES CODE**: ONLY agent that modifies coffee_maker/, tests/, scripts/
7. **PROJECT_MANAGER WRITES DOCS**: ONLY agent that modifies docs/ (specific subdirectories)
8. **ACE ENABLED BY DEFAULT**: All agents learn continuously (opt-out via environment variables)

---

## 1. Ownership Requirements (CRITICAL)

### 1.1 The NO OVERLAPS Rule

**CRITICAL REQUIREMENT**: NEVER allow two agents to write to the same file or directory.

This is a **non-negotiable requirement** for parallel agent operations. Overlaps cause:
- File conflicts when agents modify the same file
- Lost work when one agent overwrites another's changes
- Confusion about which agent is responsible for what
- Race conditions in git commits

**Enforcement**: Runtime validation crashes system if overlaps detected (34+ tests).

### 1.2 NO PARENT DIRECTORY OWNERSHIP

**NO agent can own a parent directory when subdirectories have different owners.**

**Examples**:

```
❌ WRONG: project_manager owns docs/ AND architect owns docs/architecture/ → OVERLAP!
✅ CORRECT: project_manager owns docs/roadmap/, architect owns docs/architecture/ → NO overlap
```

**Rationale**: Parent directory ownership would create implicit overlap with subdirectory ownership.

### 1.3 Complete Ownership Matrix

**File/Directory Ownership** (NO OVERLAPS):

| Path | Owner | Permissions | Others |
|------|-------|-------------|--------|
| **docs/*.md** | project_manager | Top-level files ONLY | READ-ONLY |
| **docs/roadmap/** | project_manager | Full control | READ-ONLY |
| **docs/roadmap/ROADMAP.md** | project_manager (strategy), code_developer (status) | PM: Strategic, CD: Status only | READ-ONLY |
| **docs/architecture/** | architect | Technical specs, ADRs, guidelines | READ-ONLY |
| **docs/refacto/** | code-sanitizer | Refactoring recommendations | READ-ONLY |
| **docs/generator/** | generator (ACE) | Execution traces | READ-ONLY |
| **docs/reflector/** | reflector (ACE) | Delta items (insights) | READ-ONLY |
| **docs/curator/** | curator (ACE) | Playbooks | READ-ONLY |
| **docs/templates/** | project_manager | Documentation templates | READ-ONLY |
| **docs/code-searcher/** | project_manager | Code analysis docs | code-searcher prepares (READ-ONLY) |
| **docs/user_interpret/** | project_manager | Meta-docs ABOUT user_interpret | READ-ONLY |
| **docs/code_developer/** | project_manager | Meta-docs ABOUT code_developer | READ-ONLY |
| **pyproject.toml** | architect | Dependency management (user approval required) | READ-ONLY |
| **poetry.lock** | architect | Dependency lock | READ-ONLY |
| **.gemini.styleguide.md** | code-sanitizer | Code quality guidelines | READ-ONLY |
| **.claude/** | code_developer | Technical configurations | READ-ONLY |
| **coffee_maker/** | code_developer | All implementation | READ-ONLY |
| **tests/** | code_developer | All test code | READ-ONLY |
| **scripts/** | code_developer | Utility scripts | READ-ONLY |
| **.pre-commit-config.yaml** | code_developer | Pre-commit hooks | READ-ONLY |
| **data/user_interpret/** | user_interpret | Operational data | READ-ONLY |

**NO agent owns**:
- `docs/` (parent directory - would create overlaps)

### 1.4 Correct Ownership Patterns

**✅ Correct Examples**:

```python
# User: "Fix bug in roadmap_cli.py"
# Flow: user_listener → assistant → code_developer (owns coffee_maker/)

# User: "Update ROADMAP with new priority"
# Flow: user_listener → assistant → project_manager (owns docs/roadmap/)

# User: "Add new dependency: requests"
# Flow: user_listener → architect (asks user approval) → architect runs poetry add
```

**❌ Incorrect Examples (Don't Do This)**:

```python
# assistant tries to edit code
→ NO! code_developer owns ALL code changes

# assistant tries to update ROADMAP.md
→ NO! project_manager owns docs/ subdirectories

# project_manager tries to modify coffee_maker/cli/roadmap_cli.py
→ NO! code_developer owns coffee_maker/ directory

# code_developer tries to create technical specs in docs/
→ NO! project_manager owns docs/ subdirectories

# code_developer tries to add dependencies
→ NO! architect manages dependencies (with user approval)

# project_manager tries to create a PR
→ NO! code_developer creates PRs autonomously
```

### 1.5 Shared Write Exception: ROADMAP.md

**Special Case**: `docs/roadmap/ROADMAP.md` has shared write with **clear field boundaries**:

- **project_manager**: Strategic updates (add/remove priorities, change order, modify descriptions)
- **code_developer**: Status updates only (Planned → In Progress → Complete, progress percentages)

**No overlap** because different fields are modified.

### 1.6 Enforcement Implementation

**Reference**: `coffee_maker/autonomous/document_ownership.py`

```python
class DocumentOwnershipGuard:
    """Enforces document ownership rules at runtime."""

    OWNERSHIP_RULES: Dict[str, Set[str]] = {
        "docs/roadmap/": {"project_manager"},
        "docs/architecture/": {"architect"},
        "coffee_maker/": {"code_developer"},
        # ... full ownership map
    }

    @classmethod
    def assert_can_write(cls, agent_name: str, file_path: str):
        """Raises PermissionError if agent doesn't own file."""
        # Crashes system if ownership violated
```

**Startup Validation**: Module validates on import (catches overlaps before operations run).

### 1.7 Testing Requirements

**34+ Tests** verify ownership (Reference: `tests/unit/test_document_ownership.py`):

```python
def test_no_overlapping_ownership_critical():
    """CRITICAL: Verify NO overlaps in ownership rules."""
    guard = DocumentOwnershipGuard()
    violations = guard.validate_no_overlaps()
    assert len(violations) == 0

def test_project_manager_cannot_write_code():
    """project_manager CANNOT write to code files."""
    assert not DocumentOwnershipGuard.can_write(
        "project_manager", "coffee_maker/cli/test.py"
    )

def test_code_developer_cannot_modify_dependencies():
    """code_developer CANNOT modify pyproject.toml."""
    with pytest.raises(PermissionError):
        DocumentOwnershipGuard.assert_can_write(
            "code_developer", "pyproject.toml"
        )
```

**All tests MUST pass** before deployment.

---

## 2. Git Workflow Requirements (CRITICAL)

### 2.1 Single Branch Workflow

**CRITICAL**: ALL agents work on `roadmap` branch ONLY.

**Rules**:
- **NO branch switching** between agents
- **NO feature branches** for agent work
- **Tags for milestones**: code_developer uses tags, not branches
- **NO merge conflicts**: Single branch eliminates synchronization issues

**Enforcement**: GitStrategy module enforces roadmap branch.

**Rationale**: Branch switching caused synchronization problems between agents. Single branch solved this permanently.

### 2.2 Branch Protection

**Branch**: `roadmap`

**Protection Rules**:
- Direct commits allowed (agents commit directly)
- No branch switching required
- Linear history preferred
- Tags mark important milestones

### 2.3 Commit Message Format

**Required Format**:

```
<type>: <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation changes
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Example**:

```
feat: US-015 Phase 3 - Add /metrics command for detailed tracking

Implemented detailed metrics tracking with velocity and accuracy
calculations per the technical specification.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 2.4 Pre-commit Hooks

**Required Hooks** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
        args: [--line-length=120]

  - repo: https://github.com/PyCQA/autoflake
    hooks:
      - id: autoflake
        args: [--remove-all-unused-imports, --in-place]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

**All hooks MUST pass** before commit succeeds.

### 2.5 Tag-Based Milestones

**Format**: `v{priority_number}` or `milestone-{name}`

**Examples**:
- `v021-refactoring-complete`
- `milestone-ace-integration`

**Usage**: code_developer tags completed priorities.

---

## 3. Agent Boundaries Requirements

### 3.1 User Interface Ownership

**user_listener** - PRIMARY USER INTERFACE

**CRITICAL**: user_listener is the ONLY agent with UI.

**Responsibilities**:
- ONLY agent with UI
- Interprets user intent
- Routes to backend agents
- Chat interface, CLI interaction
- ALL user requests start here

**ALL other agents are backend-only** (NO UI).

### 3.2 Agent Roles and Boundaries

**assistant** - Documentation Expert + Intelligent Dispatcher
- **Role**: Routes requests to appropriate agents
- **Knowledge**: Deep understanding of ALL project documentation
- **Approach**: Handles quick questions, delegates complex tasks
- **Access**: READ-ONLY on all files
- **NEVER modifies**: Code or docs (always delegates)

**architect** - Strategic Architecture & Roadmap Optimization

**Role**: Strategic architectural oversight (NOT tactical implementation)

**Key Philosophy**: Takes a step back - analyzes ENTIRE roadmap and ENTIRE codebase (big picture)

**Responsibilities**:
- **Strategic Analysis**: Analyzes ENTIRE roadmap and ENTIRE codebase (big picture)
- **Roadmap Optimization**: Identifies implementation synergies, recommends priority reordering
- **Value Maximization**: Helps project_manager ship maximum value per timeframe
- **Technical Specifications**: Creates architectural designs before implementation
- **Dependency Management**: ONLY agent that runs `poetry add` (requires user approval)

**Owns**:
- `docs/architecture/` (specs, ADRs, guidelines, synergies)
- `pyproject.toml`, `poetry.lock`

**Workflow**: Works BEFORE code_developer (strategic design + priority optimization)

**Key Distinction**:
- architect = STRATEGIC (step back, see patterns, optimize priorities)
- code_developer = TACTICAL (focus on next priority, execute design)

**Impact on Prioritization**:
- architect can recommend moving priorities up/down
- architect identifies "quick wins" after foundational work
- architect estimates time savings from synergies
- project_manager adjusts ROADMAP based on architect's analysis

**Example**: If architect identifies that implementing US-034 makes US-042 trivial,
architect advises project_manager to move US-042 immediately after US-034

**code_developer** - Autonomous Implementation (TACTICAL)

**Role**: Executes all code changes (TACTICAL execution, not strategic planning)

**Key Philosophy**: Focus on next priority - implement what architect designed

**Owns**:
- `coffee_maker/`, `tests/`, `scripts/`, `.claude/`

**Responsibilities**:
- **ALL code changes**: Implementation in coffee_maker/, tests/, scripts/
- **Test writing**: Comprehensive test coverage
- **Create PRs autonomously**: No waiting for approvals
- **Update ROADMAP status**: Planned → In Progress → Complete
- **DoD verification** (during implementation)
- **Works AFTER architect**: Follows strategic design

**Key Distinction**:
- code_developer = TACTICAL (next priority, focused execution)
- architect = STRATEGIC (entire roadmap, entire codebase, synergies)

**CANNOT**:
- Analyze entire roadmap for synergies (that's architect)
- Optimize priority ordering (that's architect + project_manager)
- Modify dependencies (must request architect)
- Create technical specs (that's project_manager or architect)
- Monitor project health (that's project_manager)
- Make strategic decisions (that's project_manager)

**code-sanitizer** - Code Quality Monitoring
- **Role**: Analyze code quality, detect refactoring opportunities
- **Owns**: docs/refacto/, .gemini.styleguide.md
- **Trigger**: Wakes automatically when code_developer commits
- **Authority**: Generates refactoring recommendations for project_manager
- **Access**: READ-ONLY on coffee_maker/

**project_manager** - Strategic Oversight
- **Role**: Project coordination and documentation
- **Owns**: docs/*.md, docs/roadmap/, docs/templates/, docs/code-searcher/
- **Authority**: Strategic ROADMAP decisions, technical specs, GitHub monitoring
- **CANNOT**: Write implementation code, create PRs

**code-searcher** - Deep Codebase Analysis
- **Role**: Security audits, dependency tracing, pattern analysis
- **Access**: READ-ONLY entire codebase
- **Output**: Findings presented to assistant → delegated to project_manager for docs

**ux-design-expert** - UI/UX Design
- **Role**: Design decisions, Tailwind CSS, charts
- **Output**: Design specifications (does not implement)

**ACE Framework** - Continuous Learning
- **generator**: Captures execution traces → docs/generator/
- **reflector**: Extracts insights → docs/reflector/
- **curator**: Maintains evolving playbooks → docs/curator/

### 3.3 Decision Tree: Which Agent?

```
User Request → user_listener (PRIMARY UI) → Backend Agent

Backend Agent Selection:
- User interaction? → user_listener (ONLY with UI)
- Quick question? → assistant (answers using docs knowledge)
- Code changes? → code_developer (coffee_maker/, tests/, scripts/)
- Documentation? → project_manager (docs/ subdirectories)
- Architectural design? → architect (docs/architecture/, dependencies)
- Code quality? → code-sanitizer (analysis and recommendations)
- Simple search? → assistant (1-2 files)
- Complex analysis? → code-searcher (multiple files, patterns)
- Design decisions? → ux-design-expert (UI/UX, Tailwind)
- GitHub queries? → project_manager (PR status, CI monitoring)
- DoD verification (during)? → code_developer
- DoD verification (post)? → project_manager
- ACE observation? → generator/reflector/curator
```

### 3.4 Delegation Patterns

**Correct Delegation**:

```python
# User: "Add logging to daemon and document it"

user_listener → assistant

assistant:
"This task requires TWO agents:
1. code_developer - Add logging (code changes)
2. project_manager - Document it (docs/ updates)

Let me coordinate..."

[Delegates to code_developer first]
[Then delegates to project_manager for docs]
```

**Incorrect Delegation (Don't Do This)**:

```python
# assistant tries to modify code directly
→ NO! Delegate to code_developer

# assistant tries to update docs directly
→ NO! Delegate to project_manager

# code_developer tries to create technical specs
→ NO! Delegate to project_manager

# project_manager tries to fix code bugs
→ NO! Delegate to code_developer
```

---

## 4. ACE Framework Requirements

### 4.1 ACE Philosophy: Default to Learning

**CRITICAL**: ACE is **ENABLED BY DEFAULT** for ALL agents.

**Philosophy**: "Default to Learning"
- All agents learn from their executions automatically
- Traces captured for reflector analysis
- Playbooks evolve continuously
- System improves over time without manual intervention

### 4.2 ACE Agent Integration

**All autonomous agents MUST inherit from ACEAgent**:

```python
from coffee_maker.autonomous.ace.ace_agent import ACEAgent

class MyAgent(ACEAgent):
    """Agent with automatic trace generation."""

    def __init__(self, agent_name: str):
        super().__init__(agent_name=agent_name)

    def execute(self, task: str):
        # Automatically generates trace on execution
        return self.run(task)
```

**Reference**: `coffee_maker/autonomous/ace/ace_agent.py`

### 4.3 ACE Opt-Out Mechanism

**Environment Variables** (`.env`):

```bash
# ACE is ENABLED by default - only set these to disable
# export ACE_ENABLED_USER_INTERPRET="false"
# export ACE_ENABLED_ASSISTANT="false"
# export ACE_ENABLED_CODE_SEARCHER="false"
# export ACE_ENABLED_CODE_DEVELOPER="false"
# export ACE_ENABLED_PROJECT_MANAGER="false"
# export ACE_ENABLED_USER_LISTENER="false"
# export ACE_ENABLED_ARCHITECT="false"
# export ACE_ENABLED_CODE_SANITIZER="false"
```

**When to Disable**:
- ✅ **Keep enabled** (recommended): user_interpret, assistant, code-searcher, project_manager
- ⚠️ **Consider disabling during development**: code_developer (slow operations 30min-4hr)
- ⚠️ **Consider disabling**: user_listener (UI only, no learning needed)

### 4.4 ACE Directory Structure

**Required Directories**:

```
docs/
├── generator/
│   ├── README.md
│   └── traces/       # Execution traces (generated automatically)
├── reflector/
│   ├── README.md
│   └── deltas/       # Insights extracted from traces
└── curator/
    ├── README.md
    └── playbooks/    # Evolving playbooks for agents
```

**Ownership**: Each ACE component owns its own directory exclusively.

### 4.5 ACE Configuration

**Environment Variables** (`.env`):

```bash
export ACE_AUTO_REFLECT="false"  # Auto-run reflector after executions
export ACE_AUTO_CURATE="false"  # Auto-run curator after reflection
export ACE_TRACE_DIR="docs/generator/traces"
export ACE_DELTA_DIR="docs/reflector/deltas"
export ACE_PLAYBOOK_DIR="docs/curator/playbooks"
export ACE_SIMILARITY_THRESHOLD="0.85"  # Semantic similarity (0.0-1.0)
export ACE_PRUNING_RATE="0.10"  # Percentage of bullets to prune
export ACE_MIN_HELPFUL_COUNT="2"  # Minimum helpful count to avoid pruning
export ACE_MAX_BULLETS="150"  # Maximum playbook size
export ACE_REFLECT_BATCH_SIZE="5"  # Traces per batch
export ACE_EMBEDDING_MODEL="text-embedding-ada-002"  # OpenAI embedding
```

### 4.6 ACE Workflow

**Playbook Curation Workflow**:

```
1. Agent executes task
   ↓
2. ACEAgent generates trace (JSON) → docs/generator/traces/
   ↓
3. Reflector analyzes traces → Extracts insights → docs/reflector/deltas/
   ↓
4. Curator updates playbooks → docs/curator/playbooks/
   ↓
5. Agent uses updated playbook for next execution
   ↓
[Continuous improvement loop]
```

---

## 5. Dependency Management Requirements

### 5.1 Architect-Only Dependency Management

**CRITICAL**: ONLY architect can run `poetry add`.

**Ownership**:
- **pyproject.toml**: architect ONLY
- **poetry.lock**: architect ONLY
- **code_developer**: CANNOT modify dependencies

**Enforcement**: Runtime ownership validation (PermissionError raised).

### 5.2 Dependency Approval Workflow

**Required Workflow**:

```
1. architect analyzes need for new dependency
   ↓
2. architect requests user approval via user_listener
   ↓
3. User approves/rejects
   ↓
4. If approved: architect runs poetry add [package]
   ↓
5. architect documents decision in ADR (Architectural Decision Record)
```

**Example**:

```bash
# User: "Add authentication system"

user_listener → architect

architect:
"I need to add PyJWT for JWT authentication.
This adds a new dependency. Do you approve?"

[User approves]

architect:
$ poetry add pyjwt

architect creates:
docs/architecture/decisions/ADR-005-jwt-vs-session.md
```

### 5.3 Dependency Documentation

**Required Documentation** (architect creates):

```
docs/architecture/decisions/ADR-{number}-{dependency-decision}.md

Example:
- ADR-005-jwt-vs-session.md
- ADR-006-add-pyjwt-dependency.md
```

**Content**:
- Why the dependency is needed
- Alternatives considered
- User approval timestamp
- Impact analysis

### 5.4 Dependency Security

**Requirements**:
- All dependencies must be from trusted sources (PyPI)
- architect must review security implications
- User approval required for ALL new dependencies
- Regular dependency audits (quarterly)

**Tools**:
- `poetry show --outdated` (check for updates)
- `safety check` (security vulnerabilities)
- `pip-audit` (alternative security check)

---

## 6. Testing Requirements

### 6.1 Test Coverage Requirements

**Required Coverage**:
- **Overall**: ≥ 70% code coverage
- **Core modules**: ≥ 80% code coverage
- **Critical paths**: 100% code coverage

**Critical Modules** (100% coverage required):
- `coffee_maker/autonomous/document_ownership.py`
- `coffee_maker/autonomous/daemon.py`
- `coffee_maker/cli/roadmap_cli.py`

### 6.2 Ownership Tests

**34+ Tests** verify ownership rules (Reference: `tests/unit/test_document_ownership.py`).

**Critical Test**:

```python
def test_no_overlapping_ownership_critical():
    """CRITICAL: Verify NO overlaps in ownership rules.

    This is the MOST IMPORTANT test - overlaps break parallel operations.
    """
    guard = DocumentOwnershipGuard()
    violations = guard.validate_no_overlaps()

    assert len(violations) == 0, (
        f"CRITICAL: Ownership overlaps detected:\n" +
        "\n".join(violations)
    )
```

**All ownership tests MUST pass** before deployment.

### 6.3 Test Structure

**Required Test Organization**:

```
tests/
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_document_ownership.py  # 34+ ownership tests
│   ├── test_daemon.py
│   └── test_roadmap_cli.py
├── ci_tests/            # Integration tests (CI/CD)
│   ├── test_integration.py
│   └── test_end_to_end.py
└── conftest.py          # Pytest fixtures
```

### 6.4 Testing Commands

**Run Tests**:

```bash
# All tests
pytest

# Unit tests only (fast)
pytest tests/unit/

# Ownership tests only (critical)
pytest tests/unit/test_document_ownership.py

# With coverage
pytest --cov=coffee_maker --cov-report=html

# Specific test
pytest tests/unit/test_document_ownership.py::test_no_overlapping_ownership_critical
```

### 6.5 Continuous Testing

**Pre-commit**: Tests run automatically via pre-commit hooks
**CI/CD**: Tests run on every commit (GitHub Actions)
**Local**: Developers run tests before committing

---

## 7. Documentation Requirements

### 7.1 Documentation Ownership

**Strategic Documentation** (project_manager owns):
- `docs/*.md` (top-level files)
- `docs/roadmap/` (ROADMAP.md, TEAM_COLLABORATION.md)
- `docs/templates/` (documentation templates)
- `docs/code-searcher/` (code analysis reports)
- `docs/user_interpret/` (meta-docs about user_interpret)
- `docs/code_developer/` (meta-docs about code_developer)

**Technical Documentation** (architect owns):
- `docs/architecture/specs/` (technical specifications)
- `docs/architecture/decisions/` (Architectural Decision Records)
- `docs/architecture/guidelines/` (implementation guidelines)

**ACE Documentation** (ACE components own):
- `docs/generator/` (generator)
- `docs/reflector/` (reflector)
- `docs/curator/` (curator)

### 7.2 Documentation Standards

**Required Documentation**:
- Every priority needs technical spec (docs/PRIORITY_X_TECHNICAL_SPEC.md)
- Every architectural decision needs ADR (docs/architecture/decisions/)
- Every agent needs definition file (.claude/agents/)
- Every prompt needs centralized file (.claude/commands/)

**Documentation Format**:
- Markdown (.md) for all documentation
- Clear headings and structure
- Code examples where applicable
- Version history at bottom
- Last updated date
- Maintained by field

### 7.3 Documentation Workflow

**Code Analysis Documentation**:

```
1. code-searcher performs analysis (READ-ONLY)
   ↓
2. code-searcher prepares findings report
   ↓
3. code-searcher presents to assistant
   ↓
4. assistant delegates to project_manager
   ↓
5. project_manager creates docs/code-searcher/[analysis]_[date].md
```

**Format**: `docs/code-searcher/[analysis_type]_analysis_[date].md`

**Examples**:
- `docs/code-searcher/security_audit_2025-10-15.md`
- `docs/code-searcher/dependency_analysis_2025-10-15.md`

### 7.4 Documentation Maintenance

**Quarterly Reviews**:
- project_manager reviews all strategic docs
- architect reviews all technical docs
- Update outdated information
- Remove deprecated content
- Verify ownership rules still accurate

---

## 8. Code Quality Requirements

### 8.1 Code Style

**Formatter**: Black (enforced by pre-commit hooks)

```bash
# Format code
black .

# Check formatting
black --check .
```

**Configuration**:
- Line length: 120 characters (Black default: 88)
- Python 3.11+
- Type hints encouraged

### 8.2 Code Metrics Thresholds

**Reference**: `.gemini.styleguide.md` (owned by code-sanitizer)

**Complexity Thresholds**:
- **Cyclomatic Complexity**: ≤ 10 per function (warning at 10, error at 15)
- **Cognitive Complexity**: ≤ 15 per function
- **Lines of Code**: ≤ 50 per function, ≤ 300 per file

**Duplication**:
- **Code duplication**: ≤ 3% of codebase
- **Similar functions**: Extract to shared utility

### 8.3 Refactoring Triggers

**High Priority** (Immediate):
- Cyclomatic complexity > 15
- Function length > 100 lines
- Duplicated code blocks > 20 lines
- Security vulnerabilities
- Performance bottlenecks (>1s execution)

**Medium Priority** (Next sprint):
- Cyclomatic complexity 10-15
- Function length 50-100 lines
- Missing type hints
- Poor test coverage (<70%)
- Unclear naming

**Low Priority** (Backlog):
- Minor style inconsistencies
- Optimization opportunities
- Documentation improvements
- Code comments cleanup

### 8.4 Code Quality Monitoring

**code-sanitizer Workflow**:

```
1. code_developer commits code
   ↓
2. code-sanitizer wakes automatically
   ↓
3. Analyzes:
   - Complexity (radon)
   - Style (flake8)
   - Duplication
   - .gemini.styleguide.md compliance
   ↓
4. Generates report: docs/refacto/refactoring_analysis_YYYY-MM-DD.md
   ↓
5. project_manager reviews report
   ↓
6. Decision: Create refactoring priority OR continue with features
```

### 8.5 Type Hints

**Required** for:
- All public functions
- All class methods
- All function arguments
- All return values

**Example**:

```python
from typing import List, Dict, Optional

def calculate_total(
    prices: List[float],
    tax_rate: float,
    discount: Optional[float] = None
) -> float:
    """Calculate total price with tax and discount."""
    subtotal = sum(prices)
    if discount:
        subtotal *= (1 - discount)
    return subtotal * (1 + tax_rate)
```

### 8.6 Error Handling

**Required**:
- Defensive programming (validate inputs)
- Handle None gracefully
- Clear error messages
- Specific exception types

**Example**:

```python
def load_config(path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")
```

---

## 9. Prompt Management Requirements

### 9.1 Centralized Prompt Management

**CRITICAL**: ALL prompts MUST be in `.claude/commands/`.

**Location**: `.claude/commands/*.md`

**Format**: Markdown files with `$VARIABLE_NAME` placeholders

**Example**:

```markdown
# File: .claude/commands/implement-feature.md

Implement $PRIORITY_NAME according to the technical specification.

**Requirements**:
- Read docs/$SPEC_FILENAME
- Implement in $MODULE_PATH
- Write tests in tests/

**Context**:
$PRIORITY_CONTEXT
```

### 9.2 Prompt Loading API

**Reference**: `coffee_maker/autonomous/prompt_loader.py`

**Usage**:

```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

# Load prompt with variables
prompt = load_prompt(
    PromptNames.IMPLEMENT_FEATURE,
    {
        "PRIORITY_NAME": "US-021",
        "SPEC_FILENAME": "US_021_TECHNICAL_SPEC.md",
        "MODULE_PATH": "coffee_maker/autonomous/",
        "PRIORITY_CONTEXT": "Split daemon.py into smaller files..."
    }
)
```

### 9.3 Adding New Prompts

**Workflow**:

```bash
# 1. Create prompt file
cat > .claude/commands/my-new-prompt.md << 'EOF'
Do something with $VARIABLE_NAME.

Instructions:
- Step 1
- Step 2

Context:
$CONTEXT
EOF

# 2. Add to PromptNames (prompt_loader.py)
class PromptNames:
    MY_NEW_PROMPT = "my-new-prompt"

# 3. Use in code
prompt = load_prompt(PromptNames.MY_NEW_PROMPT, {
    "VARIABLE_NAME": value,
    "CONTEXT": context
})
```

### 9.4 Prompt Management Phases

**Phase 1** (✅ Complete):
- Local centralization in `.claude/commands/`
- PromptLoader utility
- All code uses centralized prompts

**Phase 2** (📝 Planned):
- Langfuse integration as source of truth
- `.claude/commands/` becomes local cache
- Full observability of all executions
- A/B testing of prompt variations

**Reference**: `docs/PROMPT_MANAGEMENT_SYSTEM.md`

### 9.5 Multi-AI Provider Support

**Goal**: Prompts work with ANY AI provider.

**Supported Providers**:
- Claude (current)
- Gemini (future)
- OpenAI (future)

**Provider-Agnostic Design**: Same prompts work with all providers (just swap provider class).

---

## 10. Security Requirements

### 10.1 API Key Management

**CRITICAL**: NEVER commit API keys to git.

**Storage**:
- `.env` file (local, NOT committed)
- `.env.example` as template (committed)
- `.env` already in `.gitignore`

**Required Keys** (`.env`):

```bash
# Anthropic Claude API (REQUIRED)
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# LangFuse (Analytics)
export LANGFUSE_SECRET_KEY="sk-lf-your-secret-key-here"
export LANGFUSE_PUBLIC_KEY="pk-lf-your-public-key-here"

# OpenAI API (Optional)
export OPENAI_API_KEY="sk-proj-your-key-here"

# Google Gemini API (Optional)
export GEMINI_API_KEY="your-gemini-key-here"

# GitHub Token (Optional)
export GITHUB_TOKEN="ghp_your-github-token-here"
```

### 10.2 Security Best Practices

**✅ DO**:
- Keep .env file private and local
- Use .env.example as template
- Rotate API keys periodically (every 90 days)
- Use separate keys for development and production
- Store keys in password manager

**❌ DON'T**:
- Commit .env to git (already in .gitignore)
- Share API keys in chat, email, or screenshots
- Use production keys in development
- Hard-code keys in source code
- Copy .env to public locations

### 10.3 Key Rotation

**Frequency**: Every 90 days (minimum)

**Process**:

```bash
# 1. Generate new key in provider console
# 2. Update .env file
# 3. Test with new key
# 4. Revoke old key in provider console
# 5. Document rotation date
```

### 10.4 Exposed Key Response

**If you accidentally expose a key**:

```bash
# 1. IMMEDIATELY revoke key in provider console
# 2. Remove from git history
git rm --cached .env

# 3. Generate new key
# 4. Update local .env file
# 5. Check git history
git log --all -- .env

# 6. If committed to git, force push (DANGEROUS)
# Better: Rotate key and move on
```

### 10.5 Security Audits

**Regular Audits**:
- code-searcher performs security analysis
- Checks for hardcoded secrets
- Reviews dependency vulnerabilities
- Analyzes authentication/authorization code

**Tools**:
- `bandit` (Python security linter)
- `safety check` (dependency vulnerabilities)
- `pip-audit` (alternative security check)

---

## Enforcement Mechanisms

### 1. Runtime Validation

**DocumentOwnershipGuard** (startup validation):

```python
# Runs on module import - crashes if overlaps detected
def _validate_ownership_on_import():
    """Validate ownership rules on module import."""
    violations = DocumentOwnershipGuard.validate_no_overlaps()

    if violations:
        error_msg = "CRITICAL: Ownership overlaps detected:\n" + "\n".join(violations)
        raise RuntimeError(error_msg)
```

**Result**: System crashes on startup if ownership rules have overlaps.

### 2. Pre-commit Hooks

**Enforced Checks** (`.pre-commit-config.yaml`):
- Black formatting (120 char line length)
- Autoflake (remove unused imports)
- Trailing whitespace removal
- End-of-file fixer

**All hooks MUST pass** before commit succeeds.

### 3. Test Suite

**34+ Ownership Tests**:
- Verify NO overlaps
- Verify correct permissions
- Verify agent boundaries
- Test error handling

**Continuous Testing**: Tests run on every commit (pre-commit + CI/CD).

### 4. Documentation Reviews

**Quarterly Reviews** (project_manager):
- Review ownership matrix
- Check for new overlaps
- Update documentation
- Verify enforcement working

### 5. Code Quality Monitoring

**Automatic Monitoring** (code-sanitizer):
- Wakes on every code_developer commit
- Analyzes complexity, duplication, style
- Generates refactoring recommendations
- Reports to project_manager

---

## Verification Checklist

**Run this checklist when adding new agents or directories**:

- [ ] Each directory has EXACTLY one owner
- [ ] Each file has EXACTLY one owner
- [ ] NO shared write access (except ROADMAP.md with field boundaries)
- [ ] NO parent directory ownership (when subdirs have different owners)
- [ ] All agents know their owned directories
- [ ] Ownership documented in this file and DOCUMENT_OWNERSHIP_MATRIX.md
- [ ] Tests enforce ownership rules (34+ tests pass)
- [ ] Runtime validation passes (no overlaps detected)
- [ ] Pre-commit hooks configured
- [ ] Documentation updated

---

## Related Documentation

**Primary References**:
- `docs/DOCUMENT_OWNERSHIP_MATRIX.md` - Complete ownership details
- `docs/roadmap/TEAM_COLLABORATION.md` - Team collaboration workflows
- `docs/PROMPT_MANAGEMENT_SYSTEM.md` - Prompt management system
- `.claude/CLAUDE.md` - Project overview and instructions
- `.env.example` - Environment variables template
- `.gemini.styleguide.md` - Code quality guidelines

**Implementation References**:
- `coffee_maker/autonomous/document_ownership.py` - Ownership enforcement
- `tests/unit/test_document_ownership.py` - Ownership tests
- `coffee_maker/autonomous/prompt_loader.py` - Prompt loading
- `coffee_maker/autonomous/ace/ace_agent.py` - ACE integration

---

## Version History

**v1.0 (2025-10-15)** - Initial comprehensive requirements document
- Consolidated all critical rules from multiple sources
- 10 major requirement categories
- Enforcement mechanisms documented
- Verification checklist provided
- Complete ownership matrix
- Git workflow requirements
- Agent boundaries clearly defined
- ACE framework requirements
- Dependency management workflow
- Testing, documentation, code quality standards
- Prompt management system
- Security requirements

---

**Maintained By**: project_manager
**Review Frequency**: Quarterly or when adding new agents/requirements
**Next Review**: 2026-01-15
**Status**: Active (all requirements enforced)
