# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-09
**Current Branch**: `feature/rateLimits-fallbacksModels-specializedModels`
**Status**: Refactoring phase completed ✅
**New**: 2 new Streamlit projects added (Analytics Dashboard + Agent UI) ⚡

---

## 🎯 Global Vision

Transform **Coffee Maker Agent** into a complete LLM orchestration framework with:
- ✅ **Solid infrastructure** (refactoring completed)
- 📊 **Advanced analytics** (Langfuse → SQLite/PostgreSQL export)
- 📚 **Professional documentation** (enhanced pdoc)
- 🤖 **Intelligent agents** (5 innovative projects)

---

## 📋 Project Status

### ✅ Completed Projects

#### 1. **Core Architecture Refactoring**
**Status**: ✅ **COMPLETED** (Sprint 1 & 2)
**Completion Date**: 2025-10-08
**Results**:
- Simplified AutoPickerLLM (780 → 350 lines, -55%)
- Extracted ContextStrategy
- FallbackStrategy with 3 implementations (Sequential, Smart, Cost-optimized)
- Builder Pattern (LLMBuilder + SmartLLM)
- 72 tests, 100% passing
- 100% backward compatible
- Complete codebase migration

**Documentation**:
- `docs/refactoring_complete_summary.md`
- `docs/sprint1_refactoring_summary.md`
- `docs/sprint2_refactoring_summary.md`
- `docs/migration_to_refactored_autopicker.md`

---

## 🚀 Prioritized Roadmap

### 🔴 **PRIORITY 1: Final Refactoring** (optional but recommended)

**Estimated Duration**: 1 week
**Impact**: ⭐⭐⭐⭐
**Status**: 📝 Planned (optional)

Sprint 1 & 2 refactoring is **complete and functional**, but improvements are possible:

#### Phase 1.1: Additional Refactoring (optional)
- [ ] Extract additional ContextStrategy (if future truncation/summarization needed)
- [ ] Implement CostTrackingStrategy (if enforceable budgets needed)
- [ ] Implement MetricsStrategy (if Prometheus/Datadog needed)
- [ ] Implement TokenEstimatorStrategy (if improved precision needed)

**Reference**: `docs/refactoring_priorities_updated.md`

**Decision**: To be done **AFTER** priorities 2-5 (analytics, Streamlit apps, and documentation), as current code is **already clean and functional**.

---

### 🔴 **PRIORITY 2: Analytics & Observability** ⚡ RECOMMENDED FIRST

**Estimated Duration**: 2-3 weeks
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned

#### Project: Langfuse → SQLite/PostgreSQL Export

**Objectives**:
- Automatic export of Langfuse traces to local database
- Performance analytics (LLM, prompts, agents)
- Multi-process shared rate limiting via SQLite
- Optimized SQL queries for reporting

**Architecture**:
- Default database: **SQLite** (simple, zero config)
- Advanced option: PostgreSQL (for high volume)
- **9 tables**: generations, traces, events, rate_limit_counters, scheduled_requests, agent_task_results, prompt_variants, prompt_executions, export_metadata
- WAL mode for SQLite (multi-process safe)

**Deliverables**:
```
coffee_maker/langchain_observe/analytics/
├── exporter.py                # Export Langfuse → DB
├── db_schema.py               # SQLAlchemy schemas
├── performance_analyzer.py    # Performance analysis
├── config.py                  # Configuration
└── metrics/
    ├── llm_metrics.py         # LLM metrics
    ├── prompt_metrics.py      # Prompt metrics
    └── agent_metrics.py       # Agent metrics

scripts/
├── export_langfuse_data.py    # Manual export CLI
├── setup_metrics_db.py        # Initial DB setup
├── analyze_llm_performance.py # LLM performance analysis
└── benchmark_prompts.py       # A/B testing prompts
```

**Benefits**:
- ✅ Measure LLM ROI (cost vs quality)
- ✅ Optimize prompts with quantitative data
- ✅ Monitor agent performance
- ✅ Reliable multi-process rate limiting
- ✅ Local archiving without cloud dependency

**Reference**: `docs/langfuse_to_postgresql_export_plan.md`

**Timeline**:
- Week 1: DB setup + Core exporter (13-20h)
- Week 2: Analytics + Metrics (8-12h)
- Week 3: Tests + Documentation (5-8h)

---

### 🔴 **PRIORITY 3: Streamlit Analytics Dashboard** ⚡ NEW

**Estimated Duration**: 1-2 weeks
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned
**Dependency**: Requires PRIORITY 2 (Analytics & Observability) completed

#### Project: Streamlit Dashboard for LLM & Cost Analysis

**Objectives**:
- Interactive dashboard to analyze LLM usage
- Cost visualization by model, agent, and task
- Performance graphs and trends
- Custom report exports

**Key Features**:
- 📊 **Overview**: Global metrics (total costs, tokens, requests)
- 📈 **Trends**: Temporal graphs of usage and costs
- 🔍 **Model Analysis**: Comparison of GPT-4, Claude, Gemini, etc.
- 🤖 **Agent Analysis**: Performance and costs per agent
- 💰 **Budget tracking**: Alerts and overage predictions
- 📥 **Export**: PDF, CSV, custom reports

**Architecture**:
```
streamlit_apps/
├── analytics_dashboard/
│   ├── app.py                    # Main Streamlit app
│   ├── pages/
│   │   ├── 01_overview.py        # Overview
│   │   ├── 02_cost_analysis.py   # Detailed cost analysis
│   │   ├── 03_model_comparison.py # Model comparison
│   │   ├── 04_agent_performance.py # Agent performance
│   │   └── 05_exports.py         # Report exports
│   ├── components/
│   │   ├── charts.py             # Chart components
│   │   ├── metrics.py            # Metrics widgets
│   │   └── filters.py            # Temporal/agent filters
│   └── queries/
│       └── analytics_queries.py  # SQLite/PostgreSQL queries
```

**Deliverables**:
- [ ] Multi-page Streamlit dashboard
- [ ] Connection to analytics database (SQLite/PostgreSQL)
- [ ] Interactive visualizations (Plotly/Altair)
- [ ] Dynamic filters (dates, agents, models)
- [ ] Report exports (PDF, CSV)
- [ ] Configuration and authentication
- [ ] User documentation

**Benefits**:
- ✅ Immediate visibility into LLM costs
- ✅ Quick identification of expensive agents
- ✅ Optimization based on real data
- ✅ Demonstration of framework ROI
- ✅ Accessible interface (non-technical users)

**Timeline**:
- Week 1: Setup + Main pages + Charts (8-12h)
- Week 2: Filters + Export + Tests + Documentation (6-10h)
- **Total**: 14-22h

---

### 🔴 **PRIORITY 4: Streamlit Agent Interaction UI** ⚡ NEW

**Estimated Duration**: 1-2 weeks
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Planned
**Dependency**: None (can be done in parallel)

#### Project: Streamlit Interface for Agent Interaction

**Objectives**:
- Graphical interface to interact with Coffee Maker agents
- Interactive chat with streaming responses
- Dynamic agent configuration (models, strategies)
- Conversation history and export
- Demo and testing of agent capabilities

**Key Features**:
- 💬 **Chat interface**: Fluid conversation with agents
- 🔄 **Streaming**: Real-time response display
- ⚙️ **Configuration**: Choice of model, temperature, strategies
- 📝 **History**: Save and reload conversations
- 🎯 **Predefined agents**: Templates for different use cases
- 📊 **Live metrics**: Tokens, cost, latency per request
- 🎨 **Multi-agents**: Support for multi-agent conversations

**Architecture**:
```
streamlit_apps/
├── agent_interface/
│   ├── app.py                    # Main Streamlit app
│   ├── pages/
│   │   ├── 01_chat.py            # Chat interface
│   │   ├── 02_agent_config.py    # Agent configuration
│   │   ├── 03_history.py         # Conversation history
│   │   └── 04_playground.py      # Testing & experimentation
│   ├── components/
│   │   ├── chat_interface.py     # Chat component
│   │   ├── agent_selector.py     # Agent selection
│   │   ├── model_config.py       # Model configuration
│   │   └── metrics_display.py    # Metrics display
│   ├── agents/
│   │   ├── agent_manager.py      # Agent instance management
│   │   └── agent_templates.py    # Predefined templates
│   └── storage/
│       └── conversation_storage.py # Conversation save
```

**Deliverables**:
- [ ] Chat interface with streaming
- [ ] Dynamic agent configuration
- [ ] Support for multiple agents (code reviewer, architect, etc.)
- [ ] Persistent conversation history
- [ ] Real-time metrics (tokens, cost, latency)
- [ ] Conversation exports (Markdown, JSON)
- [ ] Predefined agent templates
- [ ] User documentation

**Benefits**:
- ✅ Facilitates agent usage (non-developers)
- ✅ Interactive demo of framework capabilities
- ✅ Fast testing of prompts and configurations
- ✅ Modern and intuitive user experience
- ✅ Accelerates framework adoption
- ✅ Collects user feedback

**Timeline**:
- Week 1: Chat interface + Streaming + Config (10-14h)
- Week 2: History + Export + Templates + Tests (8-12h)
- **Total**: 18-26h

---

### 🔴 **PRIORITY 5: Professional Documentation**

**Estimated Duration**: 1-2 weeks
**Impact**: ⭐⭐⭐⭐
**Status**: 📝 Planned

#### Project: pdoc Documentation Enhancement

**Objectives**:
- Complete and navigable API documentation
- Usage examples for each component
- Automatic documentation validation
- Automatic publication to GitHub Pages ✅ (already in place)

**Deliverables**:
- [ ] pdoc configuration (`.pdoc.yml`)
- [ ] Enriched `__init__.py` with complete docstrings
- [ ] Google Style docstrings for all public modules
- [ ] Usage examples in each class/function
- [ ] `__pdoc__` variables to hide/document attributes
- [ ] Validation script (`scripts/validate_docs.py`)

**Priority Modules**:
1. `auto_picker_llm_refactored.py` ✅ (already well documented, enrich)
2. `builder.py` ⚠️ (new, to be fully documented)
3. `strategies/fallback.py` ✅ (add concrete examples)
4. `llm.py`, `cost_calculator.py`, `scheduled_llm.py`

**Reference**: `docs/pdoc_improvement_plan.md`

**Timeline**:
- Phase 1: Configuration (1-2h)
- Phase 2: `__init__.py` files (2-3h)
- Phase 3: Priority modules (5-8h)
- Phase 4: Metadata (1-2h)
- Phase 5: Tests & validation (2-3h)
- **Total**: 11-18h

**Note**: GitHub Action already in place ✅, just need to enrich docstrings.

---

### 🟡 **PRIORITY 6: Innovative Projects** (choose based on interest)

**Estimated Duration**: 3-4 weeks **per project**
**Impact**: ⭐⭐⭐⭐⭐
**Status**: 📝 Complete documentation created
**Dependency**: Recommended after Streamlit apps (Priorities 3 & 4)

Choose **1 project** to implement first, based on interest and needs:

---

#### Option A: **Multi-Model Code Review Agent** ⭐ TOP RECOMMENDATION

**Pitch**: Agent that reviews code with **multiple LLMs simultaneously**, each with different expertise (bugs, architecture, performance, security).

**Use Cases**:
- Automated code review before merge
- Multi-perspective analysis of file/PR
- Detection of recurring bug patterns
- Performance improvement suggestions

**Deliverables**:
```
coffee_maker/code_reviewer/
├── reviewer.py                 # MultiModelCodeReviewer
├── perspectives/
│   ├── bug_hunter.py           # GPT-4 for bugs
│   ├── architect_critic.py     # Claude for architecture
│   ├── performance_analyst.py  # Gemini for performance
│   └── security_auditor.py     # Security agent
├── report_generator.py         # HTML report generation
└── git_integration.py          # Git hooks
```

**Business Impact**:
- ⚡ Code review time reduction (30-50%)
- 🐛 Early bug detection (-40% bugs in prod)
- 📈 Code quality improvement
- 💰 Direct measurable ROI

**Reference**: `docs/projects/01_multi_model_code_review_agent.md`

**Timeline**: 3-4 weeks

---

#### Option B: **Self-Improving Prompt Lab**

**Pitch**: Automatic prompt optimization system with A/B testing, evolutionary algorithms, and continuous learning.

**Use Cases**:
- A/B testing of prompt variants
- Automatic optimization via genetic algorithm
- Performance tracking for each prompt
- Continuous improvement without manual intervention

**Deliverables**:
```
coffee_maker/prompt_lab/
├── lab.py                      # PromptLab orchestrator
├── experiments/
│   ├── ab_tester.py            # A/B testing
│   ├── genetic_optimizer.py   # Genetic algorithm
│   └── experiment_runner.py   # Experiment execution
├── mutators/
│   └── prompt_mutator.py      # Prompt mutations
└── reporting/
    └── experiment_report.py   # Experiment reports
```

**Business Impact**:
- 📈 Response quality improvement (+15-30%)
- 💰 Cost reduction (shorter, more efficient prompts)
- 🤖 Automatic continuous improvement
- 📊 Quantitative data for decisions

**Reference**: `docs/projects/02_self_improving_prompt_lab.md`

**Timeline**: 3-4 weeks

---

#### Option C: **Agent Ensemble Orchestrator**

**Pitch**: Meta-agent that coordinates multiple specialized agents (architect, coder, tester, reviewer) with collaboration patterns (sequential, parallel, debate).

**Use Cases**:
- Development of complex features
- Automatic review pipelines
- Multi-perspective analysis
- Problem solving by consensus

**Deliverables**:
```
coffee_maker/agent_ensemble/
├── orchestrator.py             # Meta-agent
├── agents/
│   ├── architect_agent.py      # Design
│   ├── coder_agent.py          # Implementation
│   ├── tester_agent.py         # Tests
│   └── reviewer_agent.py       # Review
├── patterns/
│   ├── sequential.py           # Pipeline
│   ├── parallel.py             # Fan-out/fan-in
│   └── debate.py               # Consensus
└── coordination/
    ├── task_decomposer.py      # Decomposition
    └── result_synthesizer.py   # Synthesis
```

**Business Impact**:
- 🚀 Complex task resolution (+40% productivity)
- 🤝 Optimal multi-model collaboration
- 🎯 Better quality through consensus
- 📊 Collaboration metrics

**Reference**: `docs/projects/03_agent_ensemble_orchestrator.md`

**Timeline**: 3-4 weeks

---

#### Option D: **Cost-Aware Smart Router**

**Pitch**: Intelligent router that dynamically chooses the best model for each request based on budget, latency, and quality constraints.

**Use Cases**:
- Automatic cost/quality optimization
- Real-time budget management
- Load balancing between providers
- Task pattern learning

**Deliverables**:
```
coffee_maker/smart_router/
├── router.py                   # SmartRouter
├── prediction/
│   ├── complexity_predictor.py # ML complexity prediction
│   └── cost_predictor.py       # Cost prediction
├── optimization/
│   ├── optimizer.py            # Optimal selection
│   └── budget_manager.py       # Budget management
└── learning/
    ├── pattern_learner.py      # Pattern learning
    └── model_ranker.py         # Model ranking
```

**Business Impact**:
- 💰 Cost reduction (-30-50%)
- ⚡ Latency/quality optimization
- 📊 Real-time budget enforcement
- 🎯 Direct measurable ROI

**Reference**: `docs/projects/04_cost_aware_smart_router.md`

**Timeline**: 3-4 weeks

---

#### Option E: **LLM Performance Profiler**

**Pitch**: Automated profiling tool that precisely measures LLM performance across different dimensions and generates detailed comparative reports.

**Use Cases**:
- Automated and reproducible benchmarking
- Model comparison (cost, latency, quality)
- Stress testing and context window testing
- Interactive HTML report generation

**Deliverables**:
```
coffee_maker/llm_profiler/
├── profiler.py                 # LLMProfiler
├── benchmarks/
│   ├── code_gen_benchmark.py   # Code generation
│   ├── summarization_benchmark.py
│   └── translation_benchmark.py
├── metrics/
│   ├── latency_meter.py        # Latency measurement
│   ├── quality_evaluator.py   # Quality evaluation
│   └── cost_calculator.py      # Cost calculation
└── reporting/
    ├── html_reporter.py        # HTML reports
    └── comparison_generator.py # Comparisons
```

**Business Impact**:
- 📊 Data-driven decisions
- 💰 Cost/quality optimization
- ⚡ Identification of fastest models
- 🎯 Reproducible benchmarks

**Reference**: `docs/projects/05_llm_performance_profiler.md`

**Timeline**: 3-4 weeks

---

## 📅 Recommended Timeline

### **Month 1: Solid Foundations**

#### Week 1-3: Analytics & Observability 🔴 PRIORITY
- SQLite database setup + Langfuse export
- Performance analytics
- Multi-process rate limiting
- **Deliverable**: Operational analytics system

---

### **Month 2: Streamlit User Interfaces** ⚡ NEW

#### Week 1-2: Analytics Dashboard 🔴 PRIORITY
- Streamlit dashboard for LLM & cost visualization
- Connection to analytics database
- Interactive charts (Plotly/Altair)
- Report export (PDF, CSV)
- **Deliverable**: Operational analytics dashboard

#### Week 3-4: Agent Interaction UI 🔴 PRIORITY
- Chat interface with agents
- Real-time response streaming
- Dynamic agent configuration
- Conversation history and export
- **Deliverable**: Web interface to interact with agents

---

### **Month 3: Documentation & First Innovative Project**

#### Week 1: Documentation 🔴 PRIORITY
- pdoc enhancement
- Docstring validation
- **Deliverable**: Professional API documentation

#### Week 2-4: First Innovative Project (optional)

Choose **1 project** among the 5 options based on business priority:

**Recommended option**: **Multi-Model Code Review Agent** ⭐

- Core reviewer + Perspectives
- Report generation + Git integration
- Tests + Documentation

---

### **Month 4+: Expansion (based on needs)**

Possible choices:
- Implement a 2nd innovative project (Agent Ensemble, Prompt Lab, etc.)
- Improve Streamlit apps with user feedback
- Additional refactoring (ContextStrategy, MetricsStrategy)
- Advanced features based on feedback

---

## 🌳 Git Strategy and Versioning

**Objective**: Maintain a clean and traceable Git history throughout the roadmap.

### 📋 Branch Structure

```
main (main branch, always stable)
│
├── feature/analytics-export-langfuse        (Priority 2)
│   ├── feat/db-schema                       (subtask)
│   ├── feat/exporter-core                   (subtask)
│   └── feat/analytics-queries               (subtask)
│
├── feature/streamlit-analytics-dashboard    (Priority 3)
│   ├── feat/dashboard-overview-page         (subtask)
│   ├── feat/cost-analysis-page             (subtask)
│   └── feat/charts-components              (subtask)
│
├── feature/streamlit-agent-ui              (Priority 4)
│   ├── feat/chat-interface                 (subtask)
│   ├── feat/agent-config                   (subtask)
│   └── feat/conversation-history           (subtask)
│
└── feature/documentation-pdoc              (Priority 5)
```

### 🏷️ Semantic Versioning Convention

Follow [Semantic Versioning 2.0.0](https://semver.org/):

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR** (v1.0.0 → v2.0.0): Breaking changes incompatible with existing API
- **MINOR** (v1.0.0 → v1.1.0): New backward-compatible features
- **PATCH** (v1.0.0 → v1.0.1): Backward-compatible bug fixes

**Recommended tags for this roadmap**:

```bash
# Current state (refactoring completed)
v0.9.0  # Pre-release with complete refactoring

# After Priority 2: Analytics
v1.0.0  # First major release with analytics

# After Priority 3: Streamlit Analytics Dashboard
v1.1.0  # Minor release - new feature

# After Priority 4: Streamlit Agent UI
v1.2.0  # Minor release - new feature

# After Priority 5: Documentation
v1.2.1  # Patch release - documentation improvement

# After Priority 6: First innovative project
v1.3.0  # Minor release - major new feature
```

### 📝 Commit Message Convention

**Conventional Commits Format**:
```
<type>(<scope>): <short description>

[optional message body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Refactoring (no functional change)
- `docs`: Documentation only
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks (build, CI, etc.)
- `perf`: Performance improvement
- `style`: Formatting (no code change)

**Scopes** (examples):
- `analytics`, `exporter`, `dashboard`, `agent-ui`, `llm`, `fallback`, `tests`, etc.

**Examples**:
```bash
feat(analytics): implement SQLite exporter for Langfuse traces
fix(dashboard): correct cost calculation for multi-model queries
refactor(llm): simplify AutoPickerLLM initialization logic
docs(analytics): add usage examples to exporter module
test(dashboard): add integration tests for chart components
chore(ci): update GitHub Actions workflow for pdoc
```

### 🔄 Git Workflow per Project

#### Phase 1: Project Start
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/project-name

# First commit (initial structure)
git commit -m "chore(project): initialize [project name] structure"
```

#### Phase 2: Iterative Development
```bash
# Regular commits (at least daily)
# 1 commit = 1 feature or 1 coherent fix

git add [files related to a feature]
git commit -m "feat(scope): feature description"

# Regular push for backup
git push origin feature/project-name
```

#### Phase 3: Continuous Improvement (after each project)
```bash
# Separate refactoring commits
git commit -m "refactor(scope): simplify complex function X"
git commit -m "docs(scope): add docstrings to module Y"
git commit -m "test(scope): improve coverage to 85%"
git commit -m "chore(scope): remove dead code and unused imports"
```

#### Phase 4: Finalization and Merge
```bash
# Ensure all tests pass
pytest

# Merge into main
git checkout main
git pull origin main
git merge feature/project-name

# Create version tag
git tag -a v1.x.0 -m "Release: [Project name] completed"

# Push main and tags
git push origin main --tags

# Optional: delete feature branch (if merged)
git branch -d feature/project-name
git push origin --delete feature/project-name
```

### 📊 CHANGELOG.md

Maintain an up-to-date `CHANGELOG.md` file at project root:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- [Work in progress items]

## [1.2.0] - 2025-XX-XX

### Added
- Streamlit Agent Interaction UI with chat interface
- Real-time streaming support for agent responses
- Conversation history and export functionality

### Changed
- Improved analytics dashboard performance
- Updated documentation with new examples

### Fixed
- Fixed rate limiting issue in multi-process scenarios

## [1.1.0] - 2025-XX-XX

### Added
- Streamlit Analytics Dashboard for LLM cost visualization
- Interactive charts for model comparison
- PDF/CSV export functionality

## [1.0.0] - 2025-XX-XX

### Added
- Analytics & Observability: Langfuse to SQLite/PostgreSQL export
- Rate limiting shared across multiple processes
- Performance analytics for LLMs, prompts, and agents

### Changed
- Refactored AutoPickerLLM (780 → 350 lines, -55%)
- Extracted FallbackStrategy with 3 implementations
- Implemented Builder Pattern (LLMBuilder + SmartLLM)

## [0.9.0] - 2025-10-08

### Changed
- Complete refactoring of core architecture (Sprint 1 & 2)
- 100% backward compatible migration
```

### 🎯 Git Best Practices

1. **Atomic commits**: 1 commit = 1 logical change
2. **Descriptive messages**: Explain the "why", not the "what"
3. **Daily push**: Backup and visibility on progress
4. **Short branches**: Merge regularly (< 1 week of work)
5. **Tags on milestones**: Facilitates rollback and tracking
6. **Up-to-date CHANGELOG**: Document changes for users
7. **Review before merge**: Verify tests pass and code is clean

### 🚨 What to Avoid

- ❌ Too large commits (> 500 lines modified)
- ❌ Vague messages ("fix bug", "update code")
- ❌ Direct commits on main (always use a branch)
- ❌ Forgetting to push (risk of work loss)
- ❌ Merging untested code
- ❌ Keeping feature branches open too long

---

## 🔄 Continuous Improvement Practice (Between Each Project)

**Principle**: After each completed project, take time to improve existing code before starting the next one.

### 📋 Continuous Improvement Checklist

To do **systematically** between each project:

#### 1. **Refactoring Analysis** (2-4h)
- [ ] Identify refactoring opportunities in recently written code
- [ ] Look for code duplications (DRY violations)
- [ ] Detect functions/classes that are too long or complex
- [ ] Spot circular dependencies or tight couplings
- [ ] Verify consistency of patterns used

**Tools**:
```bash
# Complexity analysis
radon cc coffee_maker/ -a -nb

# Duplication detection
pylint coffee_maker/ --disable=all --enable=duplicate-code

# Static analysis
mypy coffee_maker/
```

#### 2. **Complexity Reduction** (1-3h)
- [ ] Extract long methods into smaller functions
- [ ] Simplify complex conditions (early returns, guard clauses)
- [ ] Reduce cyclomatic complexity (< 10 per function)
- [ ] Replace magic numbers with named constants
- [ ] Improve readability (variable names, structure)

**Quality Criteria**:
- Cyclomatic complexity < 10
- Function length < 50 lines
- Class length < 300 lines
- Indentation depth < 4 levels

#### 3. **Documentation** (1-2h)
- [ ] Add/complete missing docstrings
- [ ] Enrich usage examples
- [ ] Update README if necessary
- [ ] Document architecture decisions (ADR if relevant)
- [ ] Verify type hints are present and correct

**Validation Script**:
```bash
python scripts/validate_docs.py  # Create if doesn't exist
```

#### 4. **Tests and Coverage** (1-2h)
- [ ] Verify test coverage (target: > 80%)
- [ ] Add tests for missing edge cases
- [ ] Refactor duplicated tests
- [ ] Verify tests are readable and maintainable

**Commands**:
```bash
pytest --cov=coffee_maker --cov-report=html
coverage report --fail-under=80
```

#### 5. **Performance and Optimization** (1-2h - if relevant)
- [ ] Identify potential bottlenecks
- [ ] Check for unnecessary imports
- [ ] Optimize DB queries if applicable
- [ ] Check memory usage for high volumes

#### 6. **Cleanup** (30min-1h)
- [ ] Remove dead code (unused functions/classes)
- [ ] Clean unused imports
- [ ] Remove obsolete comments
- [ ] Format code (black, isort)
- [ ] Check TODOs and handle or document them

**Commands**:
```bash
# Automatic cleanup
black coffee_maker/
isort coffee_maker/
autoflake --remove-all-unused-imports --in-place --recursive coffee_maker/
```

#### 7. **Git Management and Versioning** (30min-1h)
- [ ] Create atomic and well-named commits
- [ ] Use feature branches for each subtask
- [ ] Make regular commits (at least daily)
- [ ] Write descriptive commit messages
- [ ] Create tags for important milestones

**Git Best Practices**:
```bash
# Branch naming convention
feature/analytics-exporter
feature/streamlit-dashboard
fix/rate-limiting-bug
refactor/simplify-fallback-strategy

# Commit message convention
# Format: <type>(<scope>): <description>
# Types: feat, fix, refactor, docs, test, chore, perf

git commit -m "feat(analytics): add Langfuse to SQLite exporter"
git commit -m "refactor(llm): reduce complexity of AutoPickerLLM"
git commit -m "docs(analytics): add usage examples to exporter"
git commit -m "test(analytics): add integration tests for exporter"

# Tags for milestones
git tag -a v1.0.0-analytics -m "Analytics & Observability completed"
git tag -a v1.1.0-streamlit-dashboard -m "Streamlit Analytics Dashboard completed"
```

**Recommended Git Workflow**:
1. **Project start**: Create feature branch
   ```bash
   git checkout -b feature/project-name
   ```

2. **During development**: Regular commits
   ```bash
   # Atomic commits per feature
   git add coffee_maker/analytics/exporter.py
   git commit -m "feat(analytics): implement basic exporter structure"

   git add tests/test_exporter.py
   git commit -m "test(analytics): add unit tests for exporter"
   ```

3. **End of subtask**: Push and potential PR (if team work)
   ```bash
   git push origin feature/project-name
   ```

4. **Continuous improvement**: Separate refactoring commits
   ```bash
   git commit -m "refactor(analytics): simplify exporter error handling"
   git commit -m "docs(analytics): add docstrings to exporter methods"
   git commit -m "test(analytics): improve test coverage to 85%"
   ```

5. **Project end**: Merge into main and tag
   ```bash
   git checkout main
   git merge feature/project-name
   git tag -a v1.x.0-project-name -m "Project completed description"
   git push origin main --tags
   ```

**Git Checklist Before Finalizing a Project**:
- [ ] All modified files are committed
- [ ] Commit messages are clear and descriptive
- [ ] Commits are atomic (1 commit = 1 feature/fix)
- [ ] Feature branch is merged into main
- [ ] Version tag is created
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] Tests pass on main branch after merge

### 📊 Improvement Documentation

Create tracking document in `docs/improvements/`:
- `improvement_after_analytics.md`
- `improvement_after_streamlit_dashboard.md`
- `improvement_after_agent_ui.md`
- etc.

**Document Template**:
```markdown
# Improvements after [Project Name]

**Date**: YYYY-MM-DD
**Time spent**: Xh

## Refactorings performed
- [List of refactorings with affected files]

## Complexity reduced
- Before: [metrics]
- After: [metrics]

## Documentation added
- [List of documented modules]

## Tests added
- Coverage before: X%
- Coverage after: Y%

## Code removed
- X lines of dead code removed
- Y unused imports cleaned

## Impact
- Maintenance: [maintainability improvement]
- Performance: [performance gains if applicable]
- Readability: [readability improvement]
```

### ⏱️ Estimated Time per Continuous Improvement Session

| Task | Simple Project | Medium Project | Complex Project |
|------|----------------|----------------|-----------------|
| 1. Refactoring Analysis | 2h | 2-3h | 3-4h |
| 2. Complexity Reduction | 1h | 1-2h | 2-3h |
| 3. Documentation | 1h | 1-2h | 1-2h |
| 4. Tests and Coverage | 1h | 1-2h | 2h |
| 5. Performance | 0-1h | 1h | 1-2h |
| 6. Cleanup | 30min | 30min-1h | 1h |
| 7. Git Management | 30min | 30min-1h | 1h |
| **TOTAL** | **6-7h** | **7-10h** | **11-15h** |

**Examples**:
- **Streamlit apps**: ~6-7h continuous improvement
- **Analytics**: ~7-10h continuous improvement
- **Innovative projects**: ~11-15h continuous improvement

### 🎯 Benefits

- ✅ **Controlled technical debt**: Avoids debt accumulation
- ✅ **Consistent quality**: Maintains high quality level
- ✅ **Maintainability**: Code easier to modify and extend
- ✅ **Learning**: Fast feedback on patterns to improve
- ✅ **Momentum**: Natural transition between projects

### 🚨 Important

This practice is **non-negotiable** and is an integral part of each project. Continuous improvement time must be **included** in each project estimate.

**New estimate per project**:
- Initial project: X weeks
- Continuous improvement: +0.5-1 week
- **Realistic total**: X + 0.5-1 weeks

---

## 🎯 Success Metrics

### Analytics & Observability
- ✅ Automatic Langfuse → SQLite export functional
- ✅ Usable SQL analysis queries
- ✅ Reliable multi-process rate limiting
- ✅ 0 duplicates in exports

### Streamlit Analytics Dashboard
- ✅ Dashboard accessible via browser
- ✅ Functional cost and trend charts
- ✅ Operational dynamic filters (dates, agents, models)
- ✅ PDF/CSV report export
- ✅ Loading time < 3 seconds

### Streamlit Agent Interaction UI
- ✅ Responsive chat interface with streaming
- ✅ Functional agent configuration
- ✅ Persistent conversation history
- ✅ Support for multiple simultaneous agents
- ✅ Real-time metrics displayed

### Documentation
- ✅ 100% of public functions documented
- ✅ Automatic validation (CI/CD)
- ✅ Usage examples for each module
- ✅ GitHub Pages updated

### Innovative Projects (example: Code Review Agent)
- ✅ Multi-model review functional
- ✅ HTML reports generated
- ✅ Git hooks integration
- ✅ Review time reduction measured (-30%)

---

## 🚫 Anti-Priorities (to avoid for now)

- ❌ **Complete rewrite** - Sprint 1 & 2 refactoring is sufficient
- ❌ **Premature optimizations** - Focus on business features
- ❌ **Support for all LLM providers** - Stick to current 3 (OpenAI, Gemini, Anthropic)
- ❌ **Complex UI/Frontend** - Streamlit is sufficient, no need for React/Vue.js for now

---

## 🔄 Flexibility and Adaptation

This roadmap is **flexible** and can be adjusted based on:
- User feedback
- Business priorities
- New technological opportunities
- Time/resource constraints

**Recommended review**: Every month, re-evaluate priorities.

---

## 📚 Associated Documentation

### Completed Projects
- `docs/refactoring_complete_summary.md` - Complete refactoring summary
- `docs/sprint1_refactoring_summary.md` - Sprint 1 detailed
- `docs/sprint2_refactoring_summary.md` - Sprint 2 detailed
- `docs/migration_to_refactored_autopicker.md` - Migration guide

### Planned Projects
- `docs/langfuse_to_postgresql_export_plan.md` - Analytics & Export
- `docs/pdoc_improvement_plan.md` - Documentation
- `docs/projects/01_multi_model_code_review_agent.md` - Code Review Agent
- `docs/projects/02_self_improving_prompt_lab.md` - Prompt Lab
- `docs/projects/03_agent_ensemble_orchestrator.md` - Agent Ensemble
- `docs/projects/04_cost_aware_smart_router.md` - Smart Router
- `docs/projects/05_llm_performance_profiler.md` - Performance Profiler

### Architecture & Planning
- `docs/refactoring_priorities_updated.md` - Additional refactoring (optional)
- `docs/feature_ideas_analysis.md` - Analysis of 5 innovative projects

---

## ✅ Recommended Decision

**To start immediately**:

1. ✅ **Week 1-3** (Month 1): Implement **Analytics & Langfuse Export** 🔴
   - Immediate business impact (ROI measurement)
   - Foundation for all other projects
   - Critical multi-process rate limiting

2. ✅ **Week 1-2** (Month 2): **Streamlit Analytics Dashboard** 🔴 ⚡ NEW
   - Immediate visualization of LLM costs
   - Accessible interface for non-technical users
   - Demonstration of framework ROI
   - **Depends on**: Analytics & Langfuse Export completed

3. ✅ **Week 3-4** (Month 2): **Streamlit Agent Interaction UI** 🔴 ⚡ NEW
   - Facilitates agent usage
   - Fast testing and interactive demo
   - Accelerates framework adoption
   - **Can be done in parallel** with Analytics Dashboard if needed

4. ✅ **Week 1** (Month 3): Improve **pdoc Documentation** 🔴
   - Quick win (11-18h)
   - Improves developer experience
   - GitHub Action already in place

5. ⭐ **Week 2-4** (Month 3) - **Optional**: First **Innovative Project**
   - Recommendation: **Multi-Model Code Review Agent**
   - Direct and measurable ROI
   - Concrete and useful use case

**Then**: Re-evaluate based on feedback and business needs.

---

**Ready to start? Which project do you want to begin with?** 🚀
