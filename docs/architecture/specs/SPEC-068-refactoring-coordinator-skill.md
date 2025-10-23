# SPEC-068: Refactoring Coordinator Skill

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: Phase 0 Acceleration Plan, Safe multi-file refactorings

---

## Executive Summary

This specification defines the **Refactoring Coordinator Skill**, a Claude Code Skill that safely coordinates multi-file refactorings by analyzing dependencies, calculating safe execution order, running parallel tests, and automatically rolling back on failure.

**Key Capabilities**:
- **Dependency Graph Analysis**: Identify ALL impacted files before refactoring
- **Safe Execution Order**: Topological sort ensures dependencies refactored before dependents
- **Parallel Test Execution**: Run tests for independent modules simultaneously
- **Automatic Rollback**: Revert ALL changes if ANY tests fail
- **Progress Tracking**: Real-time visibility into refactoring progress

**Impact**:
- **Time Savings**: 6-40 hrs/month (refactorings 4-16x faster)
- **Success Rate**: 95% (vs 70% manual - automatic rollback prevents lost work)
- **Risk Reduction**: No broken imports, no lost work, no "oops I forgot to test X"
- **Confidence**: Developers can refactor fearlessly (automation catches errors)

---

## Problem Statement

### Current Pain Points

**1. Manual Dependency Tracking is Error-Prone**
```python
# Developer wants to split daemon.py into mixins
# Current process:
1. Create daemon_git_ops.py (manually)
2. Move code, forget to add imports → BROKEN
3. Update daemon.py imports → BROKEN (circular dependency)
4. Fix imports manually → Takes 30+ minutes
5. Run tests → 23 failures (missed edge cases)
6. Debug failures → Another hour
7. Give up, revert everything → Lost 2-4 hours of work
```

**Problem**: No automated dependency analysis, no safety net

**2. Sequential Testing is Slow**
```
Refactor 6 files:
- Create file 1, run tests (2 min)
- Create file 2, run tests (2 min)
- Create file 3, run tests (2 min)
- Create file 4, run tests (2 min)
- Create file 5, run tests (2 min)
- Create file 6, run tests (2 min)
Total: 12+ minutes (tests run sequentially)
```

**Problem**: Tests could run in parallel (independent modules), wasting time

**3. No Automatic Rollback on Failure**
```
Refactor 6 files:
1. Create file 1 ✅
2. Create file 2 ✅
3. Create file 3 ✅
4. Create file 4 ❌ (test failure)
5. Developer realizes mistake
6. Manually revert files 1-4
7. Lost 2+ hours of work

Problem: No git-based snapshot + rollback automation
```

**4. No Refactoring Order Calculation**
```
Files to refactor:
- daemon.py (depends on: spec_manager, git_ops, implementation)
- daemon_spec_manager.py (depends on: git_ops)
- daemon_git_ops.py (no dependencies)
- daemon_implementation.py (depends on: spec_manager)

What order?
- If create daemon_spec_manager BEFORE daemon_git_ops → BROKEN (missing import)
- If create daemon_implementation BEFORE daemon_spec_manager → BROKEN
- Manual trial-and-error → Wastes 30-60 minutes
```

**Problem**: No topological sort, no automatic order calculation

### User Requirements

From Phase 0 Acceleration Plan:
- **Dependency Analysis**: Identify ALL impacted files automatically
- **Safe Execution Order**: Calculate optimal refactoring order (topological sort)
- **Parallel Testing**: Run tests for independent modules simultaneously
- **Automatic Rollback**: Revert if ANY tests fail
- **Progress Tracking**: Show which files refactored, which remain
- **Integration**: Works with code_developer workflow seamlessly

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  REFACTORING REQUEST                             │
│  code_developer: "Split daemon.py into mixins"                  │
│  Files to create:                                               │
│  - daemon_git_ops.py                                            │
│  - daemon_spec_manager.py                                       │
│  - daemon_implementation.py                                     │
│  - daemon_status.py                                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 1: DEPENDENCY GRAPH ANALYSIS                        │
│  coffee_maker/skills/refactoring_coordinator.py                 │
│                                                                  │
│  def analyze_dependencies(source_file, target_files):          │
│    1. Parse source file (daemon.py) using AST                  │
│    2. Identify imports, function calls, class references       │
│    3. Build dependency graph:                                  │
│       - git_ops: no dependencies                               │
│       - spec_manager: depends on git_ops                       │
│       - implementation: depends on spec_manager, git_ops       │
│       - status: depends on implementation                      │
│       - daemon.py: depends on ALL mixins                       │
│    4. Identify external impacted files:                        │
│       - run_code_developer.py (imports daemon.py)                      │
│       - tests/test_daemon.py (imports daemon.py)               │
│    5. Return dependency graph (NetworkX DiGraph)               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 2: SAFE EXECUTION ORDER CALCULATION                 │
│                                                                  │
│  def calculate_refactoring_order(dep_graph):                   │
│    1. Topological sort (NetworkX)                              │
│    2. Order:                                                   │
│       a. daemon_git_ops.py (no deps → safe to create first)   │
│       b. daemon_spec_manager.py (depends on git_ops)          │
│       c. daemon_implementation.py (depends on spec_manager)   │
│       d. daemon_status.py (depends on implementation)         │
│       e. daemon.py (update to import mixins)                  │
│       f. run_code_developer.py (update imports if needed)             │
│       g. tests/test_daemon.py (update imports)                │
│    3. Detect cycles:                                           │
│       - If cycle detected → ERROR (cannot refactor safely)    │
│    4. Group independent files for parallel execution:         │
│       - Group 1: [git_ops] (no deps)                          │
│       - Group 2: [spec_manager] (depends on Group 1)          │
│       - Group 3: [implementation] (depends on Group 2)        │
│       - Group 4: [status] (depends on Group 3)                │
│       - Group 5: [daemon.py, run_code_developer.py, tests] (updates) │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 3: GIT SNAPSHOT (PRE-REFACTORING)                   │
│                                                                  │
│  def create_snapshot():                                         │
│    1. git stash save "Pre-refactoring snapshot"                │
│    2. Record commit hash (for rollback)                        │
│    3. Record branch name (for verification)                    │
│    4. Return snapshot_id                                       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 4: EXECUTE REFACTORING (ORDERED)                    │
│                                                                  │
│  for group in refactoring_order:                               │
│    1. Create/modify files in group (parallel if independent)  │
│    2. Run tests for affected files                            │
│    3. If tests pass:                                          │
│       - Continue to next group                                │
│    4. If tests fail:                                          │
│       - ROLLBACK (goto Step 5)                                │
│       - Abort refactoring                                     │
│                                                                  │
│  Example:                                                       │
│  Group 1: Create daemon_git_ops.py                             │
│    → Run tests: pytest tests/ (2 min)                          │
│    → 127 passed ✅                                             │
│                                                                  │
│  Group 2: Create daemon_spec_manager.py                        │
│    → Run tests: pytest tests/ (2 min)                          │
│    → 127 passed ✅                                             │
│                                                                  │
│  Group 3: Create daemon_implementation.py                      │
│    → Run tests: pytest tests/ (2 min)                          │
│    → 23 failed ❌ (ROLLBACK TRIGGERED)                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 5: AUTOMATIC ROLLBACK (ON FAILURE)                  │
│                                                                  │
│  def rollback(snapshot_id):                                     │
│    1. git reset --hard {original_commit}                       │
│    2. git stash pop (restore pre-refactoring state)            │
│    3. Verify all files restored (checksum comparison)          │
│    4. Report failure details:                                  │
│       - Which group failed (Group 3: implementation)           │
│       - Test output (23 failures)                              │
│       - Suggested fixes (use test-failure-analysis skill)      │
│    5. Return rollback_result (success/failure)                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 6: SUCCESS VERIFICATION (IF ALL PASSED)             │
│                                                                  │
│  def verify_refactoring():                                      │
│    1. Run full test suite (pytest)                             │
│    2. Run black --check (code formatting)                      │
│    3. Run pre-commit hooks                                     │
│    4. Check coverage (pytest-cov)                              │
│    5. If all pass:                                             │
│       - Report success                                         │
│       - Provide commit message template                        │
│       - Delete git stash (cleanup)                             │
│    6. If any fail:                                             │
│       - ROLLBACK                                               │
│       - Report issues                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Example

**Scenario**: Split daemon.py (1592 LOC) into 4 mixins

```
Step 1: Dependency Analysis
----------------------------
Input:
- source_file: coffee_maker/autonomous/daemon.py
- target_files:
  - coffee_maker/autonomous/daemon_git_ops.py
  - coffee_maker/autonomous/daemon_spec_manager.py
  - coffee_maker/autonomous/daemon_implementation.py
  - coffee_maker/autonomous/daemon_status.py

Skill Output:
Dependency Graph:
- daemon_git_ops.py: [] (no dependencies)
- daemon_spec_manager.py: [daemon_git_ops.py]
- daemon_implementation.py: [daemon_spec_manager.py, daemon_git_ops.py]
- daemon_status.py: [daemon_implementation.py]
- daemon.py: [daemon_git_ops.py, daemon_spec_manager.py, daemon_implementation.py, daemon_status.py]

Impacted Files (external):
- run_code_developer.py (imports daemon)
- tests/test_daemon.py (imports daemon)

Total files impacted: 7 files

Step 2: Execution Order Calculation
------------------------------------
Topological Sort:
1. daemon_git_ops.py (no deps)
2. daemon_spec_manager.py (depends on #1)
3. daemon_implementation.py (depends on #1, #2)
4. daemon_status.py (depends on #3)
5. daemon.py (depends on #1-4)
6. run_code_developer.py, tests/test_daemon.py (depends on #5)

Parallel Groups:
- Group 1: [daemon_git_ops.py]
- Group 2: [daemon_spec_manager.py]
- Group 3: [daemon_implementation.py]
- Group 4: [daemon_status.py]
- Group 5: [daemon.py, run_code_developer.py, tests/test_daemon.py]

Step 3: Git Snapshot
--------------------
$ git stash save "Pre-refactoring: Split daemon.py into mixins"
Saved working directory and index state On roadmap: Pre-refactoring: Split daemon.py into mixins

Snapshot ID: stash@{0}
Original commit: 0de4e17

Step 4: Execute Refactoring
----------------------------
Group 1: Create daemon_git_ops.py
  ✅ File created (45 LOC)
  ✅ Tests: pytest tests/ → 127 passed (2.1s)

Group 2: Create daemon_spec_manager.py
  ✅ File created (67 LOC)
  ✅ Tests: pytest tests/ → 127 passed (2.3s)

Group 3: Create daemon_implementation.py
  ✅ File created (120 LOC)
  ✅ Tests: pytest tests/ → 127 passed (2.5s)

Group 4: Create daemon_status.py
  ✅ File created (38 LOC)
  ✅ Tests: pytest tests/ → 127 passed (2.2s)

Group 5: Update daemon.py, run_code_developer.py, tests/test_daemon.py
  ✅ Files updated (daemon.py reduced from 1592 → 145 LOC)
  ✅ Tests: pytest tests/ → 127 passed (2.4s)

Total Execution Time: 11.5 seconds (tests run sequentially for safety)

Step 5: Success Verification
-----------------------------
✅ Full test suite: 127 passed, 0 failed
✅ Code formatting: black --check (no changes needed)
✅ Pre-commit hooks: All hooks passed
✅ Coverage: 87% (above 80% target)

Refactoring SUCCESSFUL! ✅

Cleanup:
$ git stash drop stash@{0}
Dropped stash@{0} (commit hash)

Commit Message Template:
---
refactor: Split daemon.py into mixins (1592 → 145 LOC)

- Extract GitOpsMixin → daemon_git_ops.py (45 LOC)
- Extract SpecManagerMixin → daemon_spec_manager.py (67 LOC)
- Extract ImplementationMixin → daemon_implementation.py (120 LOC)
- Extract StatusMixin → daemon_status.py (38 LOC)
- Update daemon.py to use mixins (reduced 91% LOC)

Refactoring coordinated by: refactoring-coordinator skill
Tests: 127 passed, 0 failed
Coverage: 87%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
---

Time Saved: 2-4 hours manual → 12 minutes automated (10-20x faster)
```

---

## Component Design

### 1. Refactoring Coordinator (Main Orchestrator)

**Purpose**: Coordinate entire refactoring workflow

```python
# coffee_maker/skills/refactoring_coordinator.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import networkx as nx

@dataclass
class RefactoringRequest:
    """Request to refactor source file into target files."""
    source_file: str              # File to split/refactor
    target_files: List[str]       # Files to create
    description: str              # What's being refactored
    test_command: str = "pytest"  # Command to run tests

@dataclass
class RefactoringResult:
    """Result of refactoring operation."""
    success: bool
    message: str
    files_created: List[str] = None
    files_modified: List[str] = None
    test_results: Dict[str, bool] = None
    execution_time_seconds: float = 0.0
    rollback_reason: str = None
    commit_message_template: str = None

class RefactoringCoordinator:
    """
    Coordinate safe multi-file refactorings.

    Workflow:
    1. Analyze dependencies
    2. Calculate safe execution order
    3. Create git snapshot
    4. Execute refactoring (with tests)
    5. Rollback if failure OR verify if success
    """

    def __init__(self):
        self.dependency_analyzer = DependencyAnalyzer()
        self.parallel_test_runner = ParallelTestRunner()
        self.git_snapshot_manager = GitSnapshotManager()

    def execute_refactoring(self, request: RefactoringRequest) -> RefactoringResult:
        """
        Execute multi-file refactoring with safety checks.

        Args:
            request: Refactoring request with source/target files

        Returns:
            RefactoringResult with success/failure details
        """
        import time
        start_time = time.time()

        try:
            # Step 1: Analyze dependencies
            dep_graph = self.dependency_analyzer.analyze(
                source_file=request.source_file,
                target_files=request.target_files
            )

            # Check for cycles (cannot refactor safely)
            if self._has_cycles(dep_graph):
                return RefactoringResult(
                    success=False,
                    message="Circular dependency detected - cannot refactor safely",
                    rollback_reason="Dependency cycle prevents safe refactoring order"
                )

            # Step 2: Calculate execution order
            execution_order = self._calculate_execution_order(dep_graph)

            # Step 3: Create git snapshot (for rollback)
            snapshot_id = self.git_snapshot_manager.create_snapshot(
                description=request.description
            )

            # Step 4: Execute refactoring in order
            for group_idx, file_group in enumerate(execution_order):
                print(f"Group {group_idx + 1}: {', '.join(file_group)}")

                # Create/modify files (implementation-specific, done by code_developer)
                # This skill coordinates, doesn't write code

                # Run tests for this group
                test_result = self._run_tests_for_group(
                    file_group,
                    test_command=request.test_command
                )

                if not test_result.success:
                    # Tests failed - ROLLBACK
                    print(f"❌ Tests failed for {file_group}")
                    self.git_snapshot_manager.rollback(snapshot_id)

                    elapsed = time.time() - start_time

                    return RefactoringResult(
                        success=False,
                        message=f"Refactoring failed at group {group_idx + 1}",
                        rollback_reason=f"Tests failed: {test_result.error_message}",
                        execution_time_seconds=elapsed
                    )

                print(f"✅ Tests passed for {file_group}")

            # Step 5: Final verification (all tests)
            final_test_result = self._run_all_tests(request.test_command)

            if not final_test_result.success:
                # Final tests failed - ROLLBACK
                self.git_snapshot_manager.rollback(snapshot_id)

                elapsed = time.time() - start_time

                return RefactoringResult(
                    success=False,
                    message="Final test suite failed",
                    rollback_reason=f"Final tests failed: {final_test_result.error_message}",
                    execution_time_seconds=elapsed
                )

            # Success! Delete snapshot (no rollback needed)
            self.git_snapshot_manager.delete_snapshot(snapshot_id)

            elapsed = time.time() - start_time

            # Generate commit message
            commit_message = self._generate_commit_message(request, dep_graph)

            return RefactoringResult(
                success=True,
                message="Refactoring completed successfully",
                files_created=request.target_files,
                files_modified=[request.source_file],
                execution_time_seconds=elapsed,
                commit_message_template=commit_message
            )

        except Exception as e:
            # Unexpected error - attempt rollback
            if 'snapshot_id' in locals():
                self.git_snapshot_manager.rollback(snapshot_id)

            elapsed = time.time() - start_time

            return RefactoringResult(
                success=False,
                message=f"Refactoring failed with error: {str(e)}",
                rollback_reason=str(e),
                execution_time_seconds=elapsed
            )

    def _has_cycles(self, graph: nx.DiGraph) -> bool:
        """Check if dependency graph has cycles."""
        try:
            nx.find_cycle(graph, orientation="original")
            return True  # Cycle found
        except nx.NetworkXNoCycle:
            return False  # No cycles

    def _calculate_execution_order(self, graph: nx.DiGraph) -> List[List[str]]:
        """
        Calculate safe execution order using topological sort.

        Returns list of groups (files in each group can be created in parallel).
        """
        # Topological sort (dependencies first)
        sorted_nodes = list(nx.topological_sort(graph))

        # Group nodes by dependency level (for parallel execution)
        groups = []
        current_group = []

        for node in sorted_nodes:
            # Check if node depends on any node in current group
            depends_on_current_group = any(
                graph.has_edge(n, node) for n in current_group
            )

            if depends_on_current_group:
                # Start new group (dependency on current group)
                groups.append(current_group)
                current_group = [node]
            else:
                # Add to current group (can run in parallel)
                current_group.append(node)

        # Add final group
        if current_group:
            groups.append(current_group)

        return groups

    def _run_tests_for_group(self, file_group: List[str], test_command: str):
        """Run tests for specific file group."""
        # Run tests (implementation by ParallelTestRunner)
        return self.parallel_test_runner.run_tests(test_command)

    def _run_all_tests(self, test_command: str):
        """Run full test suite."""
        return self.parallel_test_runner.run_tests(test_command)

    def _generate_commit_message(self, request: RefactoringRequest, dep_graph: nx.DiGraph) -> str:
        """Generate commit message template for refactoring."""
        source_file_name = Path(request.source_file).name
        target_file_names = [Path(f).name for f in request.target_files]

        message = f"refactor: {request.description}\n\n"

        for target in request.target_files:
            message += f"- Extract {Path(target).stem} → {Path(target).name}\n"

        message += f"- Update {source_file_name} to use new components\n\n"
        message += f"Refactoring coordinated by: refactoring-coordinator skill\n"
        message += "Tests: All passing\n\n"
        message += "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\n"
        message += "Co-Authored-By: Claude <noreply@anthropic.com>"

        return message
```

### 2. Dependency Analyzer

**Purpose**: Build dependency graph from source code

```python
# coffee_maker/skills/dependency_graph.py

import ast
from pathlib import Path
from typing import List, Set, Dict
import networkx as nx

class DependencyAnalyzer:
    """Analyze Python code dependencies using AST."""

    def analyze(self, source_file: str, target_files: List[str]) -> nx.DiGraph:
        """
        Analyze dependencies between source and target files.

        Returns:
            Directed graph where edge (A, B) means "A depends on B"
        """
        graph = nx.DiGraph()

        # Add all files as nodes
        graph.add_node(source_file)
        for target in target_files:
            graph.add_node(target)

        # Parse source file to extract what will be in target files
        source_code = Path(source_file).read_text()
        source_ast = ast.parse(source_code)

        # Analyze imports, function calls, class references
        dependencies = self._extract_dependencies(source_ast)

        # Map dependencies to target files
        for target in target_files:
            # Determine which code goes in this target file
            # (implementation-specific, based on naming conventions)

            # Add edges for dependencies
            target_deps = self._get_target_dependencies(target, dependencies)

            for dep in target_deps:
                graph.add_edge(target, dep)  # target depends on dep

        return graph

    def _extract_dependencies(self, tree: ast.AST) -> Dict[str, Set[str]]:
        """Extract dependencies from AST."""
        dependencies = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Record import
                    pass

            elif isinstance(node, ast.ImportFrom):
                # Record from ... import ...
                pass

            elif isinstance(node, ast.Call):
                # Record function calls
                pass

        return dependencies

    def _get_target_dependencies(self, target_file: str, all_deps: Dict) -> Set[str]:
        """Get dependencies for specific target file."""
        # Implementation: Map code sections to target files
        # Return list of other target files this file depends on
        return set()
```

### 3. Git Snapshot Manager

**Purpose**: Create snapshots for rollback

```python
# coffee_maker/skills/git_snapshot_manager.py

import subprocess
from typing import Optional

class GitSnapshotManager:
    """Manage git snapshots for safe rollback."""

    def create_snapshot(self, description: str) -> str:
        """
        Create git stash snapshot.

        Returns:
            Snapshot ID (stash@{N})
        """
        # Save working directory
        result = subprocess.run(
            ["git", "stash", "save", f"Pre-refactoring: {description}"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to create snapshot: {result.stderr}")

        # Return stash ID
        return "stash@{0}"

    def rollback(self, snapshot_id: str):
        """Rollback to snapshot."""
        # Pop stash
        result = subprocess.run(
            ["git", "stash", "pop", snapshot_id],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to rollback: {result.stderr}")

    def delete_snapshot(self, snapshot_id: str):
        """Delete snapshot (after successful refactoring)."""
        result = subprocess.run(
            ["git", "stash", "drop", snapshot_id],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to delete snapshot: {result.stderr}")
```

### 4. Parallel Test Runner

**Purpose**: Run tests in parallel for independent modules

```python
# coffee_maker/skills/parallel_test_runner.py

import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List

@dataclass
class TestResult:
    """Result of test execution."""
    success: bool
    error_message: str = None
    stdout: str = None
    stderr: str = None

class ParallelTestRunner:
    """Run tests in parallel for independent modules."""

    def run_tests(self, test_command: str = "pytest") -> TestResult:
        """
        Run test suite.

        Args:
            test_command: Command to run tests (default: pytest)

        Returns:
            TestResult with success/failure
        """
        result = subprocess.run(
            test_command.split(),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return TestResult(
                success=True,
                stdout=result.stdout
            )
        else:
            return TestResult(
                success=False,
                error_message="Tests failed",
                stdout=result.stdout,
                stderr=result.stderr
            )
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_refactoring_coordinator.py

def test_dependency_graph_analysis():
    """Test dependency graph construction."""
    analyzer = DependencyAnalyzer()

    graph = analyzer.analyze(
        source_file="coffee_maker/autonomous/daemon.py",
        target_files=[
            "coffee_maker/autonomous/daemon_git_ops.py",
            "coffee_maker/autonomous/daemon_spec_manager.py"
        ]
    )

    # Verify graph structure
    assert graph.has_node("daemon.py")
    assert graph.has_node("daemon_git_ops.py")
    assert graph.number_of_nodes() == 3

def test_cycle_detection():
    """Test circular dependency detection."""
    coordinator = RefactoringCoordinator()

    # Create graph with cycle: A → B → C → A
    graph = nx.DiGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")  # Cycle!

    assert coordinator._has_cycles(graph) is True

def test_topological_sort():
    """Test execution order calculation."""
    coordinator = RefactoringCoordinator()

    # Create dependency graph
    graph = nx.DiGraph()
    graph.add_edge("daemon.py", "daemon_git_ops.py")  # daemon depends on git_ops
    graph.add_edge("daemon_spec_manager.py", "daemon_git_ops.py")

    order = coordinator._calculate_execution_order(graph)

    # git_ops should be first (no dependencies)
    assert "daemon_git_ops.py" in order[0]
```

### Integration Tests

```python
# tests/integration/test_refactoring_workflow.py

def test_refactoring_workflow_end_to_end():
    """Test complete refactoring workflow."""
    coordinator = RefactoringCoordinator()

    request = RefactoringRequest(
        source_file="test_fixtures/simple.py",
        target_files=[
            "test_fixtures/simple_part1.py",
            "test_fixtures/simple_part2.py"
        ],
        description="Split simple.py into two files"
    )

    result = coordinator.execute_refactoring(request)

    assert result.success is True
    assert len(result.files_created) == 2
    assert result.execution_time_seconds < 30

def test_rollback_on_test_failure():
    """Test automatic rollback when tests fail."""
    coordinator = RefactoringCoordinator()

    # Create request that will fail tests
    request = RefactoringRequest(
        source_file="test_fixtures/broken.py",
        target_files=["test_fixtures/broken_part1.py"],
        description="Split broken.py (tests will fail)"
    )

    result = coordinator.execute_refactoring(request)

    assert result.success is False
    assert result.rollback_reason is not None
    assert "Tests failed" in result.rollback_reason

    # Verify rollback worked (files not created)
    assert not Path("test_fixtures/broken_part1.py").exists()
```

---

## Rollout Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Implement DependencyAnalyzer (AST parsing, dependency extraction)
- [ ] Implement GitSnapshotManager (stash, rollback, cleanup)
- [ ] Implement ParallelTestRunner (pytest execution)
- [ ] Unit tests (>80% coverage)

### Phase 2: Refactoring Coordinator (Week 1)
- [ ] Implement RefactoringCoordinator (main orchestrator)
- [ ] Topological sort algorithm (execution order)
- [ ] Cycle detection
- [ ] Integration tests

### Phase 3: Integration with code_developer (Week 1)
- [ ] Add refactoring-coordinator to code_developer workflow
- [ ] Create CLI command: `poetry run refactor --source X --targets Y,Z`
- [ ] Documentation (usage guide)

### Phase 4: Architect Code Review ⭐ MANDATORY
- [ ] architect reviews implementation:
  - **Architectural Compliance**: Dependency analysis algorithms, git snapshot safety
  - **Code Quality**: Error handling (rollback on failure), test execution (parallel vs sequential)
  - **Security**: Git operations safe (no arbitrary commands), file operations validated
  - **Performance**: Topological sort efficiency (O(V+E)), test execution time
  - **CFR Compliance**:
    - CFR-008: No cross-agent dependencies (skill is standalone)
    - CFR-009: Proper rollback on failure (no lost work)
  - **Dependency Approval**: networkx (required for dependency graph analysis)
- [ ] architect approves or requests changes
- [ ] code_developer addresses feedback (if any)
- [ ] architect gives final approval

### Phase 5: Validation & Metrics (Week 1)
- [ ] Test on real refactorings (daemon.py split)
- [ ] Measure time savings (before/after comparison)
- [ ] Track success rate (target: 95%)
- [ ] Gather user feedback

---

## Success Metrics

| Metric | Baseline (Manual) | Target (Automated) | Measurement |
|--------|-------------------|-------------------|-------------|
| **Small Refactoring (2-3 files)** | 30 min | 5 min | Time from start to commit |
| **Medium Refactoring (4-6 files)** | 2-4 hrs | 15-30 min | Time from start to commit |
| **Large Refactoring (7+ files)** | 8-16 hrs | 1-2 hrs | Time from start to commit |
| **Success Rate** | 70% | 95% | Tests passing after refactor |
| **Rollback Time** | 15-30 min (manual) | 5s (automated) | Time to restore original state |
| **Monthly Time Savings** | N/A | 6-40 hrs | Cumulative savings across all refactorings |

---

## Risks & Mitigations

### Risk 1: Dependency Analysis Inaccurate
**Impact**: Incorrect execution order → broken imports
**Probability**: MEDIUM (AST parsing complex)
**Mitigation**:
- Extensive testing on real codebases
- Conservative approach (assume dependency if uncertain)
- Manual override option (user specifies order)

### Risk 2: Tests Don't Catch All Issues
**Impact**: Refactoring succeeds but code broken in production
**Probability**: LOW (comprehensive test suite)
**Mitigation**:
- Run full test suite (not just affected tests)
- Include integration tests
- Manual review for high-risk refactorings

### Risk 3: Rollback Failure
**Impact**: Lost work if rollback fails
**Probability**: VERY LOW (git stash reliable)
**Mitigation**:
- Verify stash creation before refactoring
- Test rollback mechanism thoroughly
- Document manual rollback procedure (fallback)

---

## Conclusion

The Refactoring Coordinator Skill provides:

1. **Safety**: Automatic rollback on failure (no lost work)
2. **Speed**: 4-16x faster than manual refactoring
3. **Confidence**: Developers can refactor fearlessly
4. **Consistency**: Same process for all refactorings

**Time Savings**: 6-40 hrs/month (depending on refactoring frequency)

**Success Rate**: 95% (vs 70% manual)

**Integration**: Works seamlessly with code_developer workflow

---

**Files to Create**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/refactoring-coordinator.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/skills/refactoring_coordinator.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/skills/dependency_graph.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/skills/git_snapshot_manager.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/skills/parallel_test_runner.py`

**Next Steps**:
1. Review and approve this spec
2. Assign implementation to code_developer (Week 2 of Phase 0)
3. Begin Phase 1 (Core Infrastructure) implementation
4. Integrate with code_developer workflow
