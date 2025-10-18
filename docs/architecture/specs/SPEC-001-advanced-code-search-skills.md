# SPEC-001: Advanced Code Search Skills Architecture

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: User request for improved code search capabilities

---

## Executive Summary

This specification defines four critical code search skills that enhance the architect agent's ability to analyze codebases, create detailed technical specifications, and accurately estimate implementation efforts. The system uses a 3-level hierarchical code index as shared infrastructure, enabling rapid functional searches, code explanations, and automated index maintenance.

**Key Benefits**:
- **Better Specs**: architect can identify ALL impacted code zones before designing
- **Accurate Estimates**: architect can measure scope (files, LOC, complexity) for time estimation
- **Deep Understanding**: architect can explain existing patterns to guide new implementations
- **Always Current**: Automated index updates keep code maps fresh

**Four Skills**:
1. **Code Index (Infrastructure)** - 3-level hierarchical codebase map (auto-updated, no agent ownership)
2. **Functional Code Search** - Find all code related to a feature (usable by: architect, assistant)
3. **Code Explanation & Summarization** - Explain code in accessible terms (usable by: architect, assistant)
4. **Index Update & Maintenance** - Keep index current (automated via git hooks + cron)

**Note**: The code-searcher agent has been RETIRED (see ADR-009). These skills are now available to ALL agents, not owned by any specific agent.

---

## Problem Statement

### Current Pain Points

**1. Incomplete Impact Analysis**
When architect creates technical specs, they may miss code zones affected by a feature:
- Manual grep/glob searches are ad-hoc and incomplete
- No systematic way to find "all authentication-related code"
- Risk of incomplete specifications leading to rework

**2. Inaccurate Time Estimates**
Without knowing the full scope, architect cannot estimate implementation time:
- How many files need modification?
- How complex is the existing code?
- Are there hidden dependencies?

**3. Pattern Duplication**
architect cannot easily find existing implementations to reuse:
- "How do we currently handle caching?"
- "Where else do we validate user input?"
- Leads to inconsistent patterns

**4. Large Codebase Scaling**
With 55,807 lines of Python code, manual search is inefficient:
- Search results are overwhelming without structure
- No way to navigate from high-level concept → specific implementation
- 3 levels of hierarchy needed for effective navigation

### User Requirements

From the user request:
- **Functional Search**: "Find all code related to 'authentication'"
- **3-Level Hierarchy**: Codebase → Component → Implementation (file:line_start:line_end)
- **Code Explanation**: Summarize code for architect's understanding
- **Auto-Update**: Index stays current as code changes
- **Agent Ownership**: Clear responsibility (code-searcher for infrastructure, architect for consumption)

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REQUEST                                  │
│  "Design spec for payment processing feature"                   │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│              ARCHITECT AGENT                                   │
│  1. Uses Functional Code Search skill                         │
│  2. Finds ALL payment-related code zones                      │
│  3. Uses Code Explanation skill for each zone                 │
│  4. Creates comprehensive spec with accurate estimates        │
└───────────────┬───────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│          3-LEVEL CODE INDEX (Infrastructure)                   │
│  Level 1: Functional Categories (Payment, Auth, Notifications)│
│  Level 2: Components (Gateway Integration, Validation)        │
│  Level 3: Implementations (stripe_payment.py:45-89)           │
│                                                                │
│  Maintained by: code-searcher agent                           │
│  Consumed by: architect agent                                 │
└───────────────┬───────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│         INDEX UPDATE SKILL (code-searcher-owned)              │
│  - Triggered by: git commits, file changes, manual requests   │
│  - Analyzes code structure and updates index                  │
│  - Runs incrementally for performance                         │
└───────────────────────────────────────────────────────────────┘
```

### Workflow Example

```
User: "Design payment processing feature"
         ↓
architect: "Search for 'payment' functionality"
         ↓
Functional Code Search Skill:
   Query: "payment"
   Results:
   Level 1: Payment Processing
      Level 2: Stripe Integration
         Level 3: coffee_maker/payment/stripe_gateway.py:45-89
         Level 3: coffee_maker/payment/stripe_gateway.py:120-150
      Level 2: Payment Validation
         Level 3: coffee_maker/payment/validators.py:30-67
      Level 2: Payment Webhooks
         Level 3: coffee_maker/api/webhooks/stripe.py:15-45
   Level 1: Invoice Generation
      Level 2: PDF Generation
         Level 3: coffee_maker/invoices/pdf_generator.py:100-200
         ↓
architect: "Explain stripe_gateway.py:45-89"
         ↓
Code Explanation Skill:
   Summary: "This code initializes Stripe client with API key,
            implements payment charge with error handling,
            supports idempotency keys, returns transaction ID"
   Complexity: Medium (50 LOC, 3 dependencies)
         ↓
architect creates SPEC-002-payment-processing.md:
   - Affected Files: 4 (payment/, api/, invoices/)
   - Complexity: Medium
   - Estimated Time: 6-8 hours (based on scope analysis)
   - Patterns to Follow: stripe_gateway.py error handling
   - Integration Points: webhooks/stripe.py
```

---

## 1. Code Index - 3-Level Hierarchical Structure

### 1.1 Architecture Overview

The Code Index is a **hierarchical knowledge graph** of the codebase with exactly 3 levels:

**Level 1: Functional Categories**
- High-level business/technical domains
- Examples: "Authentication", "Payment Processing", "Notification System", "Data Storage"
- User-facing concepts that architect thinks in
- Typically 10-20 categories for a medium codebase

**Level 2: Components/Sub-systems**
- Specific components within each category
- Examples under "Authentication": "Login Flow", "Password Reset", "JWT Validation", "Session Management"
- Technical implementations of Level 1 concepts
- Typically 3-8 components per category

**Level 3: Code Implementations**
- Exact file locations with line ranges
- Format: `relative/path/to/file.py:line_start:line_end`
- Examples: `coffee_maker/auth/login.py:45-89`, `coffee_maker/auth/jwt_utils.py:120-180`
- Granular enough to jump directly to code
- Typically 1-10 implementations per component

**Why 3 Levels?**
- **Navigability**: Users think in concepts (L1) → components (L2) → code (L3)
- **Manageability**: Large codebases (55K+ LOC) need hierarchy to avoid overwhelming results
- **Cognitive Load**: 3 levels match human working memory (7±2 items per level)
- **Specificity**: L3 provides exact line numbers for direct navigation

### 1.2 Data Structure

**Format**: JSON with nested structure

```json
{
  "index_version": "1.0.0",
  "generated_at": "2025-10-18T10:30:00Z",
  "codebase_stats": {
    "total_files": 450,
    "total_lines": 55807,
    "python_files": 380,
    "last_commit": "0de4e17"
  },
  "categories": [
    {
      "id": "auth",
      "name": "Authentication & Authorization",
      "description": "User authentication, authorization, session management",
      "components": [
        {
          "id": "auth.login",
          "name": "Login Flow",
          "description": "User login, credential validation, session creation",
          "implementations": [
            {
              "file": "coffee_maker/auth/login.py",
              "line_start": 45,
              "line_end": 89,
              "description": "Main login handler with email/password",
              "complexity": "medium",
              "dependencies": ["jwt_utils", "user_repository"],
              "last_modified": "2025-10-15"
            },
            {
              "file": "coffee_maker/auth/oauth_login.py",
              "line_start": 20,
              "line_end": 60,
              "description": "OAuth2 login flow (Google, GitHub)",
              "complexity": "high",
              "dependencies": ["oauth_client", "session_manager"],
              "last_modified": "2025-10-10"
            }
          ]
        },
        {
          "id": "auth.jwt",
          "name": "JWT Token Management",
          "description": "JWT token generation, validation, refresh",
          "implementations": [
            {
              "file": "coffee_maker/auth/jwt_utils.py",
              "line_start": 15,
              "line_end": 50,
              "description": "JWT token generation with claims",
              "complexity": "low",
              "dependencies": ["pyjwt"],
              "last_modified": "2025-10-12"
            },
            {
              "file": "coffee_maker/auth/jwt_utils.py",
              "line_start": 55,
              "line_end": 90,
              "description": "JWT token validation and decoding",
              "complexity": "medium",
              "dependencies": ["pyjwt"],
              "last_modified": "2025-10-12"
            }
          ]
        }
      ]
    },
    {
      "id": "payment",
      "name": "Payment Processing",
      "description": "Payment gateway integration, transaction handling",
      "components": [
        {
          "id": "payment.stripe",
          "name": "Stripe Integration",
          "description": "Stripe payment gateway integration",
          "implementations": [
            {
              "file": "coffee_maker/payment/stripe_gateway.py",
              "line_start": 45,
              "line_end": 120,
              "description": "Stripe payment charge processing",
              "complexity": "high",
              "dependencies": ["stripe", "payment_repository"],
              "last_modified": "2025-10-14"
            }
          ]
        }
      ]
    }
  ]
}
```

**Field Definitions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (kebab-case) |
| `name` | string | Yes | Human-readable name |
| `description` | string | Yes | Brief explanation of purpose |
| `file` | string | Yes (L3) | Relative path from project root |
| `line_start` | integer | Yes (L3) | Starting line number (inclusive) |
| `line_end` | integer | Yes (L3) | Ending line number (inclusive) |
| `complexity` | enum | Yes (L3) | "low", "medium", "high" |
| `dependencies` | array | No | List of imported modules/packages |
| `last_modified` | date | Yes (L3) | Last git commit date for this code |

### 1.3 Storage & Access

**Storage Location**: `data/code_index/index.json`

**Why This Location?**
- `data/` directory: Runtime-generated data (not checked into git)
- Version controlled separately from code
- Can be regenerated from source code at any time
- Multiple index versions can coexist (e.g., `index_v1.json`, `index_v2.json`)

**Access Patterns**:

```python
# Load entire index
from coffee_maker.code_index.loader import CodeIndexLoader

index = CodeIndexLoader.load()  # Loads data/code_index/index.json

# Query by functional category
auth_category = index.get_category("auth")

# Query by component
login_component = index.get_component("auth.login")

# Query by keyword (searches names + descriptions)
payment_results = index.search("payment")
# Returns: [(category, component, implementation), ...]

# Get all implementations for a category
auth_implementations = index.get_implementations("auth")
# Returns: [Implementation(...), Implementation(...), ...]
```

**Caching Strategy**:
- Index loaded into memory on first access
- Cached for duration of agent session
- Cache invalidated on index file modification
- ~1-2 MB memory footprint for typical codebase

**Concurrency**:
- Read-only access by architect (no locking needed)
- Write access by code-searcher (file-level locking during update)
- Index update creates temp file → atomic rename (no partial reads)

### 1.4 Update Mechanism

**Update Triggers**:

1. **Manual Trigger** (on-demand)
   ```bash
   poetry run code-searcher rebuild-index
   ```

2. **Git Hook Trigger** (automatic)
   - Post-commit hook: Detect changed files, trigger incremental update
   - Post-merge hook: Full rebuild on branch merges

3. **Scheduled Trigger** (nightly)
   - Cron job: Daily full rebuild at 2am
   - Ensures index freshness even if hooks fail

**Update Process**:

```python
class IndexUpdater:
    def update(self, trigger: UpdateTrigger) -> IndexUpdateResult:
        """Update code index based on trigger type."""

        if trigger.type == "full_rebuild":
            return self._full_rebuild()
        elif trigger.type == "incremental":
            return self._incremental_update(trigger.changed_files)

    def _full_rebuild(self) -> IndexUpdateResult:
        """Rebuild entire index from scratch."""
        # 1. Analyze all Python files in codebase
        # 2. Extract functions, classes, methods
        # 3. Cluster into functional categories using embeddings
        # 4. Generate component groupings
        # 5. Create implementation entries with line numbers
        # 6. Write to data/code_index/index_temp.json
        # 7. Atomic rename to index.json

    def _incremental_update(self, changed_files: List[str]) -> IndexUpdateResult:
        """Update only changed files."""
        # 1. Load existing index
        # 2. For each changed file:
        #    a. Re-analyze file
        #    b. Update affected implementations
        #    c. Re-cluster if category/component changed
        # 3. Write updated index
```

**Performance**:
- Full Rebuild: ~30 seconds for 55K LOC codebase
- Incremental Update: ~2 seconds for 1-5 file changes
- Background Task: Updates don't block agent operations

### 1.5 Example Index Entry

**Scenario**: Indexing authentication code in MonolithicCoffeeMakerAgent

```json
{
  "id": "autonomous_agents",
  "name": "Autonomous Agent System",
  "description": "Multi-agent system for autonomous software development",
  "components": [
    {
      "id": "autonomous_agents.daemon",
      "name": "Code Developer Daemon",
      "description": "Main daemon for autonomous feature implementation",
      "implementations": [
        {
          "file": "coffee_maker/autonomous/daemon.py",
          "line_start": 50,
          "line_end": 100,
          "description": "Daemon initialization and startup",
          "complexity": "high",
          "dependencies": ["langfuse_observe", "prompt_loader", "developer_status"],
          "last_modified": "2025-10-15"
        },
        {
          "file": "coffee_maker/autonomous/daemon.py",
          "line_start": 150,
          "line_end": 220,
          "description": "Main work loop - processes ROADMAP priorities",
          "complexity": "high",
          "dependencies": ["spec_manager", "implementation_mixin"],
          "last_modified": "2025-10-15"
        }
      ]
    },
    {
      "id": "autonomous_agents.spec_manager",
      "name": "Specification Manager",
      "description": "Creates technical specifications before implementation",
      "implementations": [
        {
          "file": "coffee_maker/autonomous/daemon_spec_manager.py",
          "line_start": 30,
          "line_end": 80,
          "description": "Spec creation workflow using prompts",
          "complexity": "medium",
          "dependencies": ["prompt_loader", "claude_cli_interface"],
          "last_modified": "2025-10-12"
        }
      ]
    },
    {
      "id": "autonomous_agents.status_tracking",
      "name": "Developer Status Tracking",
      "description": "Real-time status updates and progress monitoring",
      "implementations": [
        {
          "file": "coffee_maker/autonomous/developer_status.py",
          "line_start": 45,
          "line_end": 120,
          "description": "Status update and persistence",
          "complexity": "low",
          "dependencies": ["pydantic", "json"],
          "last_modified": "2025-10-10"
        }
      ]
    }
  ]
}
```

**Usage by architect**:

```python
# architect creates spec for "improve daemon error handling"
index = CodeIndexLoader.load()

# Find all daemon-related code
daemon_code = index.search("daemon")
# Returns:
# - autonomous_agents.daemon (3 implementations)
# - autonomous_agents.spec_manager (1 implementation)
# - autonomous_agents.status_tracking (1 implementation)

# Get specific implementation details
main_loop = index.get_implementation(
    "coffee_maker/autonomous/daemon.py:150:220"
)
# Returns: Implementation object with dependencies, complexity, description

# architect now knows:
# - 5 total code locations to review
# - Main loop is high complexity (needs careful design)
# - Dependencies: spec_manager, implementation_mixin
# - Estimated time: 4-6 hours (based on complexity + LOC)
```

---

## 2. Skill: Functional Code Search (architect-owned)

### 2.1 Capabilities

**Purpose**: Enable architect to find ALL code related to a business/technical function.

**What It Does**:
1. Accepts functional query (e.g., "authentication", "payment processing", "caching")
2. Searches Code Index across all 3 levels
3. Returns hierarchical results with exact file:line locations
4. Includes complexity and dependency information
5. Provides scope metrics (total files, LOC, estimated effort)

**Search Types**:

| Search Type | Example Query | Use Case |
|-------------|---------------|----------|
| Exact Match | "JWT validation" | Find specific component |
| Keyword | "payment" | Find all payment-related code |
| Multi-keyword | "user authentication login" | Broad search across related concepts |
| Category | "category:auth" | List all authentication code |
| Dependency | "depends:stripe" | Find code using Stripe |
| Complexity | "complexity:high" | Find complex code needing review |

### 2.2 Usage Pattern

**Workflow for architect**:

```python
# Step 1: architect receives task to create spec
task = "Design caching layer for API responses"

# Step 2: Use Functional Code Search
from coffee_maker.code_index.search import FunctionalCodeSearch

search = FunctionalCodeSearch()
results = search.query("caching")

# Step 3: Review results
print(results.summary())
# Output:
# Found 3 categories, 5 components, 12 implementations
# Total files: 8
# Total LOC: ~450 lines
# Complexity distribution: 3 high, 6 medium, 3 low
# Estimated review time: 2-3 hours

# Step 4: Examine each result
for category in results.categories:
    print(f"\n{category.name}:")
    for component in category.components:
        print(f"  - {component.name}")
        for impl in component.implementations:
            print(f"    • {impl.file}:{impl.line_start}-{impl.line_end}")
            print(f"      Complexity: {impl.complexity}")
            print(f"      Dependencies: {', '.join(impl.dependencies)}")

# Step 5: architect creates spec with comprehensive scope
spec = TechnicalSpec(
    title="API Response Caching Layer",
    affected_files=results.get_files(),  # ['file1.py', 'file2.py', ...]
    complexity=results.max_complexity(),  # 'high'
    estimated_time=results.estimate_hours(),  # 6-8 hours
    integration_points=results.get_dependencies(),  # ['redis', 'fastapi']
    existing_patterns=results.get_component_ids()  # ['cache.redis', 'cache.memory']
)
```

**When architect uses this skill**:
- Before creating technical specs (understand existing code)
- When estimating implementation time (measure scope)
- When identifying patterns to reuse (find similar implementations)
- When assessing risk (find high-complexity zones)

### 2.3 Integration with Code Index

**Query Processing**:

```python
class FunctionalCodeSearch:
    def __init__(self):
        self.index = CodeIndexLoader.load()

    def query(self, query_string: str, filters: dict = None) -> SearchResults:
        """Execute functional search against code index."""

        # 1. Parse query
        query = self._parse_query(query_string)
        # Example: "payment stripe" → ["payment", "stripe"]

        # 2. Search Level 1 (Categories)
        matching_categories = self._search_categories(query)
        # Searches category names + descriptions

        # 3. Search Level 2 (Components)
        matching_components = self._search_components(query)
        # Searches component names + descriptions

        # 4. Search Level 3 (Implementations)
        matching_implementations = self._search_implementations(query)
        # Searches implementation descriptions

        # 5. Apply filters
        if filters:
            results = self._apply_filters(results, filters)
            # Example: filters={'complexity': 'high'}

        # 6. Rank results by relevance
        ranked_results = self._rank_results(results, query)
        # Exact matches ranked higher than partial matches

        # 7. Return hierarchical results
        return SearchResults(
            categories=matching_categories,
            components=matching_components,
            implementations=matching_implementations,
            metadata=self._compute_metadata(results)
        )
```

**Ranking Algorithm**:
1. **Exact Match** (Score: 100): Query matches category/component name exactly
2. **Partial Match** (Score: 75): Query terms found in name or description
3. **Dependency Match** (Score: 50): Query matches dependency
4. **Recency Boost** (+10): Recently modified code ranked higher
5. **Complexity Penalty** (-5 for high): De-prioritize complex code for simpler alternatives

### 2.4 Output Format

**Terminal Output** (for architect's review):

```
=== Functional Code Search Results ===
Query: "payment processing"
Filters: None

📊 Summary:
  - Categories: 2
  - Components: 5
  - Implementations: 12
  - Total Files: 8
  - Total LOC: ~650 lines
  - Complexity: 4 high, 5 medium, 3 low
  - Estimated Review Time: 3-4 hours
  - Estimated Implementation Time: 8-12 hours (if creating similar feature)

📁 Category: Payment Processing
  📂 Component: Stripe Integration [HIGH COMPLEXITY]
     📄 coffee_maker/payment/stripe_gateway.py:45-120
        Description: Stripe payment charge processing
        Dependencies: stripe, payment_repository
        Complexity: high
        Last Modified: 2025-10-14

     📄 coffee_maker/payment/stripe_gateway.py:125-180
        Description: Stripe webhook event handling
        Dependencies: stripe, webhooks
        Complexity: medium
        Last Modified: 2025-10-14

  📂 Component: Payment Validation [MEDIUM COMPLEXITY]
     📄 coffee_maker/payment/validators.py:30-67
        Description: Credit card validation using Luhn algorithm
        Dependencies: None
        Complexity: low
        Last Modified: 2025-10-10

📁 Category: Invoice Generation
  📂 Component: PDF Generation [HIGH COMPLEXITY]
     📄 coffee_maker/invoices/pdf_generator.py:100-200
        Description: Invoice PDF generation from payment data
        Dependencies: reportlab, payment_models
        Complexity: high
        Last Modified: 2025-10-12

💡 Insights:
  - 4 high-complexity implementations (may need refactoring)
  - Stripe is primary dependency (consider vendor lock-in)
  - Payment validation is low complexity (easy to extend)
  - Recent activity in stripe_gateway.py (potential ongoing work)
```

**Programmatic Output** (for architect's automation):

```python
@dataclass
class SearchResults:
    """Results from functional code search."""

    categories: List[Category]
    components: List[Component]
    implementations: List[Implementation]
    metadata: SearchMetadata

    def get_files(self) -> List[str]:
        """Get list of all affected files."""
        return [impl.file for impl in self.implementations]

    def get_line_count(self) -> int:
        """Get total lines of code."""
        return sum(impl.line_end - impl.line_start + 1
                   for impl in self.implementations)

    def get_dependencies(self) -> Set[str]:
        """Get all dependencies."""
        deps = set()
        for impl in self.implementations:
            deps.update(impl.dependencies)
        return deps

    def max_complexity(self) -> str:
        """Get highest complexity level."""
        complexities = [impl.complexity for impl in self.implementations]
        if "high" in complexities:
            return "high"
        elif "medium" in complexities:
            return "medium"
        return "low"

    def estimate_hours(self) -> tuple[int, int]:
        """Estimate implementation time (min, max) in hours."""
        base_hours = self.get_line_count() / 100  # ~100 LOC per hour

        # Complexity multiplier
        complexity_multipliers = {"low": 1.0, "medium": 1.5, "high": 2.5}
        complexity_factor = sum(
            complexity_multipliers[impl.complexity]
            for impl in self.implementations
        ) / len(self.implementations)

        # Dependency penalty (more deps = more integration time)
        dep_penalty = len(self.get_dependencies()) * 0.5

        total_hours = base_hours * complexity_factor + dep_penalty

        # Return range (±25%)
        return (int(total_hours * 0.75), int(total_hours * 1.25))
```

### 2.5 Example Queries

**Example 1: Find all authentication code**
```python
results = search.query("authentication")

# Expected results:
# - Category: Authentication & Authorization
#   - Component: Login Flow (3 implementations)
#   - Component: JWT Management (2 implementations)
#   - Component: Session Management (4 implementations)
#   - Component: Password Reset (2 implementations)
# Total: 11 implementations across 6 files
```

**Example 2: Find high-complexity payment code**
```python
results = search.query("payment", filters={"complexity": "high"})

# Expected results:
# - Category: Payment Processing
#   - Component: Stripe Integration
#     - stripe_gateway.py:45-120 (HIGH)
#   - Component: Payment Reconciliation
#     - reconciliation.py:200-350 (HIGH)
# Total: 2 high-complexity implementations
```

**Example 3: Find code using specific dependency**
```python
results = search.query("depends:redis")

# Expected results:
# - Category: Caching
#   - Component: Redis Cache (3 implementations)
# - Category: Session Management
#   - Component: Redis Sessions (2 implementations)
# - Category: Task Queue
#   - Component: Redis Queue (1 implementation)
# Total: 6 implementations using Redis
```

**Example 4: Find recent changes in notification system**
```python
results = search.query("notification", filters={"modified_after": "2025-10-01"})

# Expected results:
# - Category: Notification System
#   - Component: Email Notifications
#     - email_sender.py:50-100 (modified: 2025-10-05)
#   - Component: Push Notifications
#     - push_sender.py:30-80 (modified: 2025-10-12)
# Total: 2 recently modified implementations
```

**Example 5: Estimate scope for caching feature**
```python
results = search.query("cache caching")

print(f"Files to modify: {len(results.get_files())}")
print(f"Lines of code: {results.get_line_count()}")
print(f"Dependencies: {results.get_dependencies()}")
print(f"Estimated time: {results.estimate_hours()[0]}-{results.estimate_hours()[1]} hours")

# Output:
# Files to modify: 8
# Lines of code: 450
# Dependencies: {'redis', 'functools', 'asyncio'}
# Estimated time: 6-8 hours
```

---

## 3. Skill: Code Explanation & Summarization (architect-owned)

### 3.1 Capabilities

**Purpose**: Explain code in accessible, technical terms for architect's understanding.

**What It Does**:
1. Accepts code location (`file:line_start:line_end`) or Implementation object
2. Analyzes code structure, logic, dependencies
3. Generates multi-level summaries (executive, technical, implementation)
4. Identifies patterns, complexity, potential issues
5. Suggests architectural improvements

**Explanation Levels**:

| Level | Audience | Detail | Length |
|-------|----------|--------|--------|
| Executive | Non-technical | What it does, why it matters | 1-2 sentences |
| Technical | architect | How it works, patterns used, dependencies | 1 paragraph |
| Implementation | code_developer | Line-by-line logic, edge cases, TODOs | Detailed breakdown |

### 3.2 Usage Pattern

**Workflow for architect**:

```python
from coffee_maker.code_index.explainer import CodeExplainer

explainer = CodeExplainer()

# Step 1: Get implementation from search results
results = search.query("stripe payment")
impl = results.implementations[0]  # stripe_gateway.py:45-120

# Step 2: Generate explanation
explanation = explainer.explain(impl, level="technical")

# Step 3: Review explanation
print(explanation.summary)
# Output:
# "This code implements Stripe payment charge processing with idempotency
# support. It uses the Stripe SDK to create charges, handles errors with
# retry logic, validates payment amounts, and stores transaction records
# in PaymentRepository. Pattern: Repository pattern for data access."

print(explanation.complexity_analysis)
# Output:
# Complexity: HIGH
# Reasons:
# - External API integration (Stripe)
# - Error handling for network failures
# - Idempotency key management
# - Database transactions
# Lines of Code: 75
# Cyclomatic Complexity: 12

print(explanation.dependencies)
# Output:
# - stripe (external): Stripe Python SDK
# - payment_repository (internal): Database access layer
# - idempotency_store (internal): Idempotency key storage

print(explanation.potential_issues)
# Output:
# - No rate limiting on Stripe API calls
# - Hard-coded API key (should use environment variable)
# - Missing logging for failed payments

print(explanation.patterns)
# Output:
# - Repository Pattern: PaymentRepository for data access
# - Idempotency Pattern: Prevents duplicate charges
# - Retry Pattern: Exponential backoff for network errors

# Step 4: Use in spec creation
spec.add_section(
    "Existing Implementation Analysis",
    explanation.summary
)
spec.add_risks(explanation.potential_issues)
spec.add_patterns_to_follow(explanation.patterns)
```

### 3.3 Output Levels

**Executive Level** (1-2 sentences):
```
This code processes Stripe payments with error handling and idempotency
support. It charges credit cards, stores transaction records, and handles
failures gracefully.
```

**Technical Level** (1 paragraph):
```
This implementation integrates with the Stripe payment gateway using the
official Python SDK. It accepts payment parameters (amount, currency,
customer_id), generates idempotency keys to prevent duplicate charges,
and creates Stripe charge objects. Error handling includes retry logic
with exponential backoff for transient failures (network issues, rate
limits). Successful charges are persisted to the database using the
Repository pattern (PaymentRepository). The code follows defensive
programming practices with input validation and comprehensive logging.
Dependencies: stripe SDK (external), payment_repository (internal),
idempotency_store (internal).
```

**Implementation Level** (detailed breakdown):
```
Line-by-line Analysis:

Lines 45-52: Input Validation
- Validates amount > 0, currency in allowed list
- Checks customer_id exists in database
- Raises ValueError for invalid inputs

Lines 53-60: Idempotency Key Generation
- Generates unique key from (customer_id, amount, timestamp)
- Checks idempotency_store for existing key (prevent duplicates)
- Pattern: Idempotency ensures retry-safety

Lines 61-75: Stripe API Call
- Creates Stripe charge with validated parameters
- Passes idempotency_key to Stripe API
- Uses exponential backoff retry (3 attempts)
- Handles StripeError exceptions (network, auth, validation)

Lines 76-85: Transaction Persistence
- Wraps database write in transaction
- Creates Payment record in PaymentRepository
- Links to Customer record via foreign key
- Commits transaction on success

Lines 86-95: Error Handling
- Catches StripeError: Logs and re-raises with context
- Catches DatabaseError: Rolls back transaction
- Returns transaction_id on success

Lines 96-100: Logging
- Logs payment attempt (INFO level)
- Logs success with transaction_id (INFO level)
- Logs failures with stack trace (ERROR level)

Complexity Analysis:
- Cyclomatic Complexity: 12 (high)
- Nested depth: 3 levels (moderate)
- Error paths: 5 (comprehensive)

Potential Issues:
- Hard-coded Stripe API key (line 65) → Use environment variable
- No rate limiting → Risk of hitting Stripe API limits
- Missing timeout on Stripe API call → Could hang indefinitely

Improvement Suggestions:
- Extract configuration to environment variables
- Add rate limiting using token bucket algorithm
- Add timeout parameter to Stripe API call (max 30 seconds)
- Consider circuit breaker pattern for Stripe API failures
```

### 3.4 Example Outputs

**Example 1: Simple Function (Low Complexity)**

```python
# Input: coffee_maker/utils/string_utils.py:10-20
explanation = explainer.explain("coffee_maker/utils/string_utils.py:10:20",
                                level="technical")

# Output:
{
  "summary": "This function validates email addresses using regex pattern matching. It checks for valid format (local@domain.tld) and returns boolean.",
  "complexity": "low",
  "cyclomatic_complexity": 2,
  "lines_of_code": 10,
  "dependencies": ["re"],
  "patterns": ["Input Validation Pattern"],
  "potential_issues": [],
  "improvement_suggestions": [
    "Consider using email-validator library for RFC-compliant validation"
  ]
}
```

**Example 2: Complex Class (High Complexity)**

```python
# Input: coffee_maker/autonomous/daemon.py:50-150
explanation = explainer.explain("coffee_maker/autonomous/daemon.py:50:150",
                                level="technical")

# Output:
{
  "summary": "This class implements the autonomous code developer daemon. It orchestrates spec creation, implementation, and testing workflows using mixins for composition. Main loop processes ROADMAP priorities continuously.",
  "complexity": "high",
  "cyclomatic_complexity": 25,
  "lines_of_code": 100,
  "dependencies": [
    "langfuse_observe",
    "prompt_loader",
    "developer_status",
    "spec_manager_mixin",
    "implementation_mixin"
  ],
  "patterns": [
    "Mixin Pattern: Composition over inheritance",
    "State Machine Pattern: Tracks daemon state (idle, working, error)",
    "Observer Pattern: Langfuse observability integration"
  ],
  "potential_issues": [
    "High cyclomatic complexity (25) - consider breaking into smaller methods",
    "Mixin interdependencies - ensure proper initialization order"
  ],
  "improvement_suggestions": [
    "Extract workflow orchestration to separate WorkflowManager class",
    "Add state machine diagram to documentation",
    "Consider dependency injection for mixins"
  ]
}
```

**Example 3: API Endpoint (Medium Complexity)**

```python
# Input: coffee_maker/api/routes/users.py:45-90
explanation = explainer.explain("coffee_maker/api/routes/users.py:45:90",
                                level="technical")

# Output:
{
  "summary": "FastAPI endpoint for user registration. Validates input, checks for existing users, hashes passwords, creates user record, and returns JWT token.",
  "complexity": "medium",
  "cyclomatic_complexity": 8,
  "lines_of_code": 45,
  "dependencies": [
    "fastapi",
    "pydantic",
    "bcrypt",
    "jwt_utils",
    "user_repository"
  ],
  "patterns": [
    "Repository Pattern: UserRepository for data access",
    "DTO Pattern: Pydantic models for request/response",
    "Hashing Pattern: bcrypt for password security"
  ],
  "potential_issues": [
    "No rate limiting - vulnerable to brute force attacks",
    "Missing email verification flow"
  ],
  "improvement_suggestions": [
    "Add rate limiting using slowapi library",
    "Implement email verification with token",
    "Add CAPTCHA for bot prevention"
  ]
}
```

---

## 4. Skill: Index Update & Maintenance (code-searcher-owned)

### 4.1 Update Triggers

**1. Manual Trigger** (Highest Priority)
```bash
# Full rebuild
poetry run code-searcher rebuild-index

# Incremental update for specific files
poetry run code-searcher update-index coffee_maker/payment/*.py
```

**When to use**:
- After major refactoring
- When index seems outdated
- When adding new functional areas

**2. Git Hook Trigger** (Automatic)

**Post-Commit Hook** (`.git/hooks/post-commit`):
```bash
#!/bin/bash
# Trigger incremental index update after commit

changed_files=$(git diff-tree --no-commit-id --name-only -r HEAD)

if echo "$changed_files" | grep -q '\.py$'; then
    echo "Python files changed, updating code index..."
    poetry run code-searcher update-index --incremental
fi
```

**Post-Merge Hook** (`.git/hooks/post-merge`):
```bash
#!/bin/bash
# Trigger full rebuild after merge (potential conflicts)

echo "Merge detected, rebuilding code index..."
poetry run code-searcher rebuild-index --async
```

**3. File Watcher Trigger** (Real-time)
```python
# coffee_maker/code_index/watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeIndexWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            # Debounce: Update after 5 seconds of inactivity
            self.schedule_update(event.src_path)
```

**When to use**:
- Development mode with live updates
- Optional feature (can be disabled for performance)

**4. Scheduled Trigger** (Nightly)
```bash
# Cron job (crontab -e)
0 2 * * * cd /path/to/project && poetry run code-searcher rebuild-index
```

**When to use**:
- Ensures index freshness daily
- Catches missed updates from failed hooks

### 4.2 Update Algorithm

**Full Rebuild Algorithm**:

```python
class IndexRebuilder:
    """Rebuild entire code index from scratch."""

    def rebuild(self) -> IndexUpdateResult:
        """Full rebuild process."""

        # Phase 1: Code Discovery (10% of time)
        python_files = self._discover_python_files()
        # Uses glob to find all *.py files
        # Excludes: tests/, migrations/, __pycache__/

        # Phase 2: Code Parsing (40% of time)
        parsed_code = []
        for file in python_files:
            parsed = self._parse_file(file)
            # Extract: functions, classes, methods, docstrings
            # Record: line ranges, dependencies, complexity
            parsed_code.append(parsed)

        # Phase 3: Semantic Clustering (30% of time)
        categories = self._cluster_into_categories(parsed_code)
        # Uses: TF-IDF embeddings of function names + docstrings
        # Clustering: K-means with k=10-20 (auto-determined)
        # Results: Functional categories (auth, payment, notification, etc.)

        # Phase 4: Component Grouping (15% of time)
        for category in categories:
            category.components = self._group_components(category)
            # Groups related functions/classes into components
            # Heuristic: shared imports, naming patterns, file proximity

        # Phase 5: Implementation Extraction (5% of time)
        for category in categories:
            for component in category.components:
                component.implementations = self._extract_implementations(component)
                # Creates Implementation objects with:
                # - file path, line_start, line_end
                # - description, complexity, dependencies

        # Phase 6: Index Serialization
        index = self._build_index_object(categories)
        index.save("data/code_index/index_temp.json")

        # Phase 7: Atomic Rename
        os.rename("data/code_index/index_temp.json",
                  "data/code_index/index.json")

        return IndexUpdateResult(
            status="success",
            duration_seconds=elapsed_time,
            files_processed=len(python_files),
            categories_created=len(categories),
            implementations_created=total_implementations
        )
```

**Incremental Update Algorithm**:

```python
class IndexIncremental Updater:
    """Update index for changed files only."""

    def update(self, changed_files: List[str]) -> IndexUpdateResult:
        """Incremental update process."""

        # Phase 1: Load existing index
        index = CodeIndexLoader.load()

        # Phase 2: Identify affected implementations
        affected_impls = []
        for file in changed_files:
            impls = index.find_implementations_by_file(file)
            affected_impls.extend(impls)

        # Phase 3: Re-parse changed files
        new_parsed_code = []
        for file in changed_files:
            parsed = self._parse_file(file)
            new_parsed_code.append(parsed)

        # Phase 4: Update implementations in-place
        for parsed in new_parsed_code:
            # Find existing component for this code
            component = self._find_matching_component(parsed, index)

            if component:
                # Update existing implementations
                component.update_implementations(parsed)
            else:
                # Code moved to new component - re-cluster
                new_component = self._create_component(parsed)
                category = self._find_or_create_category(parsed, index)
                category.add_component(new_component)

        # Phase 5: Prune deleted implementations
        for impl in affected_impls:
            if not self._implementation_still_exists(impl):
                impl.component.remove_implementation(impl)

        # Phase 6: Save updated index
        index.save("data/code_index/index.json")

        return IndexUpdateResult(
            status="success",
            duration_seconds=elapsed_time,
            files_processed=len(changed_files),
            implementations_updated=len(affected_impls)
        )
```

### 4.3 Incremental vs Full Rebuild

**When to Use Incremental**:
- ✅ 1-10 files changed
- ✅ Changes within existing components
- ✅ No major refactoring
- ✅ Speed critical (2-5 seconds)

**When to Use Full Rebuild**:
- ✅ >10 files changed
- ✅ New functional areas added
- ✅ Major refactoring (file moves, renames)
- ✅ Index corruption suspected
- ✅ Nightly scheduled rebuild

**Decision Algorithm**:

```python
def decide_update_strategy(changed_files: List[str]) -> str:
    """Decide whether to do incremental or full rebuild."""

    # Rule 1: Too many changes → Full rebuild
    if len(changed_files) > 10:
        return "full_rebuild"

    # Rule 2: Critical files changed → Full rebuild
    critical_files = ["pyproject.toml", "setup.py", ".gitignore"]
    if any(f in changed_files for f in critical_files):
        return "full_rebuild"

    # Rule 3: Directory structure changed → Full rebuild
    dir_changes = [f for f in changed_files if "/" in f]
    if len(set(os.path.dirname(f) for f in dir_changes)) > 5:
        return "full_rebuild"

    # Rule 4: Default to incremental
    return "incremental"
```

**Performance Comparison**:

| Metric | Incremental (5 files) | Full Rebuild |
|--------|----------------------|--------------|
| Duration | 2-5 seconds | 30-60 seconds |
| CPU Usage | Low (5-10%) | High (50-80%) |
| Memory | 50 MB | 200 MB |
| Accuracy | 99% (if no re-clustering) | 100% |

### 4.4 Performance Considerations

**Optimization Techniques**:

1. **Parallel Processing**
   ```python
   from concurrent.futures import ProcessPoolExecutor

   def rebuild_parallel(self, files: List[str]) -> List[ParsedCode]:
       """Parse files in parallel using multiple cores."""
       with ProcessPoolExecutor(max_workers=4) as executor:
           return list(executor.map(self._parse_file, files))
   ```

2. **Caching Parse Results**
   ```python
   # Cache AST parsing results (file hash → parsed code)
   cache_key = hashlib.md5(open(file, 'rb').read()).hexdigest()

   if cache_key in parse_cache:
       return parse_cache[cache_key]  # Use cached result
   else:
       parsed = self._parse_file(file)
       parse_cache[cache_key] = parsed
       return parsed
   ```

3. **Lazy Loading**
   ```python
   class CodeIndex:
       def __init__(self):
           self._categories = None  # Not loaded yet

       @property
       def categories(self) -> List[Category]:
           """Lazy load categories on first access."""
           if self._categories is None:
               self._categories = self._load_categories()
           return self._categories
   ```

4. **Index Compression**
   ```python
   # Compress index JSON with gzip (reduces size by ~70%)
   import gzip

   with gzip.open("data/code_index/index.json.gz", 'wt') as f:
       json.dump(index_data, f)
   ```

**Performance Targets**:

| Operation | Target Time | Max Time |
|-----------|-------------|----------|
| Full Rebuild (55K LOC) | 30 seconds | 60 seconds |
| Incremental Update (5 files) | 2 seconds | 5 seconds |
| Index Load | 100 ms | 500 ms |
| Query Execution | 50 ms | 200 ms |

**Monitoring**:

```python
# Track performance metrics with Langfuse
from coffee_maker.langfuse_observe import observe

@observe(name="code_index_rebuild")
def rebuild_index():
    start = time.time()
    result = rebuilder.rebuild()
    duration = time.time() - start

    # Log metrics
    langfuse_client.log_metric("index_rebuild_duration", duration)
    langfuse_client.log_metric("files_processed", result.files_processed)
    langfuse_client.log_metric("categories_created", result.categories_created)
```

---

## 5. Integration Architecture

### 5.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │ architect    │      │user_listener │      │code_developer│ │
│  │ agent        │      │    agent     │      │    agent     │ │
│  └──────┬───────┘      └──────────────┘      └──────────────┘ │
│         │                                                       │
└─────────┼───────────────────────────────────────────────────────┘
          │
          │ Uses skills
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SKILL LAYER (architect-owned)               │
│                                                                  │
│  ┌────────────────────────────┐  ┌──────────────────────────┐  │
│  │ Functional Code Search     │  │ Code Explanation         │  │
│  │                            │  │ & Summarization          │  │
│  │ - Query parser             │  │                          │  │
│  │ - Hierarchical search      │  │ - Multi-level summaries  │  │
│  │ - Ranking algorithm        │  │ - Pattern detection      │  │
│  │ - Scope estimation         │  │ - Complexity analysis    │  │
│  └────────────┬───────────────┘  └───────┬──────────────────┘  │
│               │                           │                     │
└───────────────┼───────────────────────────┼─────────────────────┘
                │                           │
                │ Reads                     │ Reads
                ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER (code-searcher-owned)         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Code Index (index.json)                      │  │
│  │                                                            │  │
│  │  Level 1: Functional Categories                          │  │
│  │    ↓                                                      │  │
│  │  Level 2: Components                                     │  │
│  │    ↓                                                      │  │
│  │  Level 3: Implementations (file:line_start:line_end)     │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│                         │ Updated by                            │
│                         ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Index Update & Maintenance Skill                  │  │
│  │                                                            │  │
│  │  - Full rebuild algorithm                                │  │
│  │  - Incremental update algorithm                          │  │
│  │  - Git hook integration                                  │  │
│  │  - Performance optimization                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                         ▲
                         │ Triggers
┌────────────────────────┴─────────────────────────────────────────┐
│                      TRIGGER LAYER                                │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Manual     │  │ Git Hooks  │  │ File       │  │ Scheduled │ │
│  │ Trigger    │  │ (commit)   │  │ Watcher    │  │ (cron)    │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

**Flow 1: architect Creates Technical Spec**

```
1. User → user_listener: "Design payment refactoring"

2. user_listener → architect: Delegated task

3. architect → Functional Code Search:
   search.query("payment processing")

4. Functional Code Search → Code Index:
   index.search("payment processing")

5. Code Index → Functional Code Search:
   Returns: 2 categories, 5 components, 12 implementations

6. Functional Code Search → architect:
   Returns: SearchResults with hierarchy + metadata

7. architect → Code Explanation (for each high-priority implementation):
   explainer.explain("stripe_gateway.py:45-120", level="technical")

8. Code Explanation → architect:
   Returns: Technical summary, patterns, complexity, issues

9. architect → Technical Spec Creation:
   Creates: docs/architecture/specs/SPEC-002-payment-refactoring.md
   Includes:
   - Affected files: 8 files identified by search
   - Complexity: HIGH (from search metadata)
   - Estimated time: 8-12 hours (from search.estimate_hours())
   - Patterns to follow: Repository pattern, Idempotency pattern
   - Risks: Hard-coded API keys, no rate limiting

10. architect → user_listener:
    "Spec created at SPEC-002-payment-refactoring.md"

11. user_listener → User:
    Presents spec for review
```

**Flow 2: code-searcher Updates Index After Commit**

```
1. code_developer → Git Commit:
   Commits: coffee_maker/payment/stripe_gateway.py (modified)

2. Git Post-Commit Hook → Index Updater:
   Detects: 1 Python file changed

3. Index Updater → Decision Algorithm:
   changed_files = ["coffee_maker/payment/stripe_gateway.py"]
   Decision: "incremental" (only 1 file)

4. Index Updater → Incremental Update:
   a. Load existing index
   b. Find affected implementations:
      - payment.stripe → stripe_gateway.py:45-120
   c. Re-parse: coffee_maker/payment/stripe_gateway.py
   d. Update implementation metadata:
      - last_modified: 2025-10-18
      - line_end: 125 (was 120, code expanded)
   e. Save updated index

5. Index Updater → Completion:
   Duration: 2.3 seconds
   Status: SUCCESS

6. architect (next query) → Fresh Index:
   Automatically uses updated index
   Sees latest changes in search results
```

**Flow 3: User Requests Major Refactoring Analysis**

```
1. User → user_listener: "Analyze entire authentication system for refactoring"

2. user_listener → architect: Delegated analysis task

3. architect → Functional Code Search:
   search.query("authentication", filters={"complexity": "high"})

4. Functional Code Search → Code Index:
   Returns: All auth-related code, filtered by high complexity

5. architect → Analysis:
   Finds:
   - 3 high-complexity implementations (needs refactoring)
   - 15 total implementations across 8 files
   - 800 LOC total
   - Dependencies: pyjwt, bcrypt, redis

6. architect → Estimation:
   estimate = search.estimate_hours()
   # Returns: (12, 16) hours for full refactoring

7. architect → Code Explanation (for high-complexity zones):
   For each high-complexity implementation:
   - Explain current patterns
   - Identify issues
   - Suggest improvements

8. architect → Technical Spec Creation:
   Creates: SPEC-003-auth-refactoring.md
   Includes:
   - Current state: 3 high-complexity zones (detailed)
   - Proposed refactoring: Extract to AuthService, simplify flows
   - Estimated time: 12-16 hours (data-driven)
   - Phased rollout: Phase 1 (JWT), Phase 2 (Sessions), Phase 3 (OAuth)
   - Risks: Breaking existing integrations

9. architect → user_listener:
   "Comprehensive refactoring spec created"

10. user_listener → User:
    Presents spec with accurate scope and estimates
```

### 5.3 Agent Ownership

**Clear Responsibility Matrix**:

| Component | Owner | Responsibility | Access |
|-----------|-------|----------------|--------|
| **Code Index (data/code_index/index.json)** | code-searcher | Build, maintain, update | architect: READ, code-searcher: WRITE |
| **Functional Code Search Skill** | architect | Query execution, result ranking | architect: EXECUTE, others: None |
| **Code Explanation Skill** | architect | Generate summaries, analyze code | architect: EXECUTE, others: None |
| **Index Update Skill** | code-searcher | Rebuild, incremental update | code-searcher: EXECUTE, others: Trigger only |
| **Git Hooks** | code-searcher | Install, maintain hooks | code-searcher: WRITE |
| **Search Results** | architect | Consume, interpret, use in specs | architect: READ/ANALYZE |

**Why This Ownership?**

1. **code-searcher owns infrastructure**:
   - Expertise in code analysis and indexing
   - Responsible for index accuracy and performance
   - Maintains index update mechanisms
   - Does NOT create architectural specs (that's architect)

2. **architect owns consumption**:
   - Expertise in architectural design
   - Uses search results to create better specs
   - Interprets code explanations for design decisions
   - Does NOT maintain index infrastructure (that's code-searcher)

**Collaboration Pattern**:

```
code-searcher:
- "I maintain the index so it's always accurate and fast"
- "I provide the infrastructure for code discovery"
- "I don't create specs, but I enable better specs"

architect:
- "I use the index to find ALL relevant code"
- "I create comprehensive specs based on search results"
- "I estimate implementation time using scope data"
- "I don't maintain the index, but I rely on it"

Communication:
architect → code-searcher: "Index seems outdated for module X"
code-searcher → architect: "Running rebuild now, ETA 30 seconds"
architect → architect (self): "Waiting for fresh index before creating spec"
```

---

## 6. Implementation Plan

### 6.1 Phase 1: Code Index Infrastructure (code-searcher)

**Goal**: Build the foundational 3-level hierarchical index.

**Tasks**:
1. **Create Data Structure** (2 hours)
   - Define JSON schema for index
   - Create Pydantic models (Category, Component, Implementation)
   - Implement validation logic

2. **Build Parser** (4 hours)
   - AST-based Python code parser
   - Extract functions, classes, methods
   - Record line ranges, docstrings, dependencies

3. **Implement Clustering** (4 hours)
   - TF-IDF embeddings for code elements
   - K-means clustering for functional categories
   - Component grouping heuristics

4. **Create Full Rebuild Algorithm** (3 hours)
   - Discover Python files
   - Parse all files in parallel
   - Cluster into categories
   - Generate index JSON
   - Atomic write (temp file + rename)

5. **Testing** (2 hours)
   - Test on MonolithicCoffeeMakerAgent codebase
   - Verify accuracy of categorization
   - Validate line numbers

**Deliverable**: Working code index for current codebase
**Duration**: 15 hours
**Owner**: code-searcher

### 6.2 Phase 2: Search & Explanation Skills (architect)

**Goal**: Enable architect to query index and understand code.

**Tasks**:
1. **Functional Code Search Skill** (4 hours)
   - Query parser (keywords, filters)
   - Hierarchical search across 3 levels
   - Ranking algorithm
   - Result formatting (terminal + programmatic)
   - Scope estimation logic

2. **Code Explanation Skill** (3 hours)
   - Multi-level summary generation
   - Complexity analysis
   - Pattern detection
   - Issue identification
   - Improvement suggestions

3. **Integration with Spec Creation** (2 hours)
   - Integrate search into architect's workflow
   - Add search results to spec templates
   - Use estimates in planning

4. **Testing** (2 hours)
   - Test queries on real scenarios
   - Validate explanation accuracy
   - Verify estimates against actual implementation times

**Deliverable**: architect can search and explain code
**Duration**: 11 hours
**Owner**: architect

### 6.3 Phase 3: Auto-Update Mechanism (code-searcher)

**Goal**: Keep index current automatically.

**Tasks**:
1. **Incremental Update Algorithm** (3 hours)
   - Load existing index
   - Update changed files
   - Prune deleted implementations
   - Save updated index

2. **Git Hook Integration** (2 hours)
   - Post-commit hook
   - Post-merge hook
   - Hook installation script

3. **Decision Algorithm** (1 hour)
   - Incremental vs full rebuild logic
   - Performance optimization

4. **File Watcher (Optional)** (2 hours)
   - Real-time file monitoring
   - Debounced updates
   - Background processing

5. **Scheduled Rebuild** (1 hour)
   - Cron job setup
   - Nightly full rebuild

6. **Testing** (2 hours)
   - Test incremental updates
   - Test git hooks
   - Verify performance

**Deliverable**: Index updates automatically
**Duration**: 11 hours (9 hours without file watcher)
**Owner**: code-searcher

### 6.4 Effort Estimates

**Total Effort**: 37 hours (35 hours without optional file watcher)

**Breakdown by Agent**:
- code-searcher: 26 hours (infrastructure + maintenance)
- architect: 11 hours (consumption skills)

**Breakdown by Phase**:
- Phase 1 (Infrastructure): 15 hours
- Phase 2 (Skills): 11 hours
- Phase 3 (Auto-Update): 11 hours

**Timeline** (with 1 full-time developer):
- Week 1: Phase 1 (infrastructure)
- Week 2: Phase 2 (skills) + Phase 3 (auto-update)
- Week 3: Testing, refinement, documentation

**Timeline** (with code_developer working autonomously):
- code_developer can implement incrementally
- Each phase is independently valuable
- Can be implemented over 2-3 weeks

---

## 7. Usage Examples

### 7.1 Scenario: User asks "Where is payment processing?"

**Current State** (without these skills):
```
architect:
1. Uses grep to search for "payment"
2. Gets 50+ results across many files
3. Manually reads each file to understand
4. Misses some related code (different naming)
5. Creates incomplete spec
6. Estimate is rough guess: "maybe 4-8 hours?"
```

**Future State** (with these skills):
```
architect:
1. Uses Functional Code Search: search.query("payment processing")
2. Gets hierarchical results:
   - Category: Payment Processing (5 components, 12 implementations)
   - Category: Invoice Generation (2 components, 4 implementations)
   Total: 8 files, 650 LOC, complexity: HIGH

3. Uses Code Explanation for high-complexity zones:
   - stripe_gateway.py:45-120 → "Stripe integration with idempotency"
   - reconciliation.py:200-350 → "Daily payment reconciliation batch job"

4. Creates comprehensive spec with:
   - Affected files: 8 (complete list)
   - Estimated time: 8-12 hours (data-driven)
   - Integration points: Stripe API, Invoice PDF generation
   - Risks: Hard-coded API keys, no rate limiting

5. User approves spec → code_developer implements efficiently
```

**Improvement**:
- **Completeness**: 100% of payment code found (vs ~70% before)
- **Accuracy**: Estimate based on actual scope (vs rough guess)
- **Speed**: 5 minutes to analyze (vs 30+ minutes manual search)

### 7.2 Scenario: Architect estimates implementation time

**Current State**:
```
User: "How long to implement caching layer?"
architect: "Hmm, maybe 6-10 hours? Not sure without looking at the code."
```

**Future State**:
```
User: "How long to implement caching layer?"

architect:
1. search.query("cache caching")
2. Results:
   - 3 existing cache implementations found
   - Total: 450 LOC, complexity: MEDIUM
   - Dependencies: redis, functools, asyncio

3. estimate = search.estimate_hours()
   # Returns: (6, 8) hours based on:
   # - Base: 450 LOC / 100 LOC per hour = 4.5 hours
   # - Complexity factor: 1.5x (medium) = 6.75 hours
   # - Dependency penalty: +0.5 hours (redis integration)
   # - Total: 6-8 hours (with 25% margin)

4. architect: "Based on scope analysis, 6-8 hours:
   - 3 existing cache implementations to integrate with
   - Medium complexity (Redis + asyncio)
   - 450 LOC to write/modify
   - Integration with existing functools caching"

User: "Great, that's detailed and credible!"
```

**Improvement**:
- **Data-Driven**: Estimate based on actual code analysis
- **Transparent**: User understands how estimate was derived
- **Credible**: architect can justify the numbers

### 7.3 Scenario: Code Index becomes stale

**Trigger**: code_developer commits new payment module

**Flow**:
```
1. code_developer:
   git commit -m "feat: Add PayPal payment integration"
   # Commits: coffee_maker/payment/paypal_gateway.py

2. Git Post-Commit Hook:
   Detects: 1 new Python file
   Decision: Incremental update

3. Index Updater:
   a. Parses: coffee_maker/payment/paypal_gateway.py
   b. Identifies category: "Payment Processing"
   c. Creates new component: "PayPal Integration"
   d. Adds implementations:
      - paypal_gateway.py:20-80 (charge processing)
      - paypal_gateway.py:85-120 (webhook handling)
   e. Updates index.json
   Duration: 2.1 seconds

4. Next architect Query:
   architect: search.query("payment")
   # Now includes new PayPal component!
   Results:
   - Category: Payment Processing
     - Component: Stripe Integration (12 implementations)
     - Component: PayPal Integration (2 implementations) ← NEW!

5. architect creates spec with PayPal in scope:
   "Payment refactoring must account for both Stripe AND PayPal gateways"
```

**Benefit**: Index is always current, architect never misses new code.

---

## 8. Success Metrics

### 8.1 Quantitative Metrics

| Metric | Baseline (Before) | Target (After) | Measurement |
|--------|-------------------|----------------|-------------|
| **Spec Completeness** | ~70% of affected code found | >95% of affected code found | Manual verification after implementation |
| **Estimation Accuracy** | ±50% error (rough guesses) | ±25% error (data-driven) | Actual vs estimated hours |
| **Time to Analyze Code** | 30+ minutes (manual grep) | <5 minutes (automated search) | Time from query to results |
| **Index Freshness** | N/A (no index exists) | <5 minutes stale | Time between commit and index update |
| **Search Recall** | ~60% (miss obscure locations) | >90% (hierarchical indexing) | Found relevant code / Total relevant code |
| **architect Satisfaction** | Subjective frustration | Confident, efficient | User feedback |

### 8.2 Qualitative Metrics

**architect Capabilities Before**:
- ❌ Manual grep searching (slow, incomplete)
- ❌ Rough time estimates (often inaccurate)
- ❌ Missed code zones (incomplete specs)
- ❌ Inconsistent patterns (no easy way to find existing implementations)

**architect Capabilities After**:
- ✅ Automated hierarchical search (fast, comprehensive)
- ✅ Data-driven estimates (scope + complexity + dependencies)
- ✅ Complete code discovery (3-level index captures everything)
- ✅ Pattern reuse (find similar implementations easily)

**code_developer Benefits**:
- More detailed specs → less confusion during implementation
- Accurate estimates → better planning
- Clear integration points → faster development

**User Benefits**:
- Credible time estimates → better project planning
- Comprehensive specs → fewer surprises
- Higher quality implementations → less rework

### 8.3 Success Criteria

**Phase 1 Success** (Infrastructure):
- ✅ Index generated for MonolithicCoffeeMakerAgent codebase
- ✅ 3-level hierarchy with categories, components, implementations
- ✅ All Python files indexed with line numbers
- ✅ Complexity and dependencies captured
- ✅ Full rebuild completes in <60 seconds

**Phase 2 Success** (Skills):
- ✅ architect can query by functional area
- ✅ Search returns hierarchical results
- ✅ Scope estimation provides hour range
- ✅ Code explanation generates technical summaries
- ✅ Patterns and issues identified automatically

**Phase 3 Success** (Auto-Update):
- ✅ Git hooks trigger index updates
- ✅ Incremental updates complete in <5 seconds
- ✅ Index stays current (freshness <5 minutes)
- ✅ No manual intervention needed

**Overall Success**:
- ✅ architect creates 50% more detailed specs
- ✅ Time estimates within ±25% of actual
- ✅ architect can analyze entire auth system in <10 minutes (vs 1+ hour before)
- ✅ code_developer reports specs are "much clearer"

---

## 9. Risks & Mitigations

### 9.1 Risk: Index Accuracy

**Risk**: Clustering algorithm may misclassify code into wrong categories.

**Impact**: architect gets incomplete or incorrect search results.

**Probability**: MEDIUM (ML clustering is not perfect)

**Mitigation**:
1. **Manual Review**: Allow architect to override categorization
2. **Feedback Loop**: architect reports misclassifications → code-searcher adjusts
3. **Hybrid Approach**: Combine ML clustering with rule-based heuristics
4. **Incremental Improvement**: Index accuracy improves over time with feedback

**Fallback**: architect can still use manual grep as backup.

### 9.2 Risk: Performance Degradation

**Risk**: Index updates slow down git commits or become a bottleneck.

**Impact**: Developers frustrated by slow commits.

**Probability**: LOW (with proper optimization)

**Mitigation**:
1. **Async Updates**: Git hooks trigger background index update (non-blocking)
2. **Incremental Updates**: Only update changed files (2-5 seconds)
3. **Performance Monitoring**: Track update times, optimize if >5 seconds
4. **Opt-Out**: Allow disabling auto-update in development mode

**Fallback**: Manual index rebuild when convenient.

### 9.3 Risk: Index Becomes Stale

**Risk**: Git hooks fail or are not installed, index becomes outdated.

**Impact**: architect works with stale data, creates incorrect specs.

**Probability**: LOW (with scheduled rebuild)

**Mitigation**:
1. **Scheduled Rebuild**: Nightly full rebuild ensures freshness
2. **Freshness Indicator**: Index includes "generated_at" timestamp
3. **Warning System**: architect sees warning if index >24 hours old
4. **Manual Trigger**: architect can request rebuild anytime

**Fallback**: architect manually greps if index is stale.

### 9.4 Risk: Complexity Underestimation

**Risk**: Estimation algorithm underestimates implementation time.

**Impact**: Deadlines missed, user disappointed.

**Probability**: MEDIUM (estimation is inherently uncertain)

**Mitigation**:
1. **Range Estimates**: Provide min-max range (e.g., 6-8 hours, not "7 hours")
2. **Safety Margin**: Add 25% buffer to estimates
3. **Calibration**: Track actual vs estimated, adjust algorithm over time
4. **Human Override**: architect can adjust estimates based on intuition

**Fallback**: architect treats estimates as guidelines, not guarantees.

### 9.5 Risk: Index Size Growth

**Risk**: Index file becomes too large, slows down loading.

**Impact**: architect waits several seconds for search results.

**Probability**: LOW (for codebases <100K LOC)

**Mitigation**:
1. **Compression**: Use gzip to reduce index size by ~70%
2. **Lazy Loading**: Load categories on-demand, not all at once
3. **Pruning**: Remove deleted code from index
4. **Pagination**: Return search results in pages (e.g., 20 at a time)

**Fallback**: Split index into multiple files if size exceeds 10 MB.

---

## 10. Future Enhancements

### 10.1 Multi-Language Support

**Current**: Python only
**Future**: Support JavaScript, TypeScript, Go, etc.

**Implementation**:
- Abstract parser interface
- Language-specific parsers (e.g., Babel for JS, go/parser for Go)
- Unified index format across languages

### 10.2 Semantic Search with Embeddings

**Current**: Keyword-based search
**Future**: Semantic search using code embeddings

**Example**:
- Query: "find authentication logic"
- Semantic search finds "login handlers", "credential validators", "session managers"
- Even if "authentication" keyword not present

**Implementation**:
- Use CodeBERT or similar model for code embeddings
- Vector database (Pinecone, Weaviate) for similarity search
- Fallback to keyword search if embeddings unavailable

### 10.3 Dependency Graph Visualization

**Current**: Text-based dependency list
**Future**: Interactive dependency graph

**Example**:
- architect queries "payment processing"
- Sees visual graph: PaymentController → PaymentService → StripeGateway
- Can click nodes to explore implementations

**Implementation**:
- Generate GraphViz/Mermaid diagrams from index
- Interactive web UI for exploration

### 10.4 Code Change Impact Analysis

**Current**: architect manually identifies affected code
**Future**: Automated impact analysis

**Example**:
- architect plans to refactor StripeGateway
- System shows: "This will impact 12 implementations across 5 components"
- Highlights high-risk changes

**Implementation**:
- Dependency tracking in index
- Call graph analysis
- Impact score calculation

### 10.5 AI-Powered Categorization

**Current**: Rule-based + K-means clustering
**Future**: Fine-tuned LLM for categorization

**Example**:
- LLM reads code and docstrings
- Generates category/component names automatically
- Suggests better organization

**Implementation**:
- Fine-tune small LLM (e.g., CodeGen, StarCoder)
- Train on manually categorized code examples
- Use for automatic categorization

---

## 11. Appendix

### 11.1 Example Index (Full)

See **Section 1.5** for detailed example.

### 11.2 Code Snippets

**Loading Index**:
```python
from coffee_maker.code_index.loader import CodeIndexLoader

index = CodeIndexLoader.load()
print(f"Index version: {index.version}")
print(f"Generated at: {index.generated_at}")
print(f"Total categories: {len(index.categories)}")
```

**Searching Index**:
```python
from coffee_maker.code_index.search import FunctionalCodeSearch

search = FunctionalCodeSearch()
results = search.query("authentication login")

for category in results.categories:
    print(f"Category: {category.name}")
    for component in category.components:
        print(f"  Component: {component.name}")
        for impl in component.implementations:
            print(f"    {impl.file}:{impl.line_start}-{impl.line_end}")
```

**Explaining Code**:
```python
from coffee_maker.code_index.explainer import CodeExplainer

explainer = CodeExplainer()
explanation = explainer.explain("coffee_maker/auth/login.py:45:89", level="technical")

print(explanation.summary)
print(f"Complexity: {explanation.complexity}")
print(f"Dependencies: {', '.join(explanation.dependencies)}")
```

**Updating Index**:
```python
from coffee_maker.code_index.updater import IndexUpdater

updater = IndexUpdater()
result = updater.update(changed_files=["coffee_maker/payment/stripe_gateway.py"])

print(f"Status: {result.status}")
print(f"Duration: {result.duration_seconds}s")
print(f"Files processed: {result.files_processed}")
```

### 11.3 API Reference

**CodeIndexLoader**:
```python
class CodeIndexLoader:
    @staticmethod
    def load() -> CodeIndex:
        """Load code index from data/code_index/index.json."""

    @staticmethod
    def load_version(version: str) -> CodeIndex:
        """Load specific index version."""
```

**FunctionalCodeSearch**:
```python
class FunctionalCodeSearch:
    def query(self, query_string: str, filters: dict = None) -> SearchResults:
        """Execute functional search."""

    def search_category(self, category_id: str) -> Category:
        """Get specific category."""

    def search_component(self, component_id: str) -> Component:
        """Get specific component."""
```

**CodeExplainer**:
```python
class CodeExplainer:
    def explain(self, location: str, level: str = "technical") -> Explanation:
        """Generate code explanation.

        Args:
            location: "file:line_start:line_end" format
            level: "executive", "technical", or "implementation"
        """
```

**IndexUpdater**:
```python
class IndexUpdater:
    def rebuild(self) -> IndexUpdateResult:
        """Full index rebuild."""

    def update(self, changed_files: List[str]) -> IndexUpdateResult:
        """Incremental update."""
```

---

## 12. Conclusion

This specification defines a comprehensive code search infrastructure that transforms how architect analyzes codebases and creates technical specifications. By providing:

1. **3-Level Hierarchical Index**: Navigate from concepts → components → code
2. **Functional Search**: Find ALL code related to a feature
3. **Code Explanation**: Understand existing patterns and complexity
4. **Auto-Update**: Keep index fresh automatically

architect can create:
- **More Complete Specs**: 95%+ of affected code identified
- **Accurate Estimates**: Data-driven time ranges (±25% error)
- **Better Designs**: Reuse existing patterns, avoid pitfalls

The system is designed for:
- **Large Codebases**: 55K+ LOC navigable with 3 levels
- **Autonomous Agents**: Minimal manual intervention needed
- **Continuous Evolution**: Index updates automatically as code changes

**Next Steps**:
1. Review and approve this specification
2. Create ADR documenting decision to build this system
3. Assign implementation to code_developer
4. Begin Phase 1 (Infrastructure) implementation

This is a FOUNDATIONAL improvement that will benefit architect for all future work on this project and beyond.

---

**Status**: Draft → Awaiting Review
**Reviewers**: User (via user_listener)
**Implementation**: code_developer (after approval)
