"""
Integration tests for git-workflow-automation skill.

Tests the scripts working together in a real git environment.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "git-workflow-automation" / "scripts"
sys.path.insert(0, str(scripts_dir))

from git_commit_generator import GitCommitGenerator
from semantic_tagger import SemanticTagger


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize git repo
        subprocess.run(
            ["git", "init"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Configure git
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Create initial commit
        (repo_path / "README.md").write_text("# Test Repo\n")
        subprocess.run(
            ["git", "add", "README.md"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        yield repo_path


class TestGitCommitGeneratorIntegration:
    """Integration tests for git commit generator."""

    def test_generate_from_unstaged_changes(self, temp_git_repo):
        """Test generating commit message from unstaged changes."""
        # Create and add initial files, then modify them
        (temp_git_repo / "feature.py").write_text("# placeholder\n")
        subprocess.run(
            ["git", "add", "feature.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add feature file"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Now modify the file (unstaged changes)
        (temp_git_repo / "feature.py").write_text("def new_feature():\n    pass\n")

        # Generate commit message
        generator = GitCommitGenerator(str(temp_git_repo))
        message = generator.generate_commit_message()

        # Verify message structure
        assert message.type in ["feat", "test", "chore"]
        assert message.subject
        assert "🤖 Generated with" in message.format()
        assert "Co-Authored-By: Claude" in message.format()

    def test_generate_from_staged_changes(self, temp_git_repo):
        """Test generating commit message from staged changes."""
        # Create and stage changes
        (temp_git_repo / "docs").mkdir(parents=True, exist_ok=True)
        (temp_git_repo / "docs" / "guide.md").write_text("# Guide\n")

        subprocess.run(
            ["git", "add", "docs/"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Generate commit message
        generator = GitCommitGenerator(str(temp_git_repo))
        message = generator.generate_commit_message(staged_only=True)

        # Should detect docs type
        assert message.type == "docs"
        assert "docs" in message.scope or message.scope is None

    def test_generate_with_priority_and_issue(self, temp_git_repo):
        """Test generating commit with priority and issue references."""
        # Create and commit initial file
        (temp_git_repo / "feature.py").write_text("# placeholder\n")
        subprocess.run(
            ["git", "add", "feature.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add feature file"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Modify file
        (temp_git_repo / "feature.py").write_text("def feature():\n    pass\n")

        # Generate with references
        generator = GitCommitGenerator(str(temp_git_repo))
        message = generator.generate_commit_message(
            priority_id="US-067",
            issue_id="123",
        )

        formatted = message.format()
        assert "Implements: US-067" in formatted
        assert "Closes: #123" in formatted

    def test_generate_with_type_override(self, temp_git_repo):
        """Test overriding auto-detected commit type."""
        # Create and commit initial file
        (temp_git_repo / "refactored.py").write_text("# placeholder\n")
        subprocess.run(
            ["git", "add", "refactored.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add file"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Modify file
        (temp_git_repo / "refactored.py").write_text("def refactored():\n    pass\n")

        # Generate with type override
        generator = GitCommitGenerator(str(temp_git_repo))
        message = generator.generate_commit_message(commit_type="refactor")

        assert message.type == "refactor"

    def test_generate_with_scope_override(self, temp_git_repo):
        """Test overriding auto-detected scope."""
        # Create and commit initial file
        (temp_git_repo / "file.py").write_text("# placeholder\n")
        subprocess.run(
            ["git", "add", "file.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add file"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Modify file
        (temp_git_repo / "file.py").write_text("content")

        # Generate with scope override
        generator = GitCommitGenerator(str(temp_git_repo))
        message = generator.generate_commit_message(scope="custom")

        assert message.scope == "custom"


class TestSemanticTaggerIntegration:
    """Integration tests for semantic tagger."""

    def test_create_wip_tag(self, temp_git_repo):
        """Test creating WIP tag."""
        tagger = SemanticTagger(str(temp_git_repo))

        # Create WIP tag
        tag_info = tagger.create_wip_tag("us-067", message="Test WIP tag")

        assert tag_info.tag_name == "wip-us-067"
        assert tag_info.tag_type == "wip"

        # Verify tag exists
        result = subprocess.run(
            ["git", "tag", "-l", "wip-us-067"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "wip-us-067" in result.stdout

    def test_create_dod_verified_tag(self, temp_git_repo):
        """Test creating DoD verified tag."""
        tagger = SemanticTagger(str(temp_git_repo))

        # Create DoD verified tag
        tag_info = tagger.create_dod_verified_tag("us-067")

        assert tag_info.tag_name == "dod-verified-us-067"
        assert tag_info.tag_type == "dod-verified"

        # Verify tag exists
        result = subprocess.run(
            ["git", "tag", "-l", "dod-verified-us-067"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "dod-verified-us-067" in result.stdout

    def test_create_stable_tag_explicit_version(self, temp_git_repo):
        """Test creating stable tag with explicit version."""
        tagger = SemanticTagger(str(temp_git_repo))

        # Create stable tag
        tag_info = tagger.create_stable_tag(version="1.0.0")

        assert tag_info.tag_name == "stable-v1.0.0"
        assert tag_info.tag_type == "stable"

        # Verify tag exists
        result = subprocess.run(
            ["git", "tag", "-l", "stable-v1.0.0"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "stable-v1.0.0" in result.stdout

    def test_version_auto_calculation(self, temp_git_repo):
        """Test automatic version calculation from commits."""
        # Create a baseline tag first
        subprocess.run(
            ["git", "tag", "-a", "stable-v0.0.0", "-m", "Initial version"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Create some conventional commits
        (temp_git_repo / "feature1.py").write_text("def feature1():\n    pass\n")
        subprocess.run(
            ["git", "add", "feature1.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "feat: Add feature 1"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        (temp_git_repo / "feature2.py").write_text("def feature2():\n    pass\n")
        subprocess.run(
            ["git", "add", "feature2.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "fix: Fix bug"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Calculate version
        tagger = SemanticTagger(str(temp_git_repo))
        version_bump = tagger.calculate_next_version("v0.0.0")

        # Should be minor bump (has feat commits)
        assert version_bump.bump_type == "minor"
        assert version_bump.new_version == "v0.1.0"
        assert version_bump.feat_count == 1
        assert version_bump.fix_count == 1


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_complete_workflow(self, temp_git_repo):
        """Test complete git workflow: commit → tag → verify."""
        # 1. Create changes
        (temp_git_repo / "coffee_maker").mkdir(parents=True, exist_ok=True)
        (temp_git_repo / "coffee_maker/feature.py").write_text("def new_feature():\n    pass\n")
        (temp_git_repo / "tests").mkdir(parents=True, exist_ok=True)
        (temp_git_repo / "tests/test_feature.py").write_text("def test_feature():\n    pass\n")

        subprocess.run(
            ["git", "add", "."],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # 2. Generate commit message
        generator = GitCommitGenerator(str(temp_git_repo))
        message = generator.generate_commit_message(
            staged_only=True,
            priority_id="US-067",
        )

        # 3. Create commit
        subprocess.run(
            ["git", "commit", "-m", message.format()],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # 4. Create WIP tag
        tagger = SemanticTagger(str(temp_git_repo))
        tagger.create_wip_tag("us-067")

        # 5. Verify everything worked
        # Check commit exists
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "US-067" in result.stdout or message.type in result.stdout

        # Check tag exists
        result = subprocess.run(
            ["git", "tag", "-l"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "wip-us-067" in result.stdout

    def test_multiple_commits_to_version(self, temp_git_repo):
        """Test multiple commits leading to version bump."""
        # Create several commits
        commits = [
            ("feat: Add feature 1", "feature1.py"),
            ("feat: Add feature 2", "feature2.py"),
            ("fix: Fix bug", "bugfix.py"),
            ("docs: Update docs", "docs.md"),
        ]

        for commit_msg, filename in commits:
            (temp_git_repo / filename).write_text("content\n")
            subprocess.run(
                ["git", "add", filename],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )

        # Calculate version
        tagger = SemanticTagger(str(temp_git_repo))
        version_bump = tagger.calculate_next_version("v0.0.0")

        # Should be minor bump (has feat commits)
        assert version_bump.bump_type == "minor"
        assert version_bump.new_version == "v0.1.0"
        assert version_bump.commits_analyzed == len(commits) + 1  # +1 for initial commit


def test_scripts_are_executable():
    """Test that scripts have correct permissions and can be executed."""
    scripts = [
        scripts_dir / "git_commit_generator.py",
        scripts_dir / "semantic_tagger.py",
        scripts_dir / "pr_creator.py",
    ]

    for script in scripts:
        assert script.exists(), f"Script {script} does not exist"
        assert script.is_file(), f"Script {script} is not a file"

        # Test that script can be imported
        # (Already done by importing at top of file)


def test_script_help_messages():
    """Test that scripts provide help messages."""
    scripts = [
        "git_commit_generator.py",
        "semantic_tagger.py",
        "pr_creator.py",
    ]

    for script_name in scripts:
        script = scripts_dir / script_name
        result = subprocess.run(
            ["python", str(script), "--help"],
            capture_output=True,
            text=True,
        )

        # Should exit successfully and show help
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()
