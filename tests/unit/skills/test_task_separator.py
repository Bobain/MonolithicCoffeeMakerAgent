"""Tests for task-separator skill."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import from the skill module
from importlib.util import module_from_spec, spec_from_file_location


def load_task_separator():
    """Dynamically load the task-separator module."""
    skill_path = (
        Path(__file__).parent.parent.parent.parent
        / ".claude"
        / "skills"
        / "architect"
        / "task-separator"
        / "task-separator.py"
    )
    spec = spec_from_file_location("task_separator", skill_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestExtractFilePatterns:
    """Tests for extract_file_patterns_from_text."""

    def setup_method(self):
        """Set up test."""
        self.module = load_task_separator()

    def test_extract_file_pattern_with_file_keyword(self):
        """Test extracting **File**: `path/to/file.py`."""
        text = "**File**: `coffee_maker/orchestrator/coordinator.py`"
        patterns = self.module.extract_file_patterns_from_text(text)
        assert "coffee_maker/orchestrator/coordinator.py" in patterns

    def test_extract_file_pattern_with_bullet_points(self):
        """Test extracting bullet points with .py files."""
        text = "- `coffee_maker/cli/dashboard.py`\n- `tests/unit/test_dashboard.py`"
        patterns = self.module.extract_file_patterns_from_text(text)
        assert "coffee_maker/cli/dashboard.py" in patterns
        assert "tests/unit/test_dashboard.py" in patterns

    def test_extract_file_pattern_with_directory_glob(self):
        """Test extracting directory patterns."""
        text = "coffee_maker/orchestrator/* and tests/orchestrator/*"
        patterns = self.module.extract_file_patterns_from_text(text)
        assert "coffee_maker/orchestrator/*" in patterns
        assert "tests/orchestrator/*" in patterns

    def test_extract_file_pattern_empty_text(self):
        """Test extracting from empty text."""
        patterns = self.module.extract_file_patterns_from_text("")
        assert len(patterns) == 0

    def test_extract_file_pattern_no_python_files(self):
        """Test extracting from text with no Python files."""
        text = "This is just regular text without any file paths."
        patterns = self.module.extract_file_patterns_from_text(text)
        assert len(patterns) == 0


class TestFilesConflict:
    """Tests for files_conflict function."""

    def setup_method(self):
        """Set up test."""
        self.module = load_task_separator()

    def test_exact_match(self):
        """Test exact file match."""
        assert self.module.files_conflict("coffee_maker/cli/dashboard.py", "coffee_maker/cli/dashboard.py")

    def test_glob_pattern_match(self):
        """Test glob pattern matching."""
        assert self.module.files_conflict("coffee_maker/orchestrator/*", "coffee_maker/orchestrator/coordinator.py")

    def test_glob_pattern_reverse(self):
        """Test glob pattern matching (reverse order)."""
        assert self.module.files_conflict("coffee_maker/orchestrator/coordinator.py", "coffee_maker/orchestrator/*")

    def test_no_conflict_different_directories(self):
        """Test no conflict for different directories."""
        assert not self.module.files_conflict(
            "coffee_maker/cli/dashboard.py", "coffee_maker/orchestrator/coordinator.py"
        )

    def test_no_conflict_different_modules(self):
        """Test no conflict for different modules."""
        assert not self.module.files_conflict("coffee_maker/skills/*", "coffee_maker/orchestrator/*")


class TestFindSafePairs:
    """Tests for find_safe_pairs function."""

    def setup_method(self):
        """Set up test."""
        self.module = load_task_separator()

    def test_find_safe_pairs_no_overlap(self):
        """Test finding safe pairs with no file overlap."""
        task_file_map = {
            20: {"coffee_maker/skills/analyzer.py"},
            21: {"coffee_maker/cli/dashboard.py"},
            22: {"coffee_maker/orchestrator/coordinator.py"},
        }
        safe_pairs = self.module.find_safe_pairs(task_file_map)
        assert (20, 21) in safe_pairs
        assert (20, 22) in safe_pairs
        assert (21, 22) in safe_pairs

    def test_find_safe_pairs_with_overlap(self):
        """Test finding safe pairs with some overlaps."""
        task_file_map = {
            20: {"coffee_maker/cli/dashboard.py"},
            21: {"coffee_maker/cli/dashboard.py"},  # Overlaps with 20
            22: {"coffee_maker/orchestrator/coordinator.py"},
        }
        safe_pairs = self.module.find_safe_pairs(task_file_map)
        assert (20, 21) not in safe_pairs  # Conflict
        assert (20, 22) in safe_pairs
        assert (21, 22) in safe_pairs

    def test_find_safe_pairs_glob_pattern_conflict(self):
        """Test finding safe pairs with glob pattern conflicts."""
        task_file_map = {
            20: {"coffee_maker/orchestrator/*"},
            21: {"coffee_maker/orchestrator/coordinator.py"},  # Matches glob
            22: {"coffee_maker/cli/dashboard.py"},
        }
        safe_pairs = self.module.find_safe_pairs(task_file_map)
        assert (20, 21) not in safe_pairs  # Conflict
        assert (20, 22) in safe_pairs
        assert (21, 22) in safe_pairs

    def test_find_safe_pairs_empty_map(self):
        """Test finding safe pairs with empty map."""
        safe_pairs = self.module.find_safe_pairs({})
        assert len(safe_pairs) == 0


class TestFindConflicts:
    """Tests for find_conflicts function."""

    def setup_method(self):
        """Set up test."""
        self.module = load_task_separator()

    def test_find_conflicts_direct_overlap(self):
        """Test finding conflicts with direct file overlap."""
        task_file_map = {
            20: {"coffee_maker/cli/dashboard.py"},
            21: {"coffee_maker/cli/dashboard.py", "tests/unit/test_dashboard.py"},
        }
        conflicts = self.module.find_conflicts(task_file_map)
        assert (20, 21) in conflicts
        assert "coffee_maker/cli/dashboard.py" in conflicts[(20, 21)]

    def test_find_conflicts_glob_pattern(self):
        """Test finding conflicts with glob patterns."""
        task_file_map = {20: {"coffee_maker/orchestrator/*"}, 21: {"coffee_maker/orchestrator/coordinator.py"}}
        conflicts = self.module.find_conflicts(task_file_map)
        assert (20, 21) in conflicts

    def test_find_conflicts_no_conflicts(self):
        """Test finding conflicts when there are none."""
        task_file_map = {20: {"coffee_maker/skills/analyzer.py"}, 21: {"coffee_maker/cli/dashboard.py"}}
        conflicts = self.module.find_conflicts(task_file_map)
        assert len(conflicts) == 0


class TestMainFunction:
    """Tests for main function (integration)."""

    def setup_method(self):
        """Set up test."""
        self.module = load_task_separator()

    def test_main_no_priority_ids(self):
        """Test main with no priority IDs."""
        result = self.module.main({})
        assert "error" in result
        assert result["independent_pairs"] == []

    def test_main_with_priority_ids(self):
        """Test main with priority IDs (uses real specs if available)."""
        # This test will succeed even if specs don't exist
        # It just tests the function doesn't crash
        result = self.module.main({"priority_ids": [20, 21, 22]})
        assert "independent_pairs" in result
        assert "conflicts" in result
        assert "task_file_map" in result
        assert isinstance(result["independent_pairs"], list)
        assert isinstance(result["conflicts"], dict)
        assert isinstance(result["task_file_map"], dict)


class TestBuildFileMap:
    """Tests for build_file_map function."""

    def setup_method(self):
        """Set up test."""
        self.module = load_task_separator()

    def test_build_file_map_with_existing_spec(self):
        """Test building file map with existing spec (US-108)."""
        # US-108 should have SPEC-108 which was created earlier
        file_map = self.module.build_file_map([108])
        assert 108 in file_map
        # Should have some files extracted from spec
        # We don't assert specific files since spec might change

    def test_build_file_map_with_nonexistent_spec(self):
        """Test building file map with non-existent spec."""
        file_map = self.module.build_file_map([9999])
        assert 9999 in file_map
        assert len(file_map[9999]) == 0  # No files found


class TestFindSpecFile:
    """Tests for find_spec_file function."""

    def setup_method(self):
        """Set up test."""
        self.module = load_task_separator()

    def test_find_spec_file_existing(self):
        """Test finding existing spec file."""
        # SPEC-108 should exist
        spec_path = self.module.find_spec_file(108)
        assert spec_path is not None
        assert spec_path.exists()
        assert "SPEC-108" in spec_path.name or "SPEC-108" in str(spec_path)

    def test_find_spec_file_nonexistent(self):
        """Test finding non-existent spec file."""
        spec_path = self.module.find_spec_file(9999)
        assert spec_path is None
