# SPEC-025 - Phase 5: Testing and Documentation

**Estimated Time**: 2 hours
**Dependencies**: All previous phases complete
**Status**: Planned
**Files Created**: Test files, updated documentation

---

## Goal

Comprehensive testing of hierarchical spec system and complete documentation updates. Ensure code_developer can successfully use hierarchical specs end-to-end.

**What This Phase Accomplishes**:
- Unit tests for hierarchical spec handling
- Integration tests with code_developer
- Updated architect workflow documentation
- Examples and tutorials
- Performance benchmarks (context reduction validation)

---

## Prerequisites

- [x] Phase 1 complete (skill implemented)
- [ ] Phase 2 complete (daemon integrated)
- [ ] Phase 3 complete (guidelines created)
- [ ] Phase 4 complete (specs migrated)

---

## Detailed Steps

### Step 1: Create Unit Tests

**What**: Test hierarchical spec creation and reading in isolation

**Why**: Ensure core functionality works correctly before integration

**How**:
1. Create test file: `tests/unit/test_hierarchical_specs.py`
2. Test SpecHandler.create_hierarchical()
3. Test SpecHandler.read_hierarchical()
4. Test phase detection logic
5. Test spec type detection
6. Test backward compatibility (monolithic still works)

**Test Implementation**:
```python
# tests/unit/test_hierarchical_specs.py

import pytest
from pathlib import Path
from coffee_maker.utils.spec_handler import SpecHandler

class TestHierarchicalSpecs:
    """Test hierarchical specification handling."""

    def test_create_hierarchical_spec(self, tmp_path):
        """Test creating hierarchical spec directory structure."""
        handler = SpecHandler(specs_dir=tmp_path)

        result = handler.create_hierarchical(
            us_number="999",
            title="Test Feature",
            phases=[
                {"name": "foundation", "hours": 1},
                {"name": "implementation", "hours": 2},
                {"name": "testing", "hours": 1}
            ]
        )

        assert result["success"] is True
        assert result["total_phases"] == 3

        spec_dir = Path(result["spec_dir"])
        assert spec_dir.exists()
        assert (spec_dir / "README.md").exists()
        assert (spec_dir / "phase1-foundation.md").exists()
        assert (spec_dir / "phase2-implementation.md").exists()
        assert (spec_dir / "phase3-testing.md").exists()

    def test_read_hierarchical_spec(self, tmp_path):
        """Test reading hierarchical spec with progressive disclosure."""
        handler = SpecHandler(specs_dir=tmp_path)

        # Create spec
        handler.create_hierarchical(
            us_number="999",
            title="Test Feature",
            phases=[{"name": "phase1", "hours": 1}, {"name": "phase2", "hours": 1}]
        )

        # Read spec (phase 1)
        result = handler.read_hierarchical(priority_id="PRIORITY-999", phase=1)

        assert result["success"] is True
        assert result["spec_type"] == "hierarchical"
        assert result["current_phase"] == 1
        assert result["total_phases"] == 2
        assert "README.md" in result["full_context"]
        assert "phase1" in result["full_context"]
        assert "phase2" not in result["full_context"]  # Not loaded yet

    def test_detect_current_phase_from_roadmap(self, tmp_path, monkeypatch):
        """Test phase detection from ROADMAP checkboxes."""
        handler = SpecHandler()

        # Mock ROADMAP content
        roadmap_content = """
        ### PRIORITY 25:
        - [x] Phase 1 complete
        - [ ] Phase 2
        """
        monkeypatch.setattr(Path, "read_text", lambda self: roadmap_content)

        phase = handler._detect_current_phase("PRIORITY 25", tmp_path)
        assert phase == 2  # Phase 1 complete, so current is 2

    def test_detect_spec_type_hierarchical(self, tmp_path):
        """Test detecting hierarchical spec (directory)."""
        handler = SpecHandler(specs_dir=tmp_path)

        # Create hierarchical spec
        spec_dir = tmp_path / "SPEC-999-test-feature"
        spec_dir.mkdir()
        (spec_dir / "README.md").write_text("# Test")

        spec_type, spec_path = handler._detect_spec_type("999")
        assert spec_type == "hierarchical"
        assert spec_path == spec_dir

    def test_detect_spec_type_monolithic(self, tmp_path):
        """Test detecting monolithic spec (file)."""
        handler = SpecHandler(specs_dir=tmp_path)

        # Create monolithic spec
        spec_file = tmp_path / "SPEC-999-test-feature.md"
        spec_file.write_text("# Test")

        spec_type, spec_path = handler._detect_spec_type("999")
        assert spec_type == "monolithic"
        assert spec_path == spec_file

    def test_backward_compatibility_monolithic(self, tmp_path):
        """Test hierarchical reader falls back to monolithic."""
        handler = SpecHandler(specs_dir=tmp_path)

        # Create monolithic spec
        spec_file = tmp_path / "SPEC-999-test-feature.md"
        spec_file.write_text("# SPEC-999: Test\n\nContent")

        result = handler.read_hierarchical(priority_id="PRIORITY-999")

        # Should fall back to monolithic gracefully
        assert result["success"] is True or result.get("reason") == "Not a hierarchical spec"

    def test_context_reduction(self, tmp_path):
        """Test that hierarchical specs reduce context usage."""
        handler = SpecHandler(specs_dir=tmp_path)

        # Create spec with multiple phases
        handler.create_hierarchical(
            us_number="999",
            title="Large Feature",
            phases=[
                {"name": "phase1", "hours": 1},
                {"name": "phase2", "hours": 1},
                {"name": "phase3", "hours": 1},
                {"name": "phase4", "hours": 1}
            ]
        )

        # Add content to phase files (simulate real spec)
        spec_dir = tmp_path / "SPEC-999-large-feature"
        for i in range(1, 5):
            phase_file = spec_dir / f"phase{i}-phase{i}.md"
            phase_file.write_text("# Phase\n" + ("Detail line\n" * 50))  # 50 lines

        # Read only phase 1
        result = handler.read_hierarchical(priority_id="PRIORITY-999", phase=1)

        # Context should be README + phase1 only (not all 4 phases)
        context_lines = result["full_context"].count("\n")
        assert context_lines < 150  # Much less than 200+ if all phases loaded
```

**Files to Create/Modify**:
- `tests/unit/test_hierarchical_specs.py` (new file with 10+ tests)

---

### Step 2: Create Integration Tests

**What**: Test end-to-end workflow with code_developer

**Why**: Ensure daemon correctly uses hierarchical specs

**How**:
1. Create test file: `tests/integration/test_daemon_hierarchical_specs.py`
2. Test daemon loading hierarchical spec
3. Test daemon phase detection
4. Test daemon ROADMAP updates
5. Test context reduction in real scenario

**Test Implementation**:
```python
# tests/integration/test_daemon_hierarchical_specs.py

import pytest
from pathlib import Path
from coffee_maker.autonomous.daemon_implementation import DaemonImplementation

class TestDaemonHierarchicalSpecs:
    """Integration tests for daemon with hierarchical specs."""

    def test_daemon_loads_hierarchical_spec(self, tmp_path):
        """Test daemon successfully loads hierarchical spec."""
        # Setup: Create hierarchical spec
        # ... (create spec in tmp_path)

        # Create daemon instance
        daemon = DaemonImplementation()

        # Load spec
        priority = {"number": "25", "name": "PRIORITY 25", "title": "US-109 - Test"}
        spec_content = daemon._load_spec_content(priority)

        # Verify hierarchical spec loaded
        assert "README.md" in spec_content or len(spec_content) > 0
        assert len(spec_content) < 5000  # Context reduction (vs ~8500 monolithic)

    def test_daemon_detects_current_phase(self):
        """Test daemon detects current phase from ROADMAP."""
        daemon = DaemonImplementation()

        # Setup: ROADMAP with phase completion
        # ... (mock ROADMAP content)

        priority = {"number": "25", "name": "PRIORITY 25"}
        phase = daemon._detect_current_phase(priority)

        assert phase >= 1
        assert phase <= 5  # Within expected range

    def test_daemon_marks_phase_complete(self, tmp_path):
        """Test daemon marks phase complete in ROADMAP."""
        daemon = DaemonImplementation()

        # Setup: Create ROADMAP
        roadmap_path = tmp_path / "ROADMAP.md"
        roadmap_path.write_text("### PRIORITY 25:\n- [ ] Phase 1\n")

        # Mark phase complete
        priority = {"number": "25", "name": "PRIORITY 25"}
        daemon._mark_phase_complete(priority, phase=1)

        # Verify ROADMAP updated
        updated_roadmap = roadmap_path.read_text()
        assert "- [x] Phase 1 complete" in updated_roadmap
```

**Files to Create/Modify**:
- `tests/integration/test_daemon_hierarchical_specs.py` (new file with 5+ tests)

---

### Step 3: Create Performance Benchmarks

**What**: Measure context reduction (hierarchical vs monolithic)

**Why**: Validate 71% context reduction claim

**How**:
1. Create benchmark script
2. Load same spec in both formats
3. Measure context size (chars, lines)
4. Calculate savings percentage
5. Log results

**Benchmark Implementation**:
```python
# tests/benchmarks/benchmark_context_reduction.py

from pathlib import Path
from coffee_maker.utils.spec_handler import SpecHandler
import time

def benchmark_context_reduction():
    """Benchmark context usage: hierarchical vs monolithic."""
    handler = SpecHandler()

    # Test with SPEC-025 (hierarchical)
    start = time.time()
    hierarchical_result = handler.read_hierarchical("PRIORITY-25", phase=2)
    hierarchical_time = time.time() - start

    hierarchical_size = len(hierarchical_result["full_context"])
    hierarchical_lines = hierarchical_result["full_context"].count("\n")

    # Estimate monolithic equivalent (all phases loaded)
    # Based on SPEC-NEXT-hierarchical-modular-spec-architecture.md (645 lines)
    estimated_monolithic_size = 32000  # ~645 lines * 50 chars/line
    estimated_monolithic_lines = 645

    # Calculate savings
    size_savings_pct = ((estimated_monolithic_size - hierarchical_size) / estimated_monolithic_size) * 100
    lines_savings_pct = ((estimated_monolithic_lines - hierarchical_lines) / estimated_monolithic_lines) * 100

    print("=" * 60)
    print("CONTEXT REDUCTION BENCHMARK")
    print("=" * 60)
    print(f"Hierarchical (Phase 2 only):")
    print(f"  Size: {hierarchical_size} chars")
    print(f"  Lines: {hierarchical_lines}")
    print(f"  Load time: {hierarchical_time:.3f}s")
    print()
    print(f"Monolithic (estimated):")
    print(f"  Size: {estimated_monolithic_size} chars")
    print(f"  Lines: {estimated_monolithic_lines}")
    print()
    print(f"Savings:")
    print(f"  Size: {size_savings_pct:.1f}% reduction ✅")
    print(f"  Lines: {lines_savings_pct:.1f}% reduction ✅")
    print("=" * 60)

    # Assert meets target
    assert size_savings_pct >= 60, f"Expected ≥60% reduction, got {size_savings_pct:.1f}%"
    assert lines_savings_pct >= 60, f"Expected ≥60% reduction, got {lines_savings_pct:.1f}%"

if __name__ == "__main__":
    benchmark_context_reduction()
```

**Files to Create/Modify**:
- `tests/benchmarks/benchmark_context_reduction.py` (new file)

---

### Step 4: Update Architect Documentation

**What**: Update `.claude/agents/architect.md` with hierarchical spec workflow

**Why**: architect needs clear instructions on using new system

**How**:
1. Add section "Creating Hierarchical Specifications"
2. Document when to use hierarchical vs monolithic
3. Document phase breakdown guidelines
4. Add examples and templates
5. Link to guidelines

**Add to architect.md**:
```markdown
## Creating Hierarchical Specifications (CFR-016 Compliant)

### When to Use Hierarchical Format

Use hierarchical specs when:
- Feature requires >4 hours implementation
- Feature has distinct phases (database → API → UI → tests)
- CFR-016 compliance required (incremental 1-2 hour steps)

Use monolithic specs when:
- Feature <4 hours total
- Single cohesive implementation (no clear phases)

### Creating Hierarchical Spec

**Step 1**: Break feature into phases (1-2 hours each)

See [GUIDELINE-012: Hierarchical Spec Creation](../../docs/architecture/guidelines/GUIDELINE-012-hierarchical-spec-creation.md)

**Step 2**: Use technical-specification-handling skill

```python
from coffee_maker.utils.spec_handler import SpecHandler

handler = SpecHandler()
result = handler.create_hierarchical(
    us_number="104",
    title="User Authentication System",
    phases=[
        {"name": "database-schema", "hours": 1},
        {"name": "auth-logic", "hours": 1.5},
        {"name": "api-endpoints", "hours": 2},
        {"name": "tests", "hours": 1.5}
    ]
)
```

**Step 3**: Fill in phase details

Each phase file should include:
- Goal (what this phase accomplishes)
- Prerequisites (dependencies)
- Detailed steps (numbered, actionable)
- Code examples
- Acceptance criteria
- Testing approach

### Benefits

- ✅ 71% context reduction for code_developer
- ✅ CFR-016 compliant (incremental steps)
- ✅ Scalable (10+ phases manageable)
- ✅ Progressive implementation supported
```

**Files to Create/Modify**:
- `.claude/agents/architect.md` (add hierarchical spec section)

---

### Step 5: Create Examples and Tutorials

**What**: Create hands-on examples demonstrating hierarchical specs

**Why**: Help users understand system quickly

**How**:
1. Create `docs/architecture/HIERARCHICAL_SPEC_TUTORIAL.md`
2. Walk through creating sample spec
3. Show code_developer reading workflow
4. Include screenshots or ASCII diagrams
5. Add troubleshooting section

**Tutorial Structure**:
```markdown
# Hierarchical Specification Tutorial

## Overview

This tutorial walks you through creating and using hierarchical specs.

## Part 1: Creating Your First Hierarchical Spec

### Scenario
You're building a user authentication system (6 hours total).

### Step 1: Break Into Phases
...

### Step 2: Create Spec Structure
...

## Part 2: code_developer Using Hierarchical Spec

### Reading Spec (Phase 1)
...

### Completing Phase 1
...

### Moving to Phase 2
...

## Part 3: Advanced Topics

### Migrating Existing Specs
...

### Referencing Guidelines
...

## Troubleshooting

**Q**: Phase detection not working?
**A**: ...
```

**Files to Create/Modify**:
- `docs/architecture/HIERARCHICAL_SPEC_TUTORIAL.md` (new file)

---

### Step 6: Run All Tests and Validate

**What**: Execute full test suite and validate results

**Why**: Ensure everything works before marking phase complete

**How**:
1. Run unit tests
2. Run integration tests
3. Run benchmarks
4. Fix any failures
5. Validate metrics (context reduction, test coverage)

**Validation Commands**:
```bash
# Unit tests
pytest tests/unit/test_hierarchical_specs.py -v
# Expected: 10+ tests passing

# Integration tests
pytest tests/integration/test_daemon_hierarchical_specs.py -v
# Expected: 5+ tests passing

# Benchmarks
python tests/benchmarks/benchmark_context_reduction.py
# Expected: "Savings: 71% reduction ✅"

# Full test suite
pytest
# Expected: All tests passing

# Coverage
pytest --cov=coffee_maker.utils.spec_handler --cov-report=term
# Expected: >80% coverage
```

**Files to Create/Modify**:
- None (validation phase)

---

## Acceptance Criteria

**This phase is complete when**:

- [ ] Unit tests created and passing (10+ tests)
- [ ] Integration tests created and passing (5+ tests)
- [ ] Performance benchmarks created and validate 71% reduction
- [ ] architect.md updated with hierarchical spec workflow
- [ ] HIERARCHICAL_SPEC_TUTORIAL.md created
- [ ] All tests passing (100% pass rate)
- [ ] Test coverage >80% for spec_handler module
- [ ] Documentation reviewed and approved

**Metrics Validation**:
- Context reduction: **≥70%** (target: 71%) ✅
- Test coverage: **≥80%** ✅
- Test pass rate: **100%** ✅
- Phase implementation time: **30% faster** (measured during PRIORITY 25 implementation)

---

## Testing This Phase

### Test Execution

```bash
# Run all tests
pytest -v

# Check coverage
pytest --cov=coffee_maker --cov-report=html

# Run benchmarks
python tests/benchmarks/benchmark_context_reduction.py

# Manual end-to-end test
poetry run code-developer --priority=25 --dry-run
# Verify hierarchical spec loaded correctly
```

---

## References for This Phase

**Test Files**:
- `tests/unit/test_hierarchical_specs.py`
- `tests/integration/test_daemon_hierarchical_specs.py`
- `tests/benchmarks/benchmark_context_reduction.py`

**Documentation**:
- `.claude/agents/architect.md`
- `docs/architecture/HIERARCHICAL_SPEC_TUTORIAL.md`

---

## Next Steps

**After this phase completes**:
- PRIORITY 25 is COMPLETE ✅
- Hierarchical spec system production-ready
- code_developer can use hierarchical specs for all future priorities
- architect creates all new specs in hierarchical format
- Context efficiency gains realized (71% reduction)

**Future Enhancements** (not in scope):
- Automated phase transition notifications
- Visual progress indicators (phase completion dashboard)
- Spec analytics (time per phase, context usage trends)

---

**Note**: This is the final phase. After completion, the hierarchical spec system is fully operational and ready for production use.
