# SPEC-061: spec-creation-automation Skill

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-18

**Last Updated**: 2025-10-18

**Related**:
- docs/architecture/specs/PROPOSED_SKILLS_2025-10-18.md (lines 285-381)
- SPEC-047: Architect-Only Spec Creation Enforcement
- ADR-009: Retire code-searcher agent, replace with skills

**Related ADRs**: ADR-009

**Assigned To**: code_developer

**Estimated Effort**: 10 hours

**Priority**: CRITICAL (Phase 1)

---

## Executive Summary

The spec-creation-automation skill automates 78% of technical specification creation, reducing architect's time from 117 minutes to 25 minutes per spec (92-minute savings). This skill saves 23-30.7 hours per month by automatically populating spec templates, discovering relevant code, analyzing dependencies, estimating implementation time, and identifying risks. The skill integrates seamlessly with the architect agent workflow and leverages existing Code Index infrastructure for accurate code discovery.

**Impact**: **23-30.7 hours/month saved** (highest impact skill after context-budget-optimizer)

**ROI**: 2.3-3.1x return in first month

---

## Problem Statement

### Current Situation

Creating technical specifications is the most time-consuming task for the architect agent, consuming:

- **Time per spec**: 82-152 minutes (avg: 117 minutes = 2 hours)
- **Frequency**: 15-20 specs per month
- **Monthly impact**: 23.4-39 hours wasted on repetitive boilerplate work

**Breakdown of 117 minutes**:
1. Read ROADMAP priority (5 min)
2. Search codebase for related code (15-30 min) ← **MANUAL, REPETITIVE**
3. Analyze dependencies and impacts (20-40 min) ← **MANUAL, REPETITIVE**
4. Draft technical spec (30-60 min) ← **MOSTLY BOILERPLATE**
5. Format spec to template (10-15 min) ← **MANUAL, REPETITIVE**
6. Save to docs/architecture/specs/ (2 min)

**Pain Points**:
- **Repetitive template creation**: Same structure every time, yet manually filled
- **Manual codebase search**: Multiple grep/Glob iterations to find all related code
- **Dependency analysis**: Manual import tracing, easy to miss transitive dependencies
- **Format enforcement**: Easy to miss template sections, inconsistent formatting
- **Time estimation guesswork**: No data-driven approach, estimates often ±50% off

### Goal

Reduce spec creation time from **117 minutes → 25 minutes** (78% reduction) by automating:
- Template auto-population from ROADMAP priority
- Code discovery using functional search
- Dependency analysis with import tracing
- Time estimation using historical data
- Risk identification with pattern-based heuristics

**Target**: architect spends only 25 minutes reviewing and adding architectural insights (20% of original time)

### Non-Goals

- ❌ **Fully automated spec generation**: architect MUST review and approve (human judgment required)
- ❌ **AI-based spec quality scoring**: Too complex for Phase 1, defer to future
- ❌ **Cross-spec dependency graphs**: Advanced feature, not needed for MVP
- ❌ **Automatic spec updates**: When ROADMAP changes, manual updates for now

---

## Requirements

### Functional Requirements

1. **FR-1**: Template Auto-Population
   - Extract priority details from ROADMAP.md (name, description, acceptance criteria)
   - Pre-fill spec template sections (Overview, Problem Statement, Requirements)
   - Generate spec filename following convention (SPEC-XXX-feature-name.md)
   - Apply standard metadata (status, author, date, effort estimate)

2. **FR-2**: Code Discovery Engine
   - Search codebase for files/functions related to priority
   - Use Code Index (from SPEC-001) for hierarchical search
   - Extract affected code zones with line numbers
   - Rank files by relevance (primary vs related)
   - Generate "Affected Code Zones" section with code snippets

3. **FR-3**: Dependency Analyzer
   - Parse import statements in affected files
   - Trace transitive dependencies (3 levels deep)
   - Detect circular dependencies (warn architect)
   - Identify external package dependencies (flag for architect approval)
   - Generate dependency graph in Mermaid format

4. **FR-4**: Time Estimator
   - Calculate scope: number of files × complexity × LOC
   - Query historical data (similar priorities from ROADMAP.md)
   - Adjust for architect's past accuracy (learning from feedback)
   - Provide confidence interval (e.g., "6-8 hours, 80% confidence")
   - Break down estimate (implementation, testing, docs, review)

5. **FR-5**: Risk Identification
   - Detect performance risks (N+1 queries, large data processing)
   - Detect security risks (authentication, data validation)
   - Detect scalability risks (single-threaded, memory-intensive)
   - Detect integration risks (external API dependencies)
   - Generate "Risks & Mitigations" section

6. **FR-6**: Spec Formatter
   - Combine all sections into final spec
   - Format markdown (headers, lists, code blocks, tables)
   - Add metadata (status, author, date, effort)
   - Add links to related files/priorities
   - Generate table of contents
   - Validate completeness (all required sections present)

### Non-Functional Requirements

1. **NFR-1**: Performance
   - Spec generation completes in <60 seconds for typical priority
   - Code discovery completes in <30 seconds using Code Index
   - Dependency analysis completes in <20 seconds
   - Total skill execution: <2 minutes

2. **NFR-2**: Accuracy
   - Code discovery: 90%+ precision (finds relevant files, minimal false positives)
   - Dependency analysis: 95%+ recall (finds all dependencies, minimal misses)
   - Time estimates: ±20% of actual time (vs ±50% manual estimates)
   - Risk identification: 80%+ recall (finds most risks, some manual review needed)

3. **NFR-3**: Usability
   - architect invokes skill with single command
   - Clear progress messages (what skill is doing)
   - Human-readable output (markdown format)
   - Actionable next steps (what architect should review)

4. **NFR-4**: Maintainability
   - Skill logic separated into clear components (discovery, analysis, formatting)
   - Configurable thresholds (complexity, dependency depth, time factors)
   - Extensible risk patterns (easy to add new risk types)
   - Well-tested (unit tests for each component)

5. **NFR-5**: Observability
   - Log all skill invocations (priority name, timestamp)
   - Track time savings (actual vs manual baseline)
   - Report accuracy metrics (time estimate vs actual)
   - Alert if skill fails (fallback to manual process)

### Constraints

- **Must use existing Code Index**: From SPEC-001 (architecture-reuse-check skill)
- **Must use existing ROADMAP parser**: coffee_maker/autonomous/cached_roadmap_parser.py
- **Must use existing template**: docs/architecture/specs/SPEC-000-template.md
- **Must integrate with skill_loader.py**: Standard skill invocation pattern
- **Must not require new dependencies**: Use stdlib + existing packages only

---

## Proposed Solution

### High-Level Approach

The spec-creation-automation skill is a multi-stage pipeline that transforms a ROADMAP priority into a 90% complete technical specification:

```
ROADMAP Priority
       ↓
[Stage 1: Template Auto-Population]
       ↓
Partially filled spec (20% complete)
       ↓
[Stage 2: Code Discovery Engine]
       ↓
Spec + affected code zones (40% complete)
       ↓
[Stage 3: Dependency Analyzer]
       ↓
Spec + dependencies graph (60% complete)
       ↓
[Stage 4: Time Estimator]
       ↓
Spec + time estimate (75% complete)
       ↓
[Stage 5: Risk Identifier]
       ↓
Spec + risk analysis (90% complete)
       ↓
[Stage 6: Spec Formatter]
       ↓
Complete formatted spec (ready for architect review)
       ↓
architect reviews (25 min) + adds insights
       ↓
Final approved spec (100% complete)
```

**Key Insight**: Each stage adds value incrementally, so if a stage fails, architect still gets partial spec (better than starting from scratch).

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    architect Agent                          │
│                                                              │
│  User request: "Create spec for PRIORITY 10"                │
│         ↓                                                    │
│  load_skill(SkillNames.SPEC_CREATION_AUTOMATION, {...})     │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────┐      │
│  │     spec-creation-automation.md                  │      │
│  │  (Markdown skill with embedded Python logic)     │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Stage 1: Template Auto-Population        │      │
│  │  - Parse ROADMAP priority                        │      │
│  │  - Extract: name, description, acceptance        │      │
│  │  - Generate spec filename                        │      │
│  │  - Pre-fill template sections                    │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Stage 2: Code Discovery Engine           │      │
│  │  - Load Code Index (SPEC-001)                    │      │
│  │  - Generate search keywords                      │      │
│  │  - Query Code Index hierarchy                    │      │
│  │  - Rank files by relevance                       │      │
│  │  - Extract code snippets                         │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Stage 3: Dependency Analyzer             │      │
│  │  - Parse imports in affected files               │      │
│  │  - Trace transitive dependencies                 │      │
│  │  - Detect circular dependencies                  │      │
│  │  - Identify external packages                    │      │
│  │  - Generate Mermaid diagram                      │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Stage 4: Time Estimator                  │      │
│  │  - Calculate scope (files × LOC × complexity)    │      │
│  │  - Query historical data (ROADMAP.md)            │      │
│  │  - Apply complexity factors                      │      │
│  │  - Generate confidence interval                  │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Stage 5: Risk Identifier                 │      │
│  │  - Pattern matching (performance, security)      │      │
│  │  - Heuristics (complexity, external deps)        │      │
│  │  - Generate risk descriptions                    │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Stage 6: Spec Formatter                  │      │
│  │  - Combine all sections                          │      │
│  │  - Format markdown                               │      │
│  │  - Add metadata                                  │      │
│  │  - Validate completeness                         │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     ↓                                        │
│  Complete spec (90% filled) returned to architect           │
│         ↓                                                    │
│  architect reviews (25 min) + adds architectural insights   │
│         ↓                                                    │
│  architect saves to docs/architecture/specs/SPEC-XXX.md     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

External Dependencies:
┌──────────────────────────┐
│  Code Index              │ ← From SPEC-001 (architecture-reuse-check)
│  (JSON file)             │    Contains hierarchical code structure
└──────────────────────────┘

┌──────────────────────────┐
│  ROADMAP.md              │ ← Parsed by cached_roadmap_parser.py
│  (Markdown file)         │    Contains all priorities
└──────────────────────────┘

┌──────────────────────────┐
│  SPEC-000-template.md    │ ← Standard spec template
│  (Markdown file)         │    Base structure for all specs
└──────────────────────────┘

┌──────────────────────────┐
│  Historical data         │ ← New: data/time_estimates.json
│  (JSON file)             │    Tracks actual vs estimated time
└──────────────────────────┘
```

### Technology Stack

- **Skill format**: Markdown (.md) with embedded instructions
- **Skill loader**: skill_loader.py (existing)
- **LLM integration**: ClaudeCLIInterface (existing, for complex analysis)
- **File operations**: Read, Write, Edit tools (Claude Code built-ins)
- **Code search**: Code Index from SPEC-001 (JSON-based hierarchical search)
- **ROADMAP parsing**: cached_roadmap_parser.py (existing)
- **Template**: SPEC-000-template.md (existing)
- **Data storage**: data/time_estimates.json (new, simple JSON file)

---

## Detailed Design

### Component Design

#### Component 1: Template Auto-Population

**Responsibility**: Extract priority details from ROADMAP and pre-fill spec template

**Inputs**:
- Priority name (e.g., "PRIORITY 10")
- Priority content from ROADMAP.md
- Spec template (SPEC-000-template.md)

**Process**:

```python
def auto_populate_template(priority_name: str, priority_content: str, template: str) -> str:
    """Auto-populate spec template from ROADMAP priority.

    Steps:
        1. Parse priority content to extract:
           - Feature name/title
           - Description/problem statement
           - Acceptance criteria
           - Strategic requirements
           - Dependencies (if mentioned)

        2. Generate spec metadata:
           - Spec number (extract from priority name: "PRIORITY 10" → "SPEC-061")
           - Filename (kebab-case: "User Listener UI" → "user-listener-ui")
           - Author (always "architect agent")
           - Date (today's date)
           - Status ("Draft")

        3. Map extracted data to template sections:
           - Title: Feature name
           - Executive Summary: Description (first 2-3 sentences)
           - Problem Statement → Current Situation: Problem description
           - Requirements → Functional Requirements: Acceptance criteria
           - Related: Link to ROADMAP priority

        4. Replace template placeholders:
           - "[Feature Name]" → Actual feature name
           - "YYYY-MM-DD" → Today's date
           - "Description" → Extracted description
           - etc.

        5. Return partially filled template (20% complete)

    Returns:
        Partially populated spec template (markdown string)

    Example:
        Input priority content:
        '''
        ## PRIORITY 10: User Listener UI

        Create a unified user interface for user_listener agent that handles
        all user interactions (CLI, chat, notifications).

        **Acceptance Criteria**:
        - AC-1: CLI commands work seamlessly
        - AC-2: Chat interface provides real-time responses
        - AC-3: Notifications are delivered with sound

        **Dependencies**: None
        '''

        Output spec (partial):
        '''
        # SPEC-061: User Listener UI

        **Status**: Draft
        **Author**: architect agent
        **Date Created**: 2025-10-18
        **Related**: docs/roadmap/ROADMAP.md (PRIORITY 10)

        ## Executive Summary

        Create a unified user interface for user_listener agent that handles
        all user interactions (CLI, chat, notifications).

        ## Problem Statement

        ### Current Situation

        [architect TO FILL: Describe current state and problems]

        ### Goal

        Create a unified user interface that:
        - Handles CLI commands seamlessly
        - Provides real-time chat responses
        - Delivers notifications with sound

        ## Requirements

        ### Functional Requirements

        1. **FR-1**: CLI commands work seamlessly
        2. **FR-2**: Chat interface provides real-time responses
        3. **FR-3**: Notifications are delivered with sound

        [Rest of template with placeholders for architect to fill...]
        '''
    """
    # Implementation would go here
    pass
```

**Implementation Notes**:
- Use regular expressions to extract sections from ROADMAP priority
- Handle various ROADMAP formats (priorities may have different structures)
- If acceptance criteria missing, leave FR placeholders for architect to fill
- Always mark incomplete sections with "[architect TO FILL: ...]" so architect knows what to complete

**Edge Cases**:
- Priority has no description → Use minimal template, flag for architect review
- Priority references other priorities → Extract dependency links, add to "Related" section
- Priority is vague → Generate generic placeholders, flag as "NEEDS ARCHITECT REVIEW"

---

#### Component 2: Code Discovery Engine

**Responsibility**: Find all relevant code in codebase using Code Index

**Inputs**:
- Feature name (e.g., "User Listener UI")
- Keywords from priority description (e.g., ["user", "listener", "cli", "chat", "notification"])
- Code Index path (from SPEC-001)

**Process**:

```python
def discover_relevant_code(feature_name: str, keywords: list[str], code_index_path: str) -> dict:
    """Discover all code files/functions related to feature.

    Steps:
        1. Load Code Index (JSON file from SPEC-001):
           {
               "modules": [
                   {
                       "name": "coffee_maker.cli.notifications",
                       "path": "coffee_maker/cli/notifications.py",
                       "functions": ["send_notification", "play_sound"],
                       "classes": ["NotificationManager"],
                       "complexity": 8.5,
                       "loc": 245
                   },
                   ...
               ]
           }

        2. Generate search keywords:
           - Extract nouns from feature name: "User Listener UI" → ["user", "listener", "ui"]
           - Include keywords from description
           - Generate code-related terms:
             - "user" → ["user", "users", "User", "UserService"]
             - "listener" → ["listener", "listen", "Listener", "ListenerMixin"]
             - "ui" → ["ui", "interface", "Interface", "CLI"]

        3. Search Code Index:
           - For each module in index:
             - Calculate relevance score:
               - +10 points: module name contains keyword
               - +5 points: function name contains keyword
               - +3 points: class name contains keyword
               - +1 point: file path contains keyword
             - Track matched keywords
           - Sort modules by relevance score (descending)

        4. Classify results:
           - Primary files: Relevance score >= 15 (high confidence)
           - Related files: 5 <= Relevance score < 15 (medium confidence)
           - Ignore: Relevance score < 5 (low confidence)

        5. Extract code snippets:
           - For primary files: Read file, extract class/function signatures
           - For related files: Just list file paths
           - Include line numbers for signatures

        6. Return structured data:
           {
               "primary_files": [
                   {
                       "path": "coffee_maker/cli/user_listener.py",
                       "relevance": 25,
                       "keywords_matched": ["user", "listener"],
                       "snippets": [
                           {
                               "type": "class",
                               "name": "UserListener",
                               "line_start": 45,
                               "line_end": 120,
                               "signature": "class UserListener: ..."
                           }
                       ],
                       "complexity": 12.3,
                       "loc": 380
                   }
               ],
               "related_files": [
                   {
                       "path": "coffee_maker/cli/notifications.py",
                       "relevance": 8,
                       "keywords_matched": ["notification"]
                   }
               ]
           }

    Returns:
        Dictionary with primary_files and related_files

    Time Complexity: O(N) where N is number of modules in Code Index (fast!)
    """
    # Implementation would go here
    pass
```

**Implementation Notes**:
- Code Index is pre-built (from SPEC-001), so no expensive grepping needed
- Relevance scoring is simple but effective (tuned based on testing)
- If Code Index doesn't exist, fallback to Grep tool (slower but works)
- Cache Code Index in memory for multiple spec creations (performance optimization)

**Edge Cases**:
- Code Index missing → Fallback to Grep/Glob search (slower, log warning)
- No matches found → Return empty lists, warn architect
- Too many matches (>20 files) → Increase relevance threshold, only show top 10

---

#### Component 3: Dependency Analyzer

**Responsibility**: Analyze imports and trace dependencies

**Inputs**:
- Primary files (from Code Discovery)
- Related files (from Code Discovery)
- Maximum dependency depth (default: 3 levels)

**Process**:

```python
def analyze_dependencies(primary_files: list[dict], related_files: list[dict], max_depth: int = 3) -> dict:
    """Analyze dependencies in affected files.

    Steps:
        1. For each primary file:
           - Read file content
           - Parse import statements:
             - "import coffee_maker.models.user" → internal dependency
             - "from redis import Redis" → external dependency
             - "from .base import BaseService" → relative import
           - Extract imported modules/classes/functions

        2. Trace transitive dependencies (up to max_depth levels):
           - Level 1: Direct imports in primary files
           - Level 2: Imports in Level 1 modules
           - Level 3: Imports in Level 2 modules
           - Stop at max_depth or when no new dependencies found

        3. Detect circular dependencies:
           - Build dependency graph: {module: [imported_modules]}
           - Use DFS to detect cycles
           - If cycle found: Warn architect with cycle path

        4. Categorize dependencies:
           - Internal (coffee_maker.*): List of internal modules
           - External (third-party packages): List of package names
           - Standard library (stdlib): List of stdlib modules

        5. Check external dependencies:
           - For each external package:
             - Check if in pyproject.toml (existing dependency)
             - If not in pyproject.toml: Flag as **NEW** (needs architect approval)

        6. Assess architectural impact:
           - Database changes: Check if models.py or migrations/ affected
           - API changes: Check if api/, endpoints/ affected
           - UI changes: Check if streamlit/, templates/ affected
           - Config changes: Check if .claude/, config/ affected

        7. Generate Mermaid dependency graph:
           ```mermaid
           graph LR
               A[user_listener.py] --> B[notifications.py]
               A --> C[roadmap_cli.py]
               B --> D[sounds/]
               C --> E[cached_roadmap_parser.py]
           ```

        8. Return structured dependency data:
           {
               "internal_dependencies": [
                   "coffee_maker.cli.notifications",
                   "coffee_maker.autonomous.cached_roadmap_parser"
               ],
               "external_dependencies": [
                   {"name": "click", "status": "existing"},
                   {"name": "rich", "status": "NEW"}  # Needs approval!
               ],
               "stdlib_dependencies": ["pathlib", "json", "logging"],
               "circular_dependencies": [],  # Empty if no cycles
               "architectural_impacts": {
                   "database": False,
                   "api": False,
                   "ui": True,  # Streamlit UI changes
                   "config": True  # .claude/ changes
               },
               "mermaid_graph": "graph LR\n    A[...] --> B[...]",
               "complexity_score": 6.5  # Based on # of dependencies
           }

    Returns:
        Dictionary with dependency analysis

    Time Complexity: O(N × D) where N is # of files, D is max depth
    """
    # Implementation would go here
    pass
```

**Implementation Notes**:
- Use AST (Abstract Syntax Tree) to parse imports (more reliable than regex)
- Track visited modules to avoid infinite loops in circular dependencies
- External dependency detection: Check pyproject.toml for package name
- Mermaid graph: Limit to 10 nodes max (avoid clutter), show only primary dependencies

**Edge Cases**:
- Circular dependency detected → Include in report, architect must resolve
- External package not in pyproject.toml → Flag as **NEW**, architect approves
- Relative imports (.base, ..utils) → Resolve to absolute paths

---

#### Component 4: Time Estimator

**Responsibility**: Estimate implementation time using data-driven approach

**Inputs**:
- Number of files affected (from Code Discovery)
- Lines of code (LOC) affected
- Complexity score (from Code Index)
- Dependency count (from Dependency Analyzer)
- Historical data (data/time_estimates.json)

**Process**:

```python
def estimate_implementation_time(
    files_affected: int,
    loc_affected: int,
    complexity_score: float,
    dependency_count: int,
    historical_data_path: str
) -> dict:
    """Estimate implementation time using historical data.

    Steps:
        1. Load historical data (data/time_estimates.json):
           {
               "priorities": [
                   {
                       "name": "PRIORITY 8",
                       "files_affected": 5,
                       "loc_affected": 1200,
                       "complexity": 7.5,
                       "dependencies": 8,
                       "estimated_hours": 16,
                       "actual_hours": 18.5,
                       "accuracy": 0.86  # 86% accurate (within 20%)
                   },
                   ...
               ],
               "accuracy_avg": 0.78  # Average 78% accuracy
           }

        2. Calculate base estimate using formula:
           base_hours = (files_affected × 2) + (loc_affected / 100) + (complexity_score × 0.5)

           Rationale:
           - Each file: ~2 hours (reading, understanding, modifying, testing)
           - Each 100 LOC: ~1 hour (typical code reading/writing speed)
           - Complexity: 0.5 hours per complexity point (higher complexity = more time)

        3. Apply complexity factors:
           - Database changes: +4 hours (migrations, schema changes, testing)
           - API changes: +3 hours (endpoint creation, validation, tests)
           - New dependencies: +2 hours per dependency (research, approval, integration)
           - Security-sensitive: +5 hours (extra testing, review, documentation)
           - UI changes: +3 hours (design, implementation, user testing)
           - High dependency count (>10): +2 hours (integration complexity)

        4. Find similar historical priorities:
           - Filter priorities with similar:
             - files_affected (±2 files)
             - complexity (±2 points)
             - dependency_count (±3 dependencies)
           - Calculate average actual_hours for similar priorities
           - Use as sanity check for estimate

        5. Adjust for architect's accuracy:
           - If historical accuracy < 80%: Increase estimate by 20%
           - If historical accuracy > 90%: Keep estimate as-is
           - Rationale: architect improves over time, but initially conservative

        6. Add overhead:
           - Testing: +20% (unit tests, integration tests)
           - Documentation: +10% (docstrings, README updates)
           - Code review: +10% (pre-commit, feedback, iterations)

        7. Calculate confidence interval:
           - If similar historical priorities found (n >= 3):
             - Confidence: HIGH (80-90%)
             - Range: ±15% (e.g., "12-14 hours")
           - If few similar priorities (n < 3):
             - Confidence: MEDIUM (60-70%)
             - Range: ±25% (e.g., "10-16 hours")
           - If no similar priorities:
             - Confidence: LOW (50%)
             - Range: ±40% (e.g., "8-18 hours")

        8. Return time estimate:
           {
               "base_estimate_hours": 12,
               "complexity_factors": {
                   "database_changes": 4,
                   "api_changes": 3,
                   "new_dependencies": 4,  # 2 deps × 2 hours
                   "security_sensitive": 0,
                   "ui_changes": 3
               },
               "adjusted_estimate_hours": 26,
               "overhead": {
                   "testing": 5.2,  # 20%
                   "documentation": 2.6,  # 10%
                   "code_review": 2.6  # 10%
               },
               "total_estimate_hours": 36,
               "confidence": "MEDIUM",
               "confidence_percentage": 70,
               "range": "27-45 hours",
               "similar_priorities_count": 2,
               "breakdown": {
                   "implementation": 26,
                   "testing": 5.2,
                   "documentation": 2.6,
                   "review": 2.6
               }
           }

    Returns:
        Dictionary with time estimate breakdown

    Note: This is data-driven, not just guesswork!
    """
    # Implementation would go here
    pass
```

**Implementation Notes**:
- Historical data file (data/time_estimates.json) initially empty, grows over time
- Formula tuned based on empirical data (will improve with more historical data)
- Architect can provide feedback (actual vs estimated), skill learns over time
- Conservative estimates preferred (better to underestimate than overestimate)

**Edge Cases**:
- No historical data → Use formula only, confidence = LOW
- Outlier priorities (very large or very small) → Use median instead of average
- Architect feedback missing → Use default accuracy (78%)

---

#### Component 5: Risk Identifier

**Responsibility**: Identify architectural risks using pattern-based heuristics

**Inputs**:
- Feature description (from priority)
- Affected files (from Code Discovery)
- Dependencies (from Dependency Analyzer)
- Complexity score (from Code Index)

**Process**:

```python
def identify_risks(
    feature_description: str,
    affected_files: list[dict],
    dependencies: dict,
    complexity_score: float
) -> list[dict]:
    """Identify architectural risks using heuristics.

    Steps:
        1. Performance risk detection:
           - Pattern: "query", "database", "loop", "N+1"
           - Heuristic: If description mentions database queries + loops → Risk
           - Severity: HIGH if >1000 LOC affected, MEDIUM otherwise
           - Mitigation: "Use query optimization, add indexes, consider caching"

        2. Security risk detection:
           - Pattern: "authentication", "password", "token", "sensitive", "PII"
           - Heuristic: If security-related keywords → Risk
           - Severity: CRITICAL (security always critical)
           - Mitigation: "Follow OWASP guidelines, add input validation, encrypt data"

        3. Scalability risk detection:
           - Pattern: "single-threaded", "blocking", "synchronous", "queue"
           - Heuristic: If description mentions threading/async + high complexity → Risk
           - Severity: MEDIUM if complexity > 10, LOW otherwise
           - Mitigation: "Consider async/await, use thread pools, add rate limiting"

        4. Integration risk detection:
           - Pattern: "API", "external", "third-party", "webhook"
           - Heuristic: If external dependencies + network calls → Risk
           - Severity: HIGH if external dependency is NEW, MEDIUM if existing
           - Mitigation: "Add retry logic, handle timeouts, implement circuit breaker"

        5. Complexity risk detection:
           - Heuristic: If complexity_score > 15 → Risk
           - Severity: MEDIUM if 15-20, HIGH if >20
           - Mitigation: "Break into smaller components, add comprehensive tests, increase code review time"

        6. Dependency risk detection:
           - Heuristic: If dependency_count > 15 → Risk
           - Severity: MEDIUM (many dependencies = integration complexity)
           - Mitigation: "Map dependency graph, add integration tests, isolate failure domains"

        7. Data migration risk detection:
           - Pattern: "database", "migration", "schema", "model"
           - Heuristic: If database changes detected → Risk
           - Severity: HIGH (data migrations are risky)
           - Mitigation: "Create rollback plan, test on staging, backup production data"

        8. Testing risk detection:
           - Heuristic: If LOC affected > 500 + no existing tests → Risk
           - Severity: MEDIUM
           - Mitigation: "Increase test coverage to >80%, add integration tests, consider TDD"

        9. Return risk list:
           [
               {
                   "type": "Performance",
                   "description": "Database queries in loops may cause N+1 query problem",
                   "severity": "HIGH",
                   "likelihood": "MEDIUM",
                   "impact": "HIGH",
                   "mitigation": "Use query optimization (select_related, prefetch_related), add database indexes, consider caching frequently accessed data",
                   "detected_by": "pattern_match",
                   "patterns_matched": ["query", "loop", "database"]
               },
               {
                   "type": "Security",
                   "description": "Authentication feature requires security best practices",
                   "severity": "CRITICAL",
                   "likelihood": "HIGH",
                   "impact": "CRITICAL",
                   "mitigation": "Follow OWASP authentication guidelines, use bcrypt for password hashing, implement rate limiting for login attempts, add audit logging",
                   "detected_by": "keyword_match",
                   "patterns_matched": ["authentication", "password"]
               }
           ]

    Returns:
        List of risk dictionaries

    Note: Heuristics are conservative (better to flag potential risk than miss real risk)
    """
    # Implementation would go here
    pass
```

**Implementation Notes**:
- Pattern matching is case-insensitive
- Multiple patterns can trigger same risk (combine into single risk)
- Architect can override severity/likelihood in final spec review
- Risk patterns configurable in future (allow adding custom patterns)

**Edge Cases**:
- No risks detected → Return empty list, add note "No major risks identified (pending architect review)"
- Too many risks (>10) → Prioritize by severity, show top 5
- Conflicting risk patterns → Highest severity wins

---

#### Component 6: Spec Formatter

**Responsibility**: Combine all sections into final formatted spec

**Inputs**:
- Partially populated template (from Stage 1)
- Code discovery results (from Stage 2)
- Dependency analysis (from Stage 3)
- Time estimate (from Stage 4)
- Risk list (from Stage 5)

**Process**:

```python
def format_final_spec(
    template: str,
    code_discovery: dict,
    dependencies: dict,
    time_estimate: dict,
    risks: list[dict]
) -> str:
    """Format all sections into final spec.

    Steps:
        1. Insert code discovery section:
           ## Affected Code Zones

           ### Primary Files (High Confidence)

           1. **coffee_maker/cli/user_listener.py** (380 LOC, Complexity: 12.3)
              - Relevance: 25 (keywords: user, listener)
              - Classes:
                - `UserListener` (line 45-120): Main user interface class
              - Functions:
                - `handle_command()` (line 150-180): Process CLI commands

           2. **coffee_maker/cli/notifications.py** (245 LOC, Complexity: 8.5)
              - Relevance: 18 (keywords: notification)
              - Classes:
                - `NotificationManager` (line 30-100): Manages notifications

        2. Insert dependency section:
           ## Dependencies

           ### Internal Dependencies (coffee_maker.*)
           - coffee_maker.cli.notifications (NotificationManager)
           - coffee_maker.autonomous.cached_roadmap_parser (parse_roadmap)

           ### External Dependencies (Third-Party)
           - click (existing) - CLI framework
           - rich (existing) - Terminal formatting
           - **playsound (NEW)** - Sound playback [NEEDS ARCHITECT APPROVAL]

           ### Architectural Impacts
           - ✅ Database: No changes required
           - ✅ API: No changes required
           - ⚠️ UI: Streamlit UI modifications needed
           - ⚠️ Config: .claude/ configuration changes

           ### Dependency Graph (Mermaid)
           ```mermaid
           graph LR
               A[user_listener.py] --> B[notifications.py]
               A --> C[roadmap_cli.py]
               B --> D[sounds/]
           ```

        3. Insert time estimate section:
           ## Time Estimate

           **Total Estimate**: 36 hours (27-45 hours range)
           **Confidence**: MEDIUM (70%)
           **Based on**: 2 similar historical priorities

           ### Breakdown
           - **Implementation**: 26 hours
             - Base (files × LOC × complexity): 12 hours
             - UI changes: +3 hours
             - API changes: +3 hours
             - New dependencies: +4 hours (2 deps)
             - Database changes: +4 hours
           - **Testing**: 5.2 hours (20% overhead)
           - **Documentation**: 2.6 hours (10% overhead)
           - **Code Review**: 2.6 hours (10% overhead)

           **Note**: Estimate based on historical data. Actual time may vary.

        4. Insert risks section:
           ## Risks & Mitigations

           ### Risk 1: Performance - Database Query Optimization

           **Description**: Database queries in loops may cause N+1 query problem

           **Severity**: HIGH
           **Likelihood**: MEDIUM
           **Impact**: HIGH

           **Mitigation**:
           - Use query optimization (select_related, prefetch_related)
           - Add database indexes for frequently queried fields
           - Consider caching frequently accessed data
           - Monitor query performance with Django Debug Toolbar

           ---

           ### Risk 2: Security - Authentication Best Practices

           **Description**: Authentication feature requires security best practices

           **Severity**: CRITICAL
           **Likelihood**: HIGH
           **Impact**: CRITICAL

           **Mitigation**:
           - Follow OWASP authentication guidelines
           - Use bcrypt for password hashing (NOT plain text!)
           - Implement rate limiting for login attempts
           - Add audit logging for authentication events
           - Conduct security review before deployment

        5. Add metadata:
           - Update "Estimated Effort": From time estimate
           - Add "Auto-Generated Sections": List which sections were auto-filled
           - Add "Architect Review Required": List sections needing review

        6. Add architect notes:
           ---
           ## Notes for Architect

           **Auto-Generated Sections** (Review recommended):
           - Affected Code Zones (from Code Discovery Engine)
           - Dependencies (from Dependency Analyzer)
           - Time Estimate (from Time Estimator)
           - Risks & Mitigations (from Risk Identifier)

           **Architect Must Complete**:
           - [ ] Problem Statement → Current Situation (add context)
           - [ ] Proposed Solution → High-Level Approach (add architectural insights)
           - [ ] Detailed Design → Component Design (add implementation details)
           - [ ] Testing Strategy (add specific test cases)
           - [ ] Rollout Plan (add phased deployment plan)

           **Estimated Review Time**: 25 minutes (20% of original time)

           ---

        7. Format markdown:
           - Ensure consistent header levels
           - Format code blocks with syntax highlighting
           - Format tables with proper alignment
           - Add line breaks between sections
           - Validate markdown syntax

        8. Validate completeness:
           - Check all required sections present
           - Warn if critical sections missing
           - Add "[TO BE COMPLETED]" placeholders if needed

        9. Return final spec string

    Returns:
        Complete formatted spec (markdown string)

    Note: Spec is 90% complete, architect reviews and adds 10% (architectural insights)
    """
    # Implementation would go here
    pass
```

**Implementation Notes**:
- Use f-strings for formatting (clean, readable)
- Preserve existing template structure (don't reorganize sections)
- Add clear markers for auto-generated vs manual sections
- Include metadata about skill execution (timestamp, version, confidence)

**Edge Cases**:
- Section has no content → Add placeholder "[architect TO COMPLETE: ...]"
- Markdown syntax error → Log warning, fix automatically if possible
- Template version mismatch → Warn architect, use best-effort mapping

---

### Data Structures

#### SpecCreationInput

```python
@dataclass
class SpecCreationInput:
    """Input to spec-creation-automation skill."""
    priority_name: str  # e.g., "PRIORITY 10"
    priority_content: str  # Full ROADMAP priority text
    code_index_path: str = "data/code_index.json"  # From SPEC-001
    template_path: str = "docs/architecture/specs/SPEC-000-template.md"
    historical_data_path: str = "data/time_estimates.json"
    max_dependency_depth: int = 3
```

#### SpecCreationOutput

```python
@dataclass
class SpecCreationOutput:
    """Output from spec-creation-automation skill."""
    spec_content: str  # Complete spec (markdown)
    spec_filename: str  # e.g., "SPEC-061-user-listener-ui.md"
    completion_percentage: float  # e.g., 0.90 (90% complete)
    architect_review_required: list[str]  # Sections needing review
    execution_time_seconds: float
    confidence: str  # "HIGH" | "MEDIUM" | "LOW"
```

#### CodeDiscoveryResult

```python
@dataclass
class CodeDiscoveryResult:
    """Result from Code Discovery Engine."""
    primary_files: list[PrimaryFile]
    related_files: list[RelatedFile]
    total_files_found: int
    total_loc_affected: int
    avg_complexity: float
```

```python
@dataclass
class PrimaryFile:
    """Primary file affected by priority."""
    path: str
    relevance_score: float
    keywords_matched: list[str]
    snippets: list[CodeSnippet]
    complexity: float
    loc: int
```

```python
@dataclass
class CodeSnippet:
    """Code snippet from primary file."""
    type: str  # "class" | "function" | "method"
    name: str
    line_start: int
    line_end: int
    signature: str  # e.g., "def handle_command(self, cmd: str) -> bool:"
```

#### DependencyAnalysisResult

```python
@dataclass
class DependencyAnalysisResult:
    """Result from Dependency Analyzer."""
    internal_dependencies: list[str]  # coffee_maker.* modules
    external_dependencies: list[ExternalDependency]
    stdlib_dependencies: list[str]
    circular_dependencies: list[list[str]]  # Cycles as lists of modules
    architectural_impacts: ArchitecturalImpact
    mermaid_graph: str
    complexity_score: float
```

```python
@dataclass
class ExternalDependency:
    """External package dependency."""
    name: str
    status: str  # "existing" | "NEW"
    requires_approval: bool  # True if NEW
```

```python
@dataclass
class ArchitecturalImpact:
    """Architectural areas affected."""
    database: bool
    api: bool
    ui: bool
    config: bool
```

#### TimeEstimate

```python
@dataclass
class TimeEstimate:
    """Implementation time estimate."""
    base_estimate_hours: float
    complexity_factors: dict[str, float]
    adjusted_estimate_hours: float
    overhead: dict[str, float]  # testing, docs, review
    total_estimate_hours: float
    confidence: str  # "HIGH" | "MEDIUM" | "LOW"
    confidence_percentage: float
    range: str  # e.g., "27-45 hours"
    similar_priorities_count: int
    breakdown: dict[str, float]
```

#### Risk

```python
@dataclass
class Risk:
    """Identified risk."""
    type: str  # "Performance" | "Security" | "Scalability" | "Integration"
    description: str
    severity: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    likelihood: str  # "HIGH" | "MEDIUM" | "LOW"
    impact: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    mitigation: str  # Mitigation strategy
    detected_by: str  # "pattern_match" | "keyword_match" | "heuristic"
    patterns_matched: list[str]
```

---

### Key Algorithms

#### Algorithm 1: Relevance Scoring (Code Discovery)

```
Input: module (from Code Index), keywords (from priority)
Output: relevance_score (float)

Steps:
1. score = 0
2. For each keyword in keywords:
   a. If keyword in module.name (case-insensitive):
      score += 10
   b. For each function in module.functions:
      If keyword in function.name:
         score += 5
   c. For each class in module.classes:
      If keyword in class.name:
         score += 3
   d. If keyword in module.path:
      score += 1
3. Return score

Time Complexity: O(K × (F + C)) where K = # keywords, F = # functions, C = # classes
Space Complexity: O(1)

Example:
module = {
    "name": "coffee_maker.cli.user_listener",
    "path": "coffee_maker/cli/user_listener.py",
    "functions": ["handle_command", "start_listener"],
    "classes": ["UserListener"]
}
keywords = ["user", "listener", "command"]

Calculation:
- "user" in "user_listener" → +10
- "listener" in "user_listener" → +10
- "command" in "handle_command" → +5
- "listener" in "UserListener" → +3
- "user" in "user_listener.py" → +1
- "listener" in "user_listener.py" → +1
Total: 30 (HIGH relevance)
```

#### Algorithm 2: Dependency Tracing (DFS with Cycle Detection)

```
Input: primary_files, max_depth
Output: dependency_graph, circular_dependencies

Steps:
1. Initialize:
   - dependency_graph = {}  # {module: [imported_modules]}
   - visited = set()
   - visiting = set()  # For cycle detection
   - circular_deps = []

2. For each file in primary_files:
   a. Parse imports using AST
   b. Extract imported modules
   c. Add to dependency_graph[file] = imported_modules

3. Trace transitive dependencies (DFS):
   Function dfs(module, depth):
       If depth > max_depth:
           return

       If module in visiting:
           # Cycle detected!
           circular_deps.append(path_to_module)
           return

       If module in visited:
           return

       visiting.add(module)

       For each imported in dependency_graph[module]:
           dfs(imported, depth + 1)

       visiting.remove(module)
       visited.add(module)

4. For each file in primary_files:
   dfs(file, depth=1)

5. Return dependency_graph, circular_deps

Time Complexity: O(V + E) where V = # modules, E = # imports (DFS)
Space Complexity: O(V) for visited/visiting sets

Example:
primary_files = ["user_listener.py"]

Execution:
- Level 1: user_listener.py imports [notifications.py, roadmap_cli.py]
- Level 2: notifications.py imports [sounds/]
- Level 2: roadmap_cli.py imports [cached_roadmap_parser.py]
- Level 3: cached_roadmap_parser.py imports [pathlib, json]
- Stop at Level 3 (max_depth)

Result:
dependency_graph = {
    "user_listener.py": ["notifications.py", "roadmap_cli.py"],
    "notifications.py": ["sounds/"],
    "roadmap_cli.py": ["cached_roadmap_parser.py"],
    "cached_roadmap_parser.py": ["pathlib", "json"]
}
circular_deps = []  # No cycles
```

#### Algorithm 3: Time Estimation Formula

```
Input: files_affected, loc_affected, complexity_score, dependency_count, complexity_factors
Output: total_estimate_hours

Formula:
base_hours = (files_affected × 2) + (loc_affected / 100) + (complexity_score × 0.5)

adjusted_hours = base_hours + sum(complexity_factors.values())

overhead = adjusted_hours × (0.20 + 0.10 + 0.10)  # testing + docs + review = 40%

total_hours = adjusted_hours + overhead

Example:
files_affected = 5
loc_affected = 1200
complexity_score = 7.5
complexity_factors = {
    "database_changes": 4,
    "ui_changes": 3,
    "new_dependencies": 4
}

Calculation:
base_hours = (5 × 2) + (1200 / 100) + (7.5 × 0.5)
           = 10 + 12 + 3.75
           = 25.75

adjusted_hours = 25.75 + (4 + 3 + 4)
               = 25.75 + 11
               = 36.75

overhead = 36.75 × 0.40
         = 14.7

total_hours = 36.75 + 14.7
            = 51.45 hours

Result: ~51 hours (estimate range: 38-64 hours with ±25% confidence)
```

---

### API Definitions

#### Skill Invocation API

```python
# In architect agent
from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

# Prepare input variables
variables = {
    "PRIORITY_NAME": "PRIORITY 10",
    "PRIORITY_CONTENT": roadmap_priority_text,
    "CODE_INDEX_PATH": "data/code_index.json",
    "TEMPLATE_PATH": "docs/architecture/specs/SPEC-000-template.md",
    "HISTORICAL_DATA_PATH": "data/time_estimates.json",
    "MAX_DEPENDENCY_DEPTH": "3"
}

# Load and execute skill
spec_content = load_skill(SkillNames.SPEC_CREATION_AUTOMATION, variables)

# spec_content is markdown string with complete spec (90% filled)
# architect reviews, adds insights, saves to file
```

#### Skill Output Format

The skill outputs a **markdown string** containing the complete spec. Example structure:

```markdown
# SPEC-061: User Listener UI

**Status**: Draft
**Author**: architect agent
**Date Created**: 2025-10-18
**Estimated Effort**: 36 hours
**Auto-Generated**: 90% (architect review: 25 min)

---

## Executive Summary

[Auto-generated from priority description]

---

## Problem Statement

### Current Situation
[architect TO COMPLETE: Add context about current state]

### Goal
[Auto-generated from acceptance criteria]

---

## Affected Code Zones

### Primary Files (High Confidence)

1. **coffee_maker/cli/user_listener.py** (380 LOC, Complexity: 12.3)
   [Auto-generated from Code Discovery]

---

## Dependencies

### Internal Dependencies
[Auto-generated from Dependency Analyzer]

### External Dependencies
[Auto-generated, flags NEW dependencies]

---

## Time Estimate

**Total Estimate**: 36 hours (27-45 hours range)
[Auto-generated from Time Estimator]

---

## Risks & Mitigations

### Risk 1: Performance
[Auto-generated from Risk Identifier]

---

## Notes for Architect

**Estimated Review Time**: 25 minutes

**Architect Must Complete**:
- [ ] Problem Statement → Current Situation
- [ ] Proposed Solution → High-Level Approach
- [ ] Detailed Design → Component Design

---
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_spec_creation_automation.py`

**Test Cases**:

```python
def test_template_auto_population():
    """Test template auto-population from ROADMAP priority."""
    priority_content = """
    ## PRIORITY 10: User Listener UI

    Create unified user interface.

    **Acceptance Criteria**:
    - AC-1: CLI works
    - AC-2: Chat works
    """
    template = load_template()

    result = auto_populate_template("PRIORITY 10", priority_content, template)

    assert "User Listener UI" in result
    assert "AC-1: CLI works" in result
    assert "SPEC-061" in result  # Spec number generated


def test_code_discovery_relevance_scoring():
    """Test relevance scoring for code discovery."""
    module = {
        "name": "coffee_maker.cli.user_listener",
        "functions": ["handle_command"],
        "classes": ["UserListener"]
    }
    keywords = ["user", "listener", "command"]

    score = calculate_relevance_score(module, keywords)

    assert score >= 25  # High relevance expected


def test_dependency_analysis_detects_circular():
    """Test circular dependency detection."""
    files = {
        "a.py": ["b.py"],
        "b.py": ["c.py"],
        "c.py": ["a.py"]  # Cycle: a → b → c → a
    }

    result = analyze_dependencies(files)

    assert len(result["circular_dependencies"]) > 0
    assert ["a.py", "b.py", "c.py"] in result["circular_dependencies"]


def test_time_estimation_formula():
    """Test time estimation formula."""
    estimate = estimate_implementation_time(
        files_affected=5,
        loc_affected=1200,
        complexity_score=7.5,
        dependency_count=8,
        historical_data_path="tests/fixtures/time_estimates.json"
    )

    assert estimate["total_estimate_hours"] >= 30  # Reasonable estimate
    assert estimate["confidence"] in ["HIGH", "MEDIUM", "LOW"]
    assert "range" in estimate


def test_risk_identification_security():
    """Test security risk detection."""
    feature_description = "Implement user authentication with password hashing"

    risks = identify_risks(
        feature_description,
        affected_files=[],
        dependencies={},
        complexity_score=5.0
    )

    # Should detect security risk
    security_risks = [r for r in risks if r["type"] == "Security"]
    assert len(security_risks) > 0
    assert security_risks[0]["severity"] == "CRITICAL"


def test_spec_formatter_combines_sections():
    """Test spec formatter combines all sections."""
    template = load_template()
    code_discovery = {"primary_files": [...]}
    dependencies = {"internal_dependencies": [...]}
    time_estimate = {"total_estimate_hours": 36}
    risks = [{"type": "Performance", ...}]

    final_spec = format_final_spec(
        template, code_discovery, dependencies, time_estimate, risks
    )

    assert "## Affected Code Zones" in final_spec
    assert "## Dependencies" in final_spec
    assert "## Time Estimate" in final_spec
    assert "## Risks & Mitigations" in final_spec
    assert "36 hours" in final_spec
```

**Coverage Target**: >80% for all components

---

### Integration Tests

**File**: `tests/ci_tests/test_spec_creation_workflow.py`

**Test Cases**:

```python
def test_full_spec_creation_workflow():
    """Test complete spec creation from ROADMAP priority to final spec."""
    # Setup: Create test ROADMAP priority
    priority = {
        "name": "PRIORITY 99",
        "content": """
        ## PRIORITY 99: Test Feature

        Implement test feature for integration testing.

        **Acceptance Criteria**:
        - AC-1: Feature works
        """
    }

    # Create Code Index fixture
    code_index = create_test_code_index()

    # Execute skill
    result = execute_spec_creation_skill(
        priority_name="PRIORITY 99",
        priority_content=priority["content"],
        code_index_path="tests/fixtures/code_index.json"
    )

    # Assertions
    assert result is not None
    assert "SPEC-099" in result  # Correct spec number
    assert "Test Feature" in result
    assert "AC-1: Feature works" in result
    assert "## Affected Code Zones" in result
    assert "## Time Estimate" in result

    # Validate markdown syntax
    assert validate_markdown(result) is True

    # Check completion percentage
    assert calculate_completion_percentage(result) >= 0.85  # 85%+ complete


def test_spec_creation_with_missing_code_index():
    """Test fallback when Code Index missing."""
    # Remove Code Index
    code_index_path = Path("data/code_index.json")
    code_index_path.unlink(missing_ok=True)

    # Execute skill (should fallback to Grep)
    result = execute_spec_creation_skill(
        priority_name="PRIORITY 99",
        priority_content="Test priority"
    )

    # Should still work but with warning
    assert result is not None
    assert "Code Index not found" in get_logs()  # Warning logged


def test_architect_feedback_loop():
    """Test learning from architect feedback on time estimates."""
    # Create initial estimate
    estimate1 = estimate_implementation_time(
        files_affected=5, loc_affected=1000, ...
    )
    initial_estimate = estimate1["total_estimate_hours"]

    # Simulate architect feedback (actual time was different)
    record_actual_time(
        priority_name="PRIORITY 98",
        estimated_hours=initial_estimate,
        actual_hours=initial_estimate * 1.2  # 20% over
    )

    # Create new estimate (should adjust based on feedback)
    estimate2 = estimate_implementation_time(
        files_affected=5, loc_affected=1000, ...
    )
    new_estimate = estimate2["total_estimate_hours"]

    # New estimate should be slightly higher (learning!)
    assert new_estimate > initial_estimate
```

---

### Performance Tests

**File**: `tests/performance/test_spec_creation_performance.py`

**Test Cases**:

```python
def test_spec_creation_completes_within_60_seconds():
    """Test skill completes within performance target."""
    import time

    start = time.time()

    result = execute_spec_creation_skill(
        priority_name="PRIORITY 99",
        priority_content=large_priority_content  # Large priority
    )

    end = time.time()
    duration = end - start

    assert duration < 60  # < 60 seconds
    assert result is not None


def test_code_discovery_performance():
    """Test Code Discovery completes within 30 seconds."""
    import time

    code_index = load_large_code_index()  # 1000+ modules

    start = time.time()

    result = discover_relevant_code(
        feature_name="Test Feature",
        keywords=["test", "feature", "implementation"],
        code_index=code_index
    )

    end = time.time()
    duration = end - start

    assert duration < 30  # < 30 seconds
    assert len(result["primary_files"]) > 0
```

---

### Manual Testing

**Manual Test Plan**:

1. **Test with Real ROADMAP Priority**:
   ```bash
   # In architect agent
   poetry run architect --skill spec-creation-automation --priority "PRIORITY 10"

   # Verify:
   # - Spec file created: docs/architecture/specs/SPEC-061-user-listener-ui.md
   # - Spec is 90%+ complete
   # - Code zones are accurate
   # - Time estimate is reasonable
   # - Risks are relevant
   ```

2. **Test with Missing Code Index**:
   ```bash
   # Remove Code Index
   rm data/code_index.json

   # Run skill (should fallback to Grep)
   poetry run architect --skill spec-creation-automation --priority "PRIORITY 10"

   # Verify:
   # - Spec still created (slower but works)
   # - Warning logged about missing Code Index
   ```

3. **Test with Complex Priority**:
   ```bash
   # Use a complex priority (e.g., database migration + API changes)
   poetry run architect --skill spec-creation-automation --priority "PRIORITY 15"

   # Verify:
   # - Multiple risk types detected
   # - Time estimate includes complexity factors
   # - Dependency graph shows external packages
   ```

4. **Test Architect Review Time**:
   ```bash
   # Time how long architect takes to review and complete spec
   # Target: <25 minutes

   # Measure:
   # - Read generated spec: ~5 min
   # - Fill in missing sections: ~10 min
   # - Add architectural insights: ~10 min
   # Total: ~25 min (vs 117 min manual)
   ```

---

## Rollout Plan

### Phase 1: Core Implementation (Week 1 - 6 hours)

**Goal**: Implement core components (template auto-population, code discovery, spec formatter)

**Timeline**: Day 1-3 (6 hours)

**Tasks**:
1. Create skill file: `.claude/skills/spec-creation-automation.md`
2. Implement Stage 1: Template Auto-Population (2 hours)
   - Parse ROADMAP priority content
   - Extract feature name, description, acceptance criteria
   - Generate spec filename and metadata
   - Pre-fill template sections
3. Implement Stage 2: Code Discovery Engine (2 hours)
   - Load Code Index from SPEC-001
   - Generate search keywords
   - Calculate relevance scores
   - Extract code snippets
4. Implement Stage 6: Spec Formatter (2 hours)
   - Combine all sections
   - Format markdown
   - Add metadata and notes for architect
   - Validate completeness

**Success Criteria**:
- ✅ Skill creates 50%+ complete specs (template + code zones)
- ✅ Code discovery finds relevant files with >80% precision
- ✅ Spec is valid markdown and follows template structure

**Deliverables**:
- `.claude/skills/spec-creation-automation.md` (skill file)
- Unit tests for Stages 1, 2, 6
- Integration test: End-to-end workflow

---

### Phase 2: Advanced Features (Week 1 - 4 hours)

**Goal**: Implement dependency analysis and time estimation

**Timeline**: Day 4-5 (4 hours)

**Tasks**:
1. Implement Stage 3: Dependency Analyzer (2 hours)
   - Parse import statements with AST
   - Trace transitive dependencies (DFS)
   - Detect circular dependencies
   - Identify external packages (NEW flag)
   - Generate Mermaid dependency graph
2. Implement Stage 4: Time Estimator (2 hours)
   - Create `data/time_estimates.json` (historical data file)
   - Implement base estimation formula
   - Apply complexity factors
   - Calculate confidence interval
   - Break down estimate (implementation, testing, docs, review)

**Success Criteria**:
- ✅ Dependency analysis finds all imports (95%+ recall)
- ✅ Circular dependencies detected and reported
- ✅ Time estimates within ±30% of manual estimates (initial accuracy, improves over time)
- ✅ Confidence intervals provided (HIGH/MEDIUM/LOW)

**Deliverables**:
- Dependency Analyzer implementation
- Time Estimator implementation
- Unit tests for Stages 3, 4
- `data/time_estimates.json` (initially empty, grows over time)

---

### Phase 3: Risk Identification (Week 1 - 2 hours)

**Goal**: Implement risk identification with pattern-based heuristics

**Timeline**: Day 6 (2 hours)

**Tasks**:
1. Implement Stage 5: Risk Identifier (2 hours)
   - Define risk patterns (performance, security, scalability, integration)
   - Implement pattern matching (case-insensitive, keyword-based)
   - Assign severity/likelihood/impact
   - Generate mitigation recommendations

**Success Criteria**:
- ✅ Security risks always detected (100% recall for security keywords)
- ✅ Performance risks detected when "query" + "loop" mentioned (>80% recall)
- ✅ Risk descriptions are actionable (include mitigation strategies)

**Deliverables**:
- Risk Identifier implementation
- Unit tests for risk detection
- Risk pattern configuration (extensible for future patterns)

---

### Phase 4: Integration & Testing (Week 2 - 2 hours)

**Goal**: Integrate all stages, test end-to-end, validate with real priorities

**Timeline**: Day 7-8 (2 hours)

**Tasks**:
1. Integrate all 6 stages into single skill workflow
2. Add to `SkillNames` enum in `skill_loader.py`
3. Write integration tests (end-to-end spec creation)
4. Test with 3-5 real ROADMAP priorities
5. Measure actual time savings (baseline: 117 min → target: <30 min)
6. Collect architect feedback (accuracy, completeness, usability)

**Success Criteria**:
- ✅ Skill executes all 6 stages successfully
- ✅ Spec creation time <30 minutes (including architect review)
- ✅ Spec quality same or better than manual specs
- ✅ architect satisfaction: "This saves me hours!"

**Deliverables**:
- Complete skill integration
- Integration tests (>80% coverage)
- Performance benchmarks
- Architect feedback survey results

---

### Phase 5: Production Deployment (Week 2 - 1 hour)

**Goal**: Deploy to production, document usage, monitor metrics

**Timeline**: Day 9 (1 hour)

**Tasks**:
1. Update architect agent documentation (how to use skill)
2. Create user guide: `docs/skills/spec-creation-automation.md`
3. Add skill to architect agent's core workflow
4. Set up metrics tracking:
   - Time savings per spec
   - Accuracy of time estimates
   - Number of specs created with skill
5. Monitor first 5 spec creations, collect feedback

**Success Criteria**:
- ✅ Skill documented and ready for production use
- ✅ architect agent uses skill by default for spec creation
- ✅ Metrics tracked in Langfuse (time savings, accuracy)
- ✅ No critical bugs reported in first week

**Deliverables**:
- Production deployment
- User documentation
- Metrics dashboard
- Monitoring alerts

---

**Total Rollout Time**: 2 weeks (15 hours total)

**Phased Approach Benefits**:
- Early value delivery (Phase 1: 50% complete specs in Week 1)
- Incremental improvements (each phase adds value)
- Feedback-driven (architect tests each phase, provides feedback)
- Risk mitigation (if a phase fails, previous phases still work)

---

## Risks & Mitigations

### Risk 1: Inaccurate Code Discovery

**Description**: Code Discovery Engine finds wrong files or misses relevant files

**Likelihood**: MEDIUM

**Impact**: HIGH (architect must manually search for missed files, wastes time)

**Mitigation**:
- Implement relevance scoring with tunable thresholds
- Show confidence scores for each file (HIGH/MEDIUM/LOW)
- Allow architect to override/supplement results
- Fallback to Grep if Code Index missing (slower but reliable)
- Track precision/recall metrics, improve algorithm over time

**Fallback**: If Code Discovery fails, architect uses manual Grep/Glob (no worse than current state)

---

### Risk 2: Time Estimates Too Far Off

**Description**: Time estimates consistently ±50% off actual time (no better than manual)

**Likelihood**: MEDIUM (initially, improves over time)

**Impact**: MEDIUM (planning becomes unreliable, architect loses trust)

**Mitigation**:
- Start conservative (better to overestimate than underestimate)
- Track actual vs estimated time for all priorities
- Implement feedback loop (architect reports actual time)
- Adjust formula based on historical data (learning algorithm)
- Provide estimate ranges (e.g., "30-45 hours") instead of point estimates
- Show confidence level (HIGH/MEDIUM/LOW) so architect knows when to adjust

**Fallback**: If estimates are unreliable, architect uses manual estimation (no worse than current state)

---

### Risk 3: Template Too Rigid

**Description**: Auto-generated spec doesn't fit all priority types (simple vs complex)

**Likelihood**: MEDIUM

**Impact**: MEDIUM (architect must manually reorganize spec, wastes time)

**Mitigation**:
- Support multiple template types:
  - Simple: Small features (<5 files, <500 LOC)
  - Medium: Standard features (5-10 files, 500-2000 LOC)
  - Complex: Large features (>10 files, >2000 LOC)
- Auto-detect priority complexity (based on keywords, LOC, dependencies)
- Allow architect to specify template type (override auto-detection)
- Make template sections optional (skip if not applicable)

**Fallback**: If template doesn't fit, architect manually adjusts (no worse than current state)

---

### Risk 4: Dependency Analysis Misses Imports

**Description**: Dependency Analyzer misses imports (e.g., dynamic imports, relative imports)

**Likelihood**: LOW (AST parsing is reliable for most cases)

**Impact**: MEDIUM (architect misses dependencies, causes integration issues later)

**Mitigation**:
- Use AST (Abstract Syntax Tree) for robust parsing
- Handle relative imports (., .., etc.)
- Handle dynamic imports (`__import__()`, `importlib`)
- Warn architect if unusual import patterns detected
- Show "Unresolved imports" section for manual review

**Fallback**: If dependency analysis fails, architect manually checks imports (no worse than current state)

---

### Risk 5: Risk Identification False Positives

**Description**: Risk Identifier flags too many false risks (cry wolf problem)

**Likelihood**: MEDIUM (heuristics are conservative)

**Impact**: LOW (architect ignores irrelevant risks, wastes review time)

**Mitigation**:
- Tune risk patterns based on feedback (reduce false positives)
- Show confidence scores for each risk (HIGH/MEDIUM/LOW)
- Allow architect to mark risks as "False Positive" (feedback loop)
- Prioritize risks by severity (show CRITICAL/HIGH first)
- Limit to top 5 risks (avoid overwhelming architect)

**Fallback**: If too many false positives, architect ignores risk section (no worse than current state)

---

### Risk 6: Historical Data Insufficient

**Description**: Not enough historical data to make accurate time estimates

**Likelihood**: HIGH (initially, data grows over time)

**Impact**: LOW (estimates fall back to formula-based, still better than manual guesswork)

**Mitigation**:
- Start with formula-based estimation (no historical data needed)
- Collect data passively (architect reports actual time, data grows automatically)
- Provide confidence level (LOW if no historical data, HIGH once data sufficient)
- Use similar priorities (similar complexity, similar files) for estimates
- After 10+ priorities, historical data becomes useful

**Fallback**: If no historical data, use formula-based estimation (conservative but reliable)

---

## Observability

### Metrics

**Tracked Metrics**:

1. **Time Savings**:
   - `spec_creation.time_manual_baseline`: 117 minutes (baseline)
   - `spec_creation.time_with_skill`: Actual time with skill (target: <30 min)
   - `spec_creation.time_saved`: Manual - Skill (target: >87 min)
   - `spec_creation.savings_percentage`: (Time Saved / Manual) × 100 (target: >75%)

2. **Accuracy**:
   - `spec_creation.code_discovery_precision`: TP / (TP + FP) (target: >90%)
   - `spec_creation.code_discovery_recall`: TP / (TP + FN) (target: >80%)
   - `spec_creation.time_estimate_accuracy`: |Estimated - Actual| / Actual (target: <20%)
   - `spec_creation.risk_identification_recall`: Risks Found / Total Risks (target: >80%)

3. **Usage**:
   - `spec_creation.skill_invocations_total`: Total times skill used
   - `spec_creation.skill_invocations_per_week`: Weekly usage rate
   - `spec_creation.completion_percentage_avg`: Average spec completion (target: >85%)

4. **Performance**:
   - `spec_creation.execution_time_seconds`: Total skill execution time (target: <60s)
   - `spec_creation.code_discovery_time_seconds`: Code Discovery stage time (target: <30s)
   - `spec_creation.dependency_analysis_time_seconds`: Dependency Analyzer stage time (target: <20s)

**Metric Storage**: Langfuse (observability platform)

---

### Logs

**Log Events**:

```python
# INFO logs
logger.info("📚 Spec creation skill started", extra={
    "priority_name": "PRIORITY 10",
    "timestamp": "2025-10-18T14:30:00Z"
})

logger.info("✅ Stage 1 complete: Template auto-populated", extra={
    "completion_percentage": 0.20,
    "sections_filled": ["Executive Summary", "Requirements"]
})

logger.info("✅ Stage 2 complete: Code discovery", extra={
    "primary_files_found": 3,
    "related_files_found": 5,
    "avg_relevance_score": 18.5
})

logger.info("✅ Spec creation complete", extra={
    "spec_filename": "SPEC-061-user-listener-ui.md",
    "completion_percentage": 0.92,
    "execution_time_seconds": 45.3,
    "architect_review_time_estimated_minutes": 25
})

# WARNING logs
logger.warning("⚠️ Code Index not found, falling back to Grep", extra={
    "code_index_path": "data/code_index.json"
})

logger.warning("⚠️ Circular dependency detected", extra={
    "cycle": ["a.py", "b.py", "c.py", "a.py"]
})

logger.warning("⚠️ New external dependency requires approval", extra={
    "package_name": "redis",
    "purpose": "Caching layer"
})

# ERROR logs
logger.error("❌ Skill execution failed", extra={
    "error": "FileNotFoundError: ROADMAP.md not found",
    "stage": "Stage 1: Template Auto-Population"
})
```

---

### Alerts

**Alert Conditions**:

1. **Skill Execution Failure**:
   - Condition: Skill fails to execute (exception thrown)
   - Severity: HIGH
   - Action: Notify architect, fallback to manual spec creation

2. **Low Accuracy**:
   - Condition: Time estimate accuracy <50% for 3+ consecutive specs
   - Severity: MEDIUM
   - Action: Review formula, adjust complexity factors

3. **Performance Degradation**:
   - Condition: Execution time >120 seconds (2x target)
   - Severity: MEDIUM
   - Action: Investigate bottleneck (Code Index load time, AST parsing)

4. **Missing Code Index**:
   - Condition: Code Index not found (fallback to Grep)
   - Severity: LOW
   - Action: Regenerate Code Index (run architecture-reuse-check skill)

---

## Documentation

### User Documentation

**File**: `docs/skills/spec-creation-automation.md`

**Contents**:
```markdown
# Spec Creation Automation Skill

## Overview

Automates 78% of technical specification creation, reducing architect time from 117 min → 25 min.

## How to Use

### As Architect Agent

poetry run architect --skill spec-creation-automation --priority "PRIORITY 10"

## What Gets Auto-Generated

- ✅ Template sections (Executive Summary, Requirements)
- ✅ Affected Code Zones (primary files, related files, code snippets)
- ✅ Dependencies (internal, external, architectural impacts, Mermaid graph)
- ✅ Time Estimate (breakdown, confidence interval, range)
- ✅ Risks & Mitigations (performance, security, scalability)

## What Architect Must Review

- [ ] Problem Statement → Current Situation (add context)
- [ ] Proposed Solution → High-Level Approach (add architectural insights)
- [ ] Detailed Design → Component Design (add implementation details)
- [ ] Testing Strategy (add specific test cases)
- [ ] Rollout Plan (add phased deployment plan)

**Estimated Review Time**: 25 minutes (20% of original 117 min)

## Examples

[Examples of generated specs vs manual specs]

## Troubleshooting

**Q**: Code Index not found, what should I do?
**A**: Skill will fallback to Grep (slower but works). To regenerate Code Index, run architecture-reuse-check skill.

**Q**: Time estimate seems way off, how do I fix it?
**A**: Report actual time after implementation, skill will learn and improve estimates.
```

---

### Developer Documentation

**Inline Documentation**:

```python
# In spec-creation-automation.md skill file
"""
# Spec Creation Automation Skill

**Purpose**: Automate technical specification creation for architect agent

**Time Savings**: 92 minutes per spec (117 min → 25 min)
**Frequency**: 15-20 specs per month
**Monthly Savings**: 23-30.7 hours

## Architecture

This skill executes 6 stages sequentially:

Stage 1: Template Auto-Population (extracts from ROADMAP)
Stage 2: Code Discovery Engine (finds relevant files using Code Index)
Stage 3: Dependency Analyzer (traces imports, detects cycles)
Stage 4: Time Estimator (data-driven estimation with historical data)
Stage 5: Risk Identifier (pattern-based heuristics)
Stage 6: Spec Formatter (combines all sections into final spec)

## Inputs (via variables)

- $PRIORITY_NAME: e.g., "PRIORITY 10"
- $PRIORITY_CONTENT: Full ROADMAP priority text
- $CODE_INDEX_PATH: Path to Code Index JSON (from SPEC-001)
- $TEMPLATE_PATH: Path to spec template (SPEC-000-template.md)
- $HISTORICAL_DATA_PATH: Path to historical data (data/time_estimates.json)
- $MAX_DEPENDENCY_DEPTH: How deep to trace dependencies (default: 3)

## Outputs

Complete spec (markdown string) with:
- 90% sections auto-filled
- Architect notes on what to review
- Estimated review time: 25 minutes

## Performance

- Execution time: <60 seconds
- Code Discovery: <30 seconds
- Dependency Analysis: <20 seconds

## Accuracy

- Code Discovery: >90% precision
- Time Estimates: ±20% of actual (improves over time)
- Risk Identification: >80% recall

## Dependencies

- Code Index (from SPEC-001)
- ROADMAP parser (cached_roadmap_parser.py)
- Template (SPEC-000-template.md)
- Historical data (data/time_estimates.json)

## Future Enhancements

- AI-powered spec review (quality checks)
- Automatic ADR generation
- Spec diff/comparison tool
- Integration with Langfuse (prompt versioning)
"""
```

---

## Security Considerations

1. **File Path Validation**:
   - Validate all file paths before reading (prevent path traversal)
   - Ensure paths are within project directory
   - Reject absolute paths outside project root

2. **Code Execution**:
   - Never execute code from ROADMAP or specs
   - Only parse AST (no `eval()` or `exec()`)
   - Sandbox any LLM-generated code

3. **Sensitive Data**:
   - Don't include sensitive data in specs (API keys, passwords)
   - Warn if sensitive patterns detected ("password", "api_key", "secret")
   - Redact sensitive values in logs

4. **Dependency Security**:
   - Check external dependencies for CVEs (safety database)
   - Warn architect if dependency has known vulnerabilities
   - Require architect approval for all NEW dependencies

---

## Cost Estimate

### Development Cost

- **Implementation**: 10 hours (architect + code_developer)
- **Testing**: 3 hours (unit + integration tests)
- **Documentation**: 2 hours (user guide + inline docs)
- **Total**: 15 hours (~2 weeks at 50% allocation)

### Infrastructure Cost

- **Storage**: <1 MB for historical data (data/time_estimates.json)
- **Compute**: Negligible (runs locally, <60s per execution)
- **Total**: $0 per month

### Ongoing Maintenance

- **Bug fixes**: 1 hour per month (if issues arise)
- **Accuracy improvements**: 2 hours per quarter (tune formula, patterns)
- **Total**: ~1.5 hours per month

### ROI Calculation

**Investment**: 15 hours (one-time)

**Return (Month 1)**:
- Specs created: 15-20
- Time saved per spec: 92 minutes
- Total time saved: 1,380-1,840 minutes (23-30.7 hours)

**Net Gain (Month 1)**: 23-30.7 hours - 15 hours = **8-15.7 hours**

**ROI (Month 1)**: (8-15.7) / 15 = **53-105% return**

**ROI (Year 1)**: (23-30.7 hours × 12 months) / 15 hours = **18-24x return**

**Break-even**: <1 month 🚀

---

## Future Enhancements

### Version 2 (Future)

1. **AI-Powered Spec Review**:
   - LLM reads generated spec
   - Checks for completeness, clarity, consistency
   - Suggests improvements (e.g., "Add database schema diagram")
   - Quality score: 0-100

2. **Automatic ADR Generation**:
   - Detect architectural decisions in spec
   - Generate ADR draft from decisions
   - Link ADR to spec

3. **Spec Diff/Comparison Tool**:
   - Track spec changes over time
   - Show what changed between versions
   - Highlight architect additions vs auto-generated

4. **Integration with Langfuse**:
   - Store specs in Langfuse (versioning)
   - Track spec quality metrics (architect feedback)
   - A/B test spec generation strategies

5. **Multi-Language Support**:
   - Support other languages (JavaScript, Go, Rust)
   - Adapt Code Index to language-specific structures

**Priority**: LOW (only add if users request)

**Estimated Effort**: 20-30 hours (Phase 2)

---

## References

- **PROPOSED_SKILLS_2025-10-18.md** (lines 285-381): Original skill proposal
- **SPEC-001**: Advanced Code Search Skills (Code Index infrastructure)
- **SPEC-047**: Architect-Only Spec Creation Enforcement
- **ADR-009**: Retire code-searcher agent, replace with skills
- **SPEC-000-template.md**: Standard spec template
- **cached_roadmap_parser.py**: ROADMAP parser (existing)
- **skill_loader.py**: Skill loading infrastructure (existing)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-18 | Created | architect |
| 2025-10-18 | Status: Draft | architect |

---

## Approval

- [ ] architect (author)
- [ ] code_developer (implementer)
- [ ] project_manager (strategic alignment)
- [ ] User (final approval)

**Approval Date**: Pending

---

## Implementation Checklist

### Phase 1: Core Implementation (6 hours)
- [ ] Create skill file: `.claude/skills/spec-creation-automation.md`
- [ ] Implement Stage 1: Template Auto-Population
- [ ] Implement Stage 2: Code Discovery Engine
- [ ] Implement Stage 6: Spec Formatter
- [ ] Write unit tests for Stages 1, 2, 6
- [ ] Integration test: End-to-end workflow

### Phase 2: Advanced Features (4 hours)
- [ ] Implement Stage 3: Dependency Analyzer
- [ ] Implement Stage 4: Time Estimator
- [ ] Create `data/time_estimates.json`
- [ ] Write unit tests for Stages 3, 4

### Phase 3: Risk Identification (2 hours)
- [ ] Implement Stage 5: Risk Identifier
- [ ] Define risk patterns (performance, security, scalability)
- [ ] Write unit tests for risk detection

### Phase 4: Integration & Testing (2 hours)
- [ ] Integrate all 6 stages
- [ ] Add to `SkillNames` enum
- [ ] Write integration tests
- [ ] Test with 3-5 real ROADMAP priorities
- [ ] Measure time savings

### Phase 5: Production Deployment (1 hour)
- [ ] Update architect agent documentation
- [ ] Create user guide: `docs/skills/spec-creation-automation.md`
- [ ] Set up metrics tracking
- [ ] Monitor first 5 spec creations

**Total Effort**: 15 hours

---

**Remember**: This skill saves 23-30.7 hours per month by automating repetitive spec creation work. The architect can focus on what only a human architect can do: architectural insights, trade-off analysis, and strategic design decisions. The skill handles the boilerplate! 🚀

**Status**: Ready for implementation
**Next Step**: code_developer reads this spec and implements Phase 1
