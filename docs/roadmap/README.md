# docs/roadmap/ - Project Management Documentation

## Directory Ownership

**Owner**: project_manager agent

This directory is EXCLUSIVELY owned by the project_manager agent for strategic project planning and management.

## What Belongs Here

### Core Files
- **ROADMAP.md** - Master task list, priorities, status tracking (THE critical file)
- **TEAM_COLLABORATION.md** - Agent interaction patterns and collaboration guidelines

### Strategic Specifications
- **PRIORITY_*_STRATEGIC_SPEC.md** - High-level strategic specifications created by project_manager
  - Focus: Business requirements, user stories, acceptance criteria
  - Scope: What and why, not how
  - Example: PRIORITY_2_STRATEGIC_SPEC.md

### Subdirectories
- **learnings/** - Project learnings, retrospectives, post-mortems
  - Example: OWNERSHIP_VIOLATION_US_038.md

## What Does NOT Belong Here

### Technical Specifications
- **US_*_TECHNICAL_SPEC.md** - Belongs in docs/architecture/user_stories/ (architect's responsibility)
- **SPEC-*.md** - Belongs in docs/architecture/specs/ (architect's responsibility)

### Architectural Documentation
- **ADR-*.md** - Belongs in docs/architecture/decisions/ (architect's responsibility)
- **GUIDELINE-*.md** - Belongs in docs/architecture/guidelines/ (architect's responsibility)

### Implementation Documentation
- **Code documentation** - Belongs in coffee_maker/ (code_developer's responsibility)
- **Agent configurations** - Belongs in .claude/agents/ (code_developer's responsibility)

## Naming Conventions

### Strategic Specifications
Format: `PRIORITY_X_STRATEGIC_SPEC.md` or `PRIORITY_X_Y_STRATEGIC_SPEC.md`

Examples:
- PRIORITY_2_STRATEGIC_SPEC.md
- PRIORITY_4_1_STRATEGIC_SPEC.md

### Learnings
Format: `[type]_[identifier].md`

Examples:
- OWNERSHIP_VIOLATION_US_038.md
- RETROSPECTIVE_2025_Q4.md
- POSTMORTEM_DAEMON_CRASH.md

## Strategic vs Technical Specs

### Strategic Spec (project_manager)
Focus: Business and project management perspective
- User stories and acceptance criteria
- Business requirements and goals
- Timeline and milestones
- Resource allocation
- Risk assessment

### Technical Spec (architect)
Focus: Implementation and architectural perspective
- System design and architecture
- Technology choices and justification
- Implementation approach
- Technical dependencies
- Performance requirements

## Access Control

### project_manager
- **Can modify**: All files in docs/roadmap/
- **Can create**: Strategic specs, learnings, planning docs
- **Responsibility**: Keep ROADMAP.md up-to-date

### Other Agents
- **Can read**: All files (READ-ONLY)
- **Cannot modify**: Any files in this directory
- **Must delegate**: Requests for changes to project_manager

## Git Operations

All changes to this directory should:
1. Be made by project_manager agent only
2. Use descriptive commit messages
3. Reference related priorities/issues
4. Preserve git history (use git mv for renames)

## Related Directories

- **docs/architecture/** - Owned by architect (technical specs, ADRs, guidelines)
- **docs/generator/** - Owned by generator (execution traces)
- **docs/reflector/** - Owned by reflector (insights and deltas)
- **docs/curator/** - Owned by curator (playbooks)
- **.claude/** - Owned by code_developer (agent configs, prompts)

## Questions?

Refer to:
- **.claude/CLAUDE.md** - Project overview and agent roles
- **docs/DOCUMENT_OWNERSHIP_MATRIX.md** - Complete ownership matrix
- **TEAM_COLLABORATION.md** - Agent interaction patterns

---

Last Updated: 2025-10-16
Version: 1.0
