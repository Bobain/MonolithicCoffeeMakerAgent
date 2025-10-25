# Skill: Proactive Refactoring Analysis

**Name**: `proactive-refactoring-analysis`
**Owner**: architect agent
**Purpose**: Proactively identify refactoring opportunities and present them to project_manager for ROADMAP insertion
**Priority**: HIGH - Reduces technical debt, saves implementation time

---

## Mission Statement

**architect doit utiliser ce skill de façon PROACTIVE** pour:
1. Identifier opportunités de refactoring AVANT qu'elles deviennent bloquantes
2. Préparer propositions SYNTHÉTIQUES pour project_manager
3. Gagner du temps sur les tâches d'implémentation futures
4. Maintenir qualité architecturale constante

**Fréquence**: Exécuter ce skill **au moins 1x par semaine** (automatiquement)

---

## When to Use This Skill

### Proactive Triggers (Automatic)

✅ **Weekly cron** (every Monday 9:00 AM):
- architect automatically runs refactoring analysis
- Generates report for project_manager
- project_manager reviews and adds to ROADMAP if needed

✅ **After major feature completion** (PRIORITY marked ✅ Complete):
- Review code added for feature
- Identify patterns that could be extracted
- Suggest refactoring before moving to next priority

✅ **Code complexity threshold exceeded**:
- Monitor file size (>500 LOC = warning)
- Monitor function complexity (cyclomatic complexity >10)
- Monitor code duplication (>20% duplicated blocks)

### Reactive Triggers (On Demand)

✅ **User request**: "Analyze refactoring opportunities"

✅ **project_manager request**: "What technical debt do we have?"

✅ **code_developer request**: "This code is messy, suggest refactoring"

---

## Refactoring Analysis Checklist

architect MUST check ALL of these areas:

### 1. Code Duplication 🔄

**What to Look For**:
- Identical or near-identical code blocks in multiple files
- Copy-pasted functions with minor variations
- Same patterns repeated >3 times

**How to Detect**:
```bash
# Find duplicated code blocks
grep -r "pattern_to_search" coffee_maker/ | wc -l

# If count >3: Candidate for extraction
```

**Refactoring Opportunities**:
- Extract common function
- Create base class or mixin
- Create utility module
- Use composition instead of duplication

**Example**:
```
FOUND: 15 instances of API key loading pattern
FILES:
- coffee_maker/ai_service.py
- coffee_maker/claude_provider.py
- coffee_maker/openai_provider.py
- ... (12 more)

REFACTORING: Extract to ConfigManager.get_api_key()
BENEFIT: Reduce 150 LOC to 10 LOC, single source of truth
EFFORT: 2-3 hours
ROI: HIGH (saves 4-5 hours in future API key changes)
```

---

### 2. File Size & Complexity 📏

**What to Look For**:
- Files >500 LOC (warning)
- Files >1000 LOC (critical)
- Functions >50 LOC (consider splitting)
- Cyclomatic complexity >10 (too complex)

**How to Detect**:
```bash
# Find large files
find coffee_maker/ -name "*.py" -exec wc -l {} + | sort -rn | head -20

# Files >500 LOC are candidates for splitting
```

**Refactoring Opportunities**:
- Split large files into modules
- Extract functions into separate files
- Break down complex functions
- Use composition (mixins, modules)

**Example**:
```
FOUND: coffee_maker/autonomous/daemon.py = 1806 LOC
ANALYSIS: Monolithic daemon class doing too much
REFACTORING: Split into mixins (SpecManagerMixin, ImplementationMixin, etc.)
BENEFIT: Reduce to ~200 LOC main file + 5 mixins (~300 LOC each)
EFFORT: 8-12 hours
ROI: MEDIUM-HIGH (easier to maintain, test, extend)
```

---

### 3. Naming & Clarity 📝

**What to Look For**:
- Vague names (`data`, `temp`, `utils`)
- Misleading names (function does more than name suggests)
- Inconsistent naming (camelCase vs snake_case)
- Magic numbers/strings (hardcoded values)

**How to Detect**:
```bash
# Find vague variable names
grep -r "data\|temp\|utils\|foo\|bar" coffee_maker/ --include="*.py"

# Find magic numbers
grep -r "[0-9]\{3,\}" coffee_maker/ --include="*.py"
```

**Refactoring Opportunities**:
- Rename variables/functions for clarity
- Extract constants (magic numbers → named constants)
- Add docstrings
- Improve comments

**Example**:
```
FOUND: 23 magic numbers in coffee_maker/autonomous/daemon.py
EXAMPLES:
- sleep(300)  # What is 300? Why 5 minutes?
- if len(items) > 10:  # Why 10?
- timeout=600  # Why 10 minutes?

REFACTORING: Extract to named constants
CONSTANTS:
- CHECK_INTERVAL_SECONDS = 300  # Poll interval for background work
- MAX_BATCH_SIZE = 10  # Process max 10 items per iteration
- DEFAULT_TIMEOUT = 600  # Default timeout for LLM calls

BENEFIT: Clarity, easier to tune, self-documenting
EFFORT: 1-2 hours
ROI: LOW-MEDIUM (clarity improvement, not functional change)
```

---

### 4. Architecture Patterns 🏗️

**What to Look For**:
- God classes (classes doing too much)
- Tight coupling (module A imports 10+ modules)
- Missing abstractions (should use interface/base class)
- Inconsistent patterns (mixing paradigms)

**How to Detect**:
```bash
# Find classes with many methods (>15 = god class)
grep -r "def " coffee_maker/ --include="*.py" | awk -F: '{print $1}' | uniq -c | sort -rn

# Find files with many imports (>10 = tight coupling)
grep -r "^import\|^from" coffee_maker/ --include="*.py" | awk -F: '{print $1}' | uniq -c | sort -rn
```

**Refactoring Opportunities**:
- Extract interfaces/protocols
- Use dependency injection
- Apply SOLID principles
- Introduce design patterns (Factory, Strategy, etc.)

**Example**:
```
FOUND: daemon.py has 45 methods (god class)
ANALYSIS: Handles spec creation, implementation, git ops, status tracking
REFACTORING: Extract to mixins
MIXINS:
- SpecManagerMixin (spec creation, validation)
- ImplementationMixin (code generation, testing)
- GitOpsMixin (git commit, push, branch management)
- StatusMixin (status tracking, metrics)

BENEFIT: Single Responsibility Principle, easier testing
EFFORT: 10-15 hours
ROI: HIGH (enables parallel work, easier to extend)
```

---

### 5. Technical Debt Indicators 💸

**What to Look For**:
- TODO comments (unfinished work)
- FIXME comments (known bugs)
- HACK comments (workarounds)
- Commented-out code (dead code)
- try/except pass (swallowing errors)

**How to Detect**:
```bash
# Find TODOs
grep -r "TODO\|FIXME\|HACK\|XXX" coffee_maker/ --include="*.py"

# Find commented code
grep -r "^#.*def \|^#.*class " coffee_maker/ --include="*.py"

# Find error swallowing
grep -r "except.*:.*pass" coffee_maker/ --include="*.py"
```

**Refactoring Opportunities**:
- Address TODOs (create ROADMAP priorities)
- Fix FIXMEs (bug fixes)
- Remove HACKs (proper solutions)
- Delete commented code (use git history)
- Add proper error handling

**Example**:
```
FOUND: 12 TODO comments in codebase
TOP 3 by priority:
1. TODO: Implement retry logic for LLM calls (daemon.py:234)
   PRIORITY: HIGH (affects reliability)
   EFFORT: 2-3 hours

2. TODO: Add caching for ROADMAP reads (roadmap_cli.py:156)
   PRIORITY: MEDIUM (performance optimization)
   EFFORT: 3-4 hours

3. TODO: Migrate to Pydantic for config validation (config/manager.py:89)
   PRIORITY: LOW (nice-to-have)
   EFFORT: 5-6 hours

REFACTORING: Create 3 ROADMAP priorities
BENEFIT: Address known technical debt systematically
```

---

### 6. Test Coverage 🧪

**What to Look For**:
- Files without tests
- Low coverage (<80%)
- Missing edge case tests
- No integration tests

**How to Detect**:
```bash
# Run pytest with coverage
pytest --cov=coffee_maker --cov-report=term-missing

# Identify uncovered lines
```

**Refactoring Opportunities**:
- Add unit tests for uncovered modules
- Add integration tests for workflows
- Add edge case tests (error handling)
- Extract testable functions

**Example**:
```
FOUND: coffee_maker/autonomous/orchestrator.py = 65% coverage
MISSING:
- Error handling paths (crash recovery)
- Edge cases (agent already running)
- Integration tests (multi-agent coordination)

REFACTORING: Add comprehensive tests
TESTS NEEDED:
- Unit: _handle_crashed_agents() error cases
- Unit: _launch_agent() with invalid config
- Integration: Launch all 6 agents, verify coordination
- Integration: Crash agent, verify restart

BENEFIT: Confidence in refactoring, catch regressions
EFFORT: 6-8 hours
ROI: HIGH (prevents bugs, enables safe refactoring)
```

---

### 7. Dependency Management 📦

**What to Look For**:
- Unused dependencies (installed but not imported)
- Outdated dependencies (security vulnerabilities)
- Heavy dependencies (can we use lighter alternative?)
- Circular dependencies (module A imports B imports A)

**How to Detect**:
```bash
# Find unused imports
autoflake --check --remove-all-unused-imports -r coffee_maker/

# Check for outdated dependencies
poetry show --outdated

# Detect circular dependencies
pydeps coffee_maker/ --max-bacon 2
```

**Refactoring Opportunities**:
- Remove unused dependencies
- Upgrade outdated dependencies
- Break circular dependencies
- Lazy import heavy dependencies

**Example**:
```
FOUND: 3 unused dependencies in pyproject.toml
UNUSED:
- requests (using httpx instead)
- beautifulsoup4 (no HTML parsing in codebase)
- pillow (no image processing)

REFACTORING: Remove unused dependencies
BENEFIT: Faster installs, smaller Docker images, fewer vulnerabilities
EFFORT: 30 minutes
ROI: MEDIUM (cleanup, reduces attack surface)
```

---

## Output Format (Synthetic Report for project_manager)

architect MUST generate a **SYNTHETIC report** (1-2 pages max) for project_manager:

```markdown
# Refactoring Analysis Report

**Date**: 2025-10-18
**Analyzed by**: architect (proactive-refactoring-analysis skill)
**Codebase**: MonolithicCoffeeMakerAgent
**LOC**: 15,234 lines Python

---

## Executive Summary

**Refactoring Opportunities Found**: 8
**Total Estimated Effort**: 32-40 hours
**Potential Time Savings**: 60-80 hours (in future implementation)
**ROI**: HIGH (saves 2x effort invested)

**Top 3 Priorities**:
1. **Extract ConfigManager** (HIGH ROI) - 2-3 hours, saves 15+ hours
2. **Split daemon.py into mixins** (MEDIUM-HIGH ROI) - 10-15 hours, saves 20+ hours
3. **Add orchestrator tests** (HIGH ROI) - 6-8 hours, prevents critical bugs

---

## Refactoring Opportunities (Sorted by ROI)

### 1. 🏆 Extract ConfigManager (HIGHEST ROI)

**Issue**: API key loading duplicated 15+ times across codebase

**Current State**:
- 150 LOC scattered across 15 files
- Inconsistent error handling
- No fallback logic

**Proposed Refactoring**:
- Extract to `coffee_maker/config/manager.py`
- Centralized API key getters with fallbacks
- Custom exceptions for missing keys

**Effort**: 2-3 hours
**Time Saved (Future)**: 15+ hours (any API key change touches 1 file, not 15)
**ROI**: 🟢 **VERY HIGH** (5x return)
**Priority for ROADMAP**: **HIGH**

**Suggested ROADMAP Entry**:
```
PRIORITY X: Extract ConfigManager for API Key Loading
Status: 📝 Planned
Estimated Effort: 2-3 hours
Owner: code_developer
Technical Spec: Will be created by architect

Description:
Extract duplicated API key loading logic (15 instances) into centralized
ConfigManager with fallback support and custom exceptions.

Acceptance Criteria:
- [ ] ConfigManager class created in coffee_maker/config/manager.py
- [ ] All 15 instances migrated to use ConfigManager
- [ ] Fallback logic added (env var → .env → config file)
- [ ] Custom exceptions (APIKeyMissingError)
- [ ] Unit tests (95%+ coverage)

Benefit: Reduce 150 LOC to 10 LOC, single source of truth, saves 15+ hours in future changes
```

---

### 2. 🥈 Split daemon.py into Mixins (HIGH ROI)

**Issue**: daemon.py is 1806 LOC god class doing too much

**Current State**:
- 45 methods in single class
- Spec creation + implementation + git + status all mixed
- Hard to test, hard to extend

**Proposed Refactoring**:
- Extract 5 mixins (SpecManagerMixin, ImplementationMixin, GitOpsMixin, StatusMixin, NotificationMixin)
- Daemon composes mixins
- Each mixin has single responsibility

**Effort**: 10-15 hours
**Time Saved (Future)**: 20+ hours (easier to add features, parallel work)
**ROI**: 🟢 **HIGH** (2x return)
**Priority for ROADMAP**: **MEDIUM-HIGH**

**Suggested ROADMAP Entry**:
```
PRIORITY Y: Refactor daemon.py - Extract Mixins
Status: 📝 Planned
Estimated Effort: 10-15 hours
Owner: code_developer
Technical Spec: Will be created by architect

Description:
Split monolithic daemon.py (1806 LOC, 45 methods) into composable mixins
following Single Responsibility Principle.

Acceptance Criteria:
- [ ] SpecManagerMixin created (spec creation, validation)
- [ ] ImplementationMixin created (code generation, testing)
- [ ] GitOpsMixin created (git commit, push, branch)
- [ ] StatusMixin created (status tracking, metrics)
- [ ] NotificationMixin created (user notifications)
- [ ] Daemon class uses composition (inherits all mixins)
- [ ] All existing tests still pass
- [ ] New tests for each mixin (80%+ coverage)

Benefit: Single Responsibility, easier testing, enables parallel feature development
```

---

### 3. 🥉 Add Orchestrator Integration Tests (HIGH ROI - Risk Reduction)

**Issue**: orchestrator.py has 65% test coverage, missing critical paths

**Current State**:
- No integration tests for multi-agent coordination
- No tests for crash recovery
- No tests for agent already running errors

**Proposed Refactoring**:
- Add comprehensive unit tests (error paths)
- Add integration tests (launch all agents, verify coordination)
- Add crash recovery tests (kill agent, verify restart)

**Effort**: 6-8 hours
**Time Saved (Future)**: Prevents critical bugs (hard to quantify, but HIGH value)
**ROI**: 🟢 **HIGH** (risk reduction)
**Priority for ROADMAP**: **HIGH**

**Suggested ROADMAP Entry**:
```
PRIORITY Z: Add Comprehensive Orchestrator Tests
Status: 📝 Planned
Estimated Effort: 6-8 hours
Owner: code_developer
Technical Spec: Will be created by architect

Description:
Add missing tests for orchestrator.py (currently 65% coverage) to prevent
critical bugs in multi-agent coordination and crash recovery.

Acceptance Criteria:
- [ ] Unit tests for _handle_crashed_agents() error cases
- [ ] Unit tests for _launch_agent() with invalid config
- [ ] Integration test: Launch all 6 agents, verify coordination
- [ ] Integration test: Crash agent, verify restart with backoff
- [ ] Integration test: Agent already running error
- [ ] Coverage increased from 65% to 90%+

Benefit: Confidence in refactoring, catch regressions early, prevent critical bugs in production
```

---

### 4-8. Other Opportunities (Lower Priority)

**4. Remove Unused Dependencies** (Effort: 30 min, ROI: MEDIUM)
**5. Add Missing Docstrings** (Effort: 3-4 hours, ROI: LOW-MEDIUM)
**6. Extract Magic Numbers to Constants** (Effort: 1-2 hours, ROI: LOW)
**7. Address TODO Comments** (Effort: 8-10 hours, ROI: MEDIUM)
**8. Break Circular Dependencies** (Effort: 5-6 hours, ROI: MEDIUM)

See Appendix for details.

---

## Recommended Action Plan

### Phase 1: Quick Wins (Week 1) - 3-4 hours
1. Extract ConfigManager (2-3 hours) ← Highest ROI
2. Remove unused dependencies (30 min)

**Benefit**: Immediate cleanup, saves 15+ hours in future

### Phase 2: Structural Improvements (Week 2-3) - 16-23 hours
3. Split daemon.py into mixins (10-15 hours)
4. Add orchestrator tests (6-8 hours)

**Benefit**: Better architecture, safer refactoring, enables parallel work

### Phase 3: Polish (Week 4) - 12-16 hours
5. Address TODO comments (8-10 hours)
6. Add missing docstrings (3-4 hours)
7. Extract magic numbers (1-2 hours)

**Benefit**: Code quality, maintainability

---

## Metrics & Impact

| Metric | Before Refactoring | After Refactoring | Improvement |
|--------|-------------------|-------------------|-------------|
| **Total LOC** | 15,234 | ~14,500 | -734 LOC (-5%) |
| **Duplicated LOC** | 450 (3%) | <100 (<1%) | -350 LOC |
| **Files >500 LOC** | 5 | 2 | -3 files |
| **Test Coverage** | 78% | 90%+ | +12% |
| **God Classes** | 3 | 0 | -3 classes |
| **Unused Dependencies** | 3 | 0 | -3 deps |
| **TODO Comments** | 12 | 0 | -12 todos |

**Time Investment**: 32-40 hours (total refactoring effort)
**Time Saved (Future)**: 60-80 hours (faster feature development)
**ROI**: 2x return on investment

---

## Next Steps

1. **project_manager**: Review this report
2. **project_manager**: Add top 3 priorities to ROADMAP (Priority X, Y, Z)
3. **architect**: Create technical specs for approved refactorings
4. **code_developer**: Implement refactorings in priority order
5. **architect**: Run this skill again in 1 month (track progress)

---

## Appendix: Detailed Analysis

[Longer technical details if needed, but keep main report 1-2 pages]
```

---

## Proactive Usage by architect

### Weekly Cron (Automatic)

```python
# coffee_maker/autonomous/agents/architect_agent.py

class ArchitectAgent(BaseAgent):
    def _do_background_work(self):
        """Background work includes proactive refactoring analysis."""

        # Check if it's time for weekly refactoring analysis
        if self._should_run_refactoring_analysis():
            logger.info("🔍 Running proactive refactoring analysis...")
            self._run_refactoring_skill()

    def _should_run_refactoring_analysis(self) -> bool:
        """Check if we should run refactoring analysis.

        Returns True if:
        - It's Monday AND
        - Last analysis was >7 days ago
        """
        today = datetime.now()

        # Check if Monday (0 = Monday)
        if today.weekday() != 0:
            return False

        # Check last analysis time
        last_run_file = Path("data/architect_status/last_refactoring_analysis.json")
        if not last_run_file.exists():
            return True  # Never run before

        last_run = json.loads(last_run_file.read_text())
        last_run_date = datetime.fromisoformat(last_run["timestamp"])

        # Run if >7 days since last analysis
        return (today - last_run_date).days >= 7

    def _run_refactoring_skill(self):
        """Run proactive-refactoring-analysis skill."""

        # Load skill
        skill_prompt = load_skill("proactive-refactoring-analysis")

        # Execute skill with LLM
        logger.info("Analyzing codebase for refactoring opportunities...")
        report = self.llm.invoke(skill_prompt)

        # Write report
        report_file = Path(f"docs/architecture/refactoring_analysis_{datetime.now().strftime('%Y%m%d')}.md")
        report_file.write_text(report)

        logger.info(f"✅ Refactoring analysis complete: {report_file}")

        # Send report to project_manager
        self._send_message("project_manager", {
            "type": "refactoring_analysis_report",
            "priority": "NORMAL",
            "content": {
                "report_file": str(report_file),
                "summary": self._extract_summary(report),
                "top_priorities": self._extract_top_priorities(report)
            }
        })

        # Update last run timestamp
        last_run_file = Path("data/architect_status/last_refactoring_analysis.json")
        last_run_file.write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "report_file": str(report_file)
        }))
```

### After Feature Completion (Automatic)

```python
class ArchitectAgent(BaseAgent):
    def _handle_message(self, message: Dict):
        """Handle inter-agent messages."""

        msg_type = message.get("type")

        if msg_type == "feature_completed":
            # code_developer notifies architect when feature complete
            logger.info("Feature completed, analyzing for refactoring opportunities...")
            self._analyze_feature_refactoring(message["content"])

    def _analyze_feature_refactoring(self, feature_info: Dict):
        """Analyze completed feature for refactoring opportunities.

        Args:
            feature_info: {
                "priority": "PRIORITY 10",
                "files_changed": ["file1.py", "file2.py"],
                "loc_added": 450
            }
        """

        # Run targeted refactoring analysis
        skill_prompt = load_skill("proactive-refactoring-analysis", {
            "SCOPE": "feature",
            "FILES": feature_info["files_changed"],
            "PRIORITY": feature_info["priority"]
        })

        analysis = self.llm.invoke(skill_prompt)

        # If refactoring opportunities found, send to project_manager
        if self._has_refactoring_opportunities(analysis):
            self._send_message("project_manager", {
                "type": "refactoring_suggestion",
                "priority": "NORMAL",
                "content": {
                    "feature": feature_info["priority"],
                    "suggestions": analysis
                }
            })
```

---

## Success Metrics

### Quantitative

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Refactoring Reports Generated** | 1 per week | Count reports in docs/architecture/ |
| **Opportunities Identified** | 5-10 per report | Count items in report |
| **Opportunities Implemented** | >50% | % added to ROADMAP and completed |
| **Time Saved** | 2x ROI | Track effort vs future savings |
| **Code Quality Improvement** | +10% coverage | Test coverage increase |

### Qualitative

- ✅ project_manager receives actionable refactoring suggestions
- ✅ Refactoring priorities added to ROADMAP
- ✅ Technical debt trends downward over time
- ✅ code_developer spends less time fighting with messy code

---

## Integration with ROADMAP

### project_manager's Workflow

1. **Receive Report**: architect sends refactoring analysis (weekly or on-demand)
2. **Review Report**: Read 1-2 page synthetic report (not 20 pages of details!)
3. **Prioritize**: Decide which refactorings to add to ROADMAP
4. **Add to ROADMAP**: Create PRIORITY entries for approved refactorings
5. **Track**: Monitor refactoring completion, measure time savings

**Example**:
```markdown
# ROADMAP Update

## New Refactoring Priorities (from architect analysis 2025-10-18)

### PRIORITY 11: Extract ConfigManager (HIGHEST ROI)
**Status**: 📝 Planned
**Estimated Effort**: 2-3 hours
**Time Savings**: 15+ hours (future)
**Owner**: code_developer

### PRIORITY 12: Split daemon.py into Mixins
**Status**: 📝 Planned
**Estimated Effort**: 10-15 hours
**Time Savings**: 20+ hours (future)
**Owner**: code_developer

### PRIORITY 13: Add Orchestrator Integration Tests
**Status**: 📝 Planned
**Estimated Effort**: 6-8 hours
**Benefit**: Prevent critical bugs
**Owner**: code_developer
```

---

## References

- [architecture-reuse-check skill](./architecture-reuse-check.md) - Checks existing components before proposing new ones
- [REUSABLE_COMPONENTS.md](../../docs/architecture/REUSABLE_COMPONENTS.md) - Inventory of existing components
- [US-021 Refactoring Summary](../../docs/roadmap/ROADMAP.md) - Example of successful refactoring

---

**Remember**: Proactive refactoring prevents technical debt from becoming blocking! 🧹

**architect's Responsibility**: Identify refactoring opportunities BEFORE they become problems!
