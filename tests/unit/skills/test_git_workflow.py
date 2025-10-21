"""Unit tests for git workflow automation skills."""

import pytest
from unittest.mock import MagicMock, patch

from coffee_maker.skills.git_workflow.commit_generator import (
    CommitMessageGenerator,
    CommitMessage,
)
from coffee_maker.skills.git_workflow.semantic_versioner import (
    SemanticVersioner,
)
from coffee_maker.skills.git_workflow.pr_creator import (
    PullRequestCreator,
)


class TestCommitMessageGenerator:
    """Test conventional commit message generation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create commit message generator with temp repo."""
        return CommitMessageGenerator(repo_path=tmp_path)

    def test_detect_feat_commit_type(self, generator):
        """Test feat commit type detection from new files."""
        changed_files = [
            "coffee_maker/api/new_feature.py",
            "tests/test_new_feature.py",
        ]

        commit_type = generator._detect_commit_type(changed_files)
        assert commit_type == "feat"

    def test_detect_docs_commit_type(self, generator):
        """Test docs commit type detection."""
        changed_files = ["docs/README.md", "docs/API.md"]

        commit_type = generator._detect_commit_type(changed_files)
        assert commit_type == "docs"

    def test_detect_test_commit_type(self, generator):
        """Test test commit type detection."""
        changed_files = ["tests/unit/test_feature.py"]

        commit_type = generator._detect_commit_type(changed_files)
        assert commit_type == "test"

    def test_detect_scope_from_files(self, generator):
        """Test scope detection from file paths."""
        # API scope
        files = ["coffee_maker/api/routes.py"]
        scope = generator._detect_scope(files)
        assert scope == "api"

        # Daemon scope
        files = ["coffee_maker/autonomous/daemon.py"]
        scope = generator._detect_scope(files)
        assert scope == "daemon"

        # Skills scope
        files = ["coffee_maker/skills/git_workflow/commit_generator.py"]
        scope = generator._detect_scope(files)
        assert scope == "skills"

    def test_generate_subject_with_priority(self, generator):
        """Test subject generation with priority."""
        changed_files = ["coffee_maker/api/pagination.py"]
        subject = generator._generate_subject(
            "feat",
            changed_files,
            "US-067",
            "Implement git workflow automation",
        )

        assert "US-067" in subject or "git workflow" in subject.lower()

    def test_generate_body_with_file_summary(self, generator):
        """Test body generation with file change summary."""
        changed_files = [
            "coffee_maker/api/routes.py",
            "coffee_maker/api/schemas.py",
            "tests/test_api.py",
            "docs/API.md",
        ]
        diff_stats = {"files_changed": 4, "insertions": 120, "deletions": 30}

        body = generator._generate_body(
            changed_files,
            diff_stats,
            "US-067",
            "Implement feature",
        )

        assert "Implementation:" in body or "implementation" in body.lower()
        assert "Tests:" in body or "test" in body.lower()
        assert "Documentation:" in body or "documentation" in body.lower()
        assert "120" in body  # Insertions
        assert "30" in body  # Deletions

    def test_generate_footer_with_priority(self, generator):
        """Test footer generation with priority reference."""
        footer = generator._generate_footer("US-067")

        assert "US-067" in footer
        assert "Claude Code" in footer
        assert "Co-Authored-By" in footer

    def test_commit_message_format(self):
        """Test commit message formatting."""
        commit = CommitMessage(
            type="feat",
            scope="api",
            subject="Add pagination support",
            body="- Implement offset/limit\n- Add tests",
            footer="Implements: US-067\n\n🤖 Generated with Claude Code",
        )

        formatted = commit.format()

        assert formatted.startswith("feat(api): Add pagination support")
        assert "Implement offset/limit" in formatted
        assert "US-067" in formatted
        assert "🤖" in formatted

    @patch("subprocess.run")
    def test_generate_full_commit_message(self, mock_run, generator):
        """Test full commit message generation."""
        # Mock git diff --name-only
        mock_run.return_value = MagicMock(
            stdout="coffee_maker/api/routes.py\ntests/test_api.py\n",
            returncode=0,
        )

        commit = generator.generate(
            priority_name="US-067",
            priority_description="Add git workflow automation",
            staged_only=True,
        )

        assert commit.type in ["feat", "fix", "refactor", "docs", "test"]
        assert commit.subject
        assert commit.footer


class TestSemanticVersioner:
    """Test semantic versioning and tagging."""

    @pytest.fixture
    def versioner(self, tmp_path):
        """Create semantic versioner with temp repo."""
        return SemanticVersioner(repo_path=tmp_path)

    def test_bump_version_patch(self, versioner):
        """Test patch version bump."""
        new_version = versioner._bump_version("1.2.3", "patch")
        assert new_version == "1.2.4"

    def test_bump_version_minor(self, versioner):
        """Test minor version bump."""
        new_version = versioner._bump_version("1.2.3", "minor")
        assert new_version == "1.3.0"

    def test_bump_version_major(self, versioner):
        """Test major version bump."""
        new_version = versioner._bump_version("1.2.3", "major")
        assert new_version == "2.0.0"

    def test_analyze_commits_for_feat(self, versioner):
        """Test commit analysis detects feat for minor bump."""
        commits = [
            "feat(api): Add new endpoint",
            "fix(auth): Fix login bug",
            "refactor(daemon): Clean up code",
        ]

        bump_type = versioner._analyze_commits_for_bump(commits)
        assert bump_type == "minor"  # feat triggers minor bump

    def test_analyze_commits_for_fix(self, versioner):
        """Test commit analysis detects fix for patch bump."""
        commits = [
            "fix(api): Fix validation",
            "refactor(utils): Clean up",
        ]

        bump_type = versioner._analyze_commits_for_bump(commits)
        assert bump_type == "patch"  # Only fix triggers patch bump

    def test_analyze_commits_for_breaking(self, versioner):
        """Test commit analysis detects breaking change for major bump."""
        commits = [
            "feat(api)!: Change API response format",
            "BREAKING CHANGE: Remove deprecated endpoint",
        ]

        bump_type = versioner._analyze_commits_for_bump(commits)
        assert bump_type == "major"  # Breaking change triggers major bump

    def test_get_bump_reason(self, versioner):
        """Test bump reason generation."""
        commits = [
            "feat(api): Add pagination",
            "feat(auth): Add JWT",
            "fix(daemon): Fix crash",
        ]

        reason = versioner._get_bump_reason(commits, "minor")

        assert "2 new feature(s)" in reason.lower() or "2 new feature" in reason
        assert "1 bug fix" in reason.lower() or "1 bug fix" in reason

    def test_generate_wip_tag_message(self, versioner):
        """Test WIP tag message generation."""
        message = versioner._generate_tag_message("wip", "us-067", None)

        assert "Work in Progress" in message or "wip" in message.lower()
        assert "us-067" in message
        assert "🤖" in message

    def test_generate_dod_verified_tag_message(self, versioner):
        """Test DoD verified tag message generation."""
        message = versioner._generate_tag_message("dod-verified", "us-067", None)

        assert "DoD" in message or "verified" in message.lower()
        assert "us-067" in message

    def test_generate_stable_tag_message(self, versioner):
        """Test stable release tag message generation."""
        message = versioner._generate_tag_message("stable", "1.3.0", "1.3.0")

        assert "1.3.0" in message
        assert "Release" in message or "release" in message.lower()

    @patch("subprocess.run")
    def test_get_latest_stable_version(self, mock_run, versioner):
        """Test getting latest stable version from tags."""
        # Mock git tag -l stable-v*
        mock_run.return_value = MagicMock(
            stdout="stable-v1.0.0\nstable-v1.2.3\nstable-v1.1.5\n",
            returncode=0,
        )

        version = versioner._get_latest_stable_version()
        assert version == "1.2.3"  # Should return highest version

    @patch("subprocess.run")
    def test_calculate_version_bump_from_commits(self, mock_run, versioner):
        """Test version bump calculation from commits."""
        # Mock git tag check
        mock_run.side_effect = [
            MagicMock(stdout="stable-v1.2.3\n", returncode=0),  # Latest version
            MagicMock(returncode=0),  # Tag exists check
            MagicMock(
                stdout="feat(api): Add feature\nfix(auth): Fix bug\n",
                returncode=0,
            ),  # Commits
        ]

        bump = versioner.calculate_version_bump()

        assert bump.current_version == "1.2.3"
        assert bump.new_version == "1.3.0"  # Minor bump due to feat
        assert bump.bump_type == "minor"


class TestPullRequestCreator:
    """Test pull request creation."""

    @pytest.fixture
    def pr_creator(self, tmp_path):
        """Create PR creator with temp repo."""
        return PullRequestCreator(repo_path=tmp_path)

    @patch("subprocess.run")
    def test_get_commits_between_branches(self, mock_run, pr_creator):
        """Test getting commits between branches."""
        mock_run.return_value = MagicMock(
            stdout="abc1234 feat(api): Add feature\ndef5678 fix(auth): Fix bug\n",
            returncode=0,
        )

        commits = pr_creator._get_commits_between("main", "roadmap")

        assert len(commits) == 2
        # Commits include the hash, so check for substring
        assert any("feat(api): Add feature" in c for c in commits)
        assert any("fix(auth): Fix bug" in c for c in commits)

    @patch("subprocess.run")
    def test_get_changed_files_between_branches(self, mock_run, pr_creator):
        """Test getting changed files between branches."""
        mock_run.return_value = MagicMock(
            stdout="coffee_maker/api/routes.py\ntests/test_api.py\ndocs/API.md\n",
            returncode=0,
        )

        files = pr_creator._get_changed_files_between("main", "roadmap")

        assert len(files) == 3
        assert "coffee_maker/api/routes.py" in files
        assert "tests/test_api.py" in files
        assert "docs/API.md" in files

    def test_generate_pr_body_structure(self, pr_creator):
        """Test PR body structure and sections."""
        with patch.object(pr_creator, "_get_commits_between", return_value=["feat(api): Add feature"]):
            with patch.object(
                pr_creator,
                "_get_changed_files_between",
                return_value=["coffee_maker/api/routes.py", "tests/test_api.py"],
            ):
                body = pr_creator._generate_pr_body(
                    title="Add API feature",
                    priority_name="US-067",
                    priority_description="Implement git workflow automation",
                    dod_report_path=None,
                    base_branch="main",
                    head_branch="roadmap",
                )

                # Check for required sections
                assert "## Summary" in body
                assert "## Changes" in body
                assert "## Test Results" in body
                assert "## DoD Verification" in body
                assert "US-067" in body
                assert "🤖" in body

    def test_generate_pr_body_with_dod_report(self, pr_creator):
        """Test PR body includes DoD report when provided."""
        with patch.object(pr_creator, "_get_commits_between", return_value=[]):
            with patch.object(pr_creator, "_get_changed_files_between", return_value=[]):
                body = pr_creator._generate_pr_body(
                    title="Test PR",
                    priority_name="US-067",
                    priority_description="Test",
                    dod_report_path="data/dod_reports/US-067_dod.md",
                    base_branch="main",
                    head_branch="roadmap",
                )

                assert "DoD Verification" in body
                assert "✅ PASS" in body
                assert "US-067_dod.md" in body

    @patch("subprocess.run")
    def test_create_github_pr_success(self, mock_run, pr_creator):
        """Test successful PR creation via gh CLI."""
        mock_run.return_value = MagicMock(
            stdout="https://github.com/owner/repo/pull/123\n",
            returncode=0,
        )

        pr_number, pr_url, created = pr_creator._create_github_pr(
            title="Test PR",
            body="Test body",
            base_branch="main",
            head_branch="roadmap",
        )

        assert created is True
        assert pr_number == 123
        assert pr_url == "https://github.com/owner/repo/pull/123"

    @patch("subprocess.run")
    def test_create_github_pr_failure(self, mock_run, pr_creator):
        """Test PR creation failure handling."""
        mock_run.side_effect = Exception("gh CLI error")

        pr_number, pr_url, created = pr_creator._create_github_pr(
            title="Test PR",
            body="Test body",
            base_branch="main",
            head_branch="roadmap",
        )

        assert created is False
        assert pr_number == 0
        assert pr_url == ""


class TestIntegration:
    """Integration tests for git workflow skills."""

    @pytest.fixture
    def temp_git_repo(self, tmp_path):
        """Create a temporary git repository."""
        import subprocess

        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
        )

        # Create initial commit
        test_file = repo_path / "README.md"
        test_file.write_text("# Test Repo")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
        )

        return repo_path

    def test_full_workflow_integration(self, temp_git_repo):
        """Test complete git workflow: commit -> tag -> (PR would require gh)."""
        # Step 1: Make changes
        feature_file = temp_git_repo / "feature.py"
        feature_file.write_text("def new_feature(): pass")

        import subprocess

        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)

        # Step 2: Generate conventional commit
        generator = CommitMessageGenerator(repo_path=temp_git_repo)
        commit_msg = generator.generate(
            priority_name="US-067",
            priority_description="Add git workflow automation",
            staged_only=True,
        )

        assert commit_msg.type in ["feat", "fix", "docs", "test", "refactor"]
        assert "US-067" in commit_msg.footer

        # Step 3: Create commit
        formatted_msg = commit_msg.format()
        subprocess.run(
            ["git", "commit", "-m", formatted_msg],
            cwd=temp_git_repo,
            check=True,
        )

        # Step 4: Create version tag
        versioner = SemanticVersioner(repo_path=temp_git_repo)

        # Use auto-generated message (which includes the name)
        tag = versioner.create_tag(
            tag_type="wip",
            name="us-067",
        )

        assert tag.created is True
        assert tag.tag_name == "wip-us-067"
        # The auto-generated message should include the name
        assert "us-067" in tag.message or "Work in Progress" in tag.message

        # Verify tag was created
        result = subprocess.run(
            ["git", "tag", "-l"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert "wip-us-067" in result.stdout
