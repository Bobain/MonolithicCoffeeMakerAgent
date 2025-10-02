"""
Integration tests for GitHub API authentication and PR operations.

These tests verify real GitHub credentials and API functionality.
They are marked as integration tests and require valid GITHUB_TOKEN.
"""

import os
import pytest
from dotenv import load_dotenv
from github import Github, Auth
from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI

# Load environment variables from .env file
load_dotenv()


@pytest.mark.integration
class TestGitHubIntegration:
    """Integration tests for GitHub API operations."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Verify GITHUB_TOKEN is available."""
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            pytest.skip("GITHUB_TOKEN environment variable not set")

    def test_github_authentication(self):
        """Test that we can authenticate with GitHub using current credentials."""
        auth = Auth.Token(self.token)
        g = Github(auth=auth)

        # Verify authentication by getting the authenticated user
        user = g.get_user()
        assert user is not None
        assert user.login is not None
        print(f"✓ Successfully authenticated as: {user.login}")

    def test_github_repo_access(self):
        """Test that we can access a repository."""
        auth = Auth.Token(self.token)
        g = Github(auth=auth)

        # Use the current repository from git status
        repo_name = "Bobain/MonolithicCoffeeMakerAgent"
        repo = g.get_repo(repo_name)

        assert repo is not None
        assert repo.full_name == repo_name
        print(f"✓ Successfully accessed repository: {repo.full_name}")

    def test_github_pr_access(self):
        """Test that we can access a pull request."""
        auth = Auth.Token(self.token)
        g = Github(auth=auth)

        repo_name = "Bobain/MonolithicCoffeeMakerAgent"
        repo = g.get_repo(repo_name)

        # Get the list of PRs to find an open one
        prs = list(repo.get_pulls(state="open"))

        if not prs:
            pytest.skip("No open pull requests available for testing")

        pr = prs[0]
        assert pr is not None
        assert pr.number > 0
        print(f"✓ Successfully accessed PR #{pr.number}: {pr.title}")

    @pytest.mark.skip(reason="This test will post a real comment - enable manually when needed")
    def test_post_pr_suggestion(self):
        """
        Test posting a code suggestion to a PR.

        WARNING: This test posts a REAL comment to a PR.
        Only enable this test when you want to actually post a comment.
        """
        auth = Auth.Token(self.token)
        g = Github(auth=auth)

        repo_name = "Bobain/MonolithicCoffeeMakerAgent"
        repo = g.get_repo(repo_name)

        # Get the first open PR
        prs = list(repo.get_pulls(state="open"))
        if not prs:
            pytest.skip("No open pull requests available for testing")

        pr = prs[0]

        # Get the first file from the PR
        files = list(pr.get_files())
        if not files:
            pytest.skip("No files in the pull request")

        test_file = files[0]

        # Use the PostSuggestionToolLangAI to post a test suggestion
        tool = PostSuggestionToolLangAI()

        result = tool._run(
            repo_full_name=repo_name,
            pr_number=pr.number,
            file_path=test_file.filename,
            start_line=1,
            end_line=1,
            suggestion_body="# Test suggestion from integration test",
            comment_text="🧪 This is a test comment from the integration test suite.",
        )

        assert "Successfully posted suggestion" in result
        print(f"✓ Successfully posted suggestion to PR #{pr.number}")


@pytest.mark.integration
class TestGitHubPermissions:
    """Test specific GitHub API permissions needed for the code formatter."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup GitHub client."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN environment variable not set")
        auth = Auth.Token(token)
        self.github = Github(auth=auth)

    def test_can_read_pr_files(self):
        """Test that we can read files from a PR."""
        repo = self.github.get_repo("Bobain/MonolithicCoffeeMakerAgent")
        prs = list(repo.get_pulls(state="open"))

        if not prs:
            pytest.skip("No open pull requests available")

        pr = prs[0]
        files = list(pr.get_files())

        assert len(files) > 0
        first_file = files[0]
        assert first_file.filename is not None
        print(f"✓ Can read PR files. Found {len(files)} files in PR #{pr.number}")

    def test_can_read_file_content(self):
        """Test that we can read file content from a PR's head commit."""
        repo = self.github.get_repo("Bobain/MonolithicCoffeeMakerAgent")
        prs = list(repo.get_pulls(state="open"))

        if not prs:
            pytest.skip("No open pull requests available")

        pr = prs[0]
        files = list(pr.get_files())

        if not files:
            pytest.skip("No files in PR")

        # Try to find a file with content (skip empty files)
        content = None
        test_file = None
        for f in files:
            try:
                contents = repo.get_contents(f.filename, ref=pr.head.sha)
                decoded = contents.decoded_content.decode("utf-8")
                if len(decoded) > 0:
                    content = decoded
                    test_file = f
                    break
            except Exception:
                continue

        if content is None:
            pytest.skip("No files with content found in PR")

        assert content is not None
        assert len(content) > 0
        print(f"✓ Can read file content. Read {len(content)} bytes from {test_file.filename}")

    def test_can_get_pr_commits(self):
        """Test that we can get commits from a PR."""
        repo = self.github.get_repo("Bobain/MonolithicCoffeeMakerAgent")
        prs = list(repo.get_pulls(state="open"))

        if not prs:
            pytest.skip("No open pull requests available")

        pr = prs[0]
        commits = list(pr.get_commits())

        assert len(commits) > 0
        latest_commit = commits[-1]
        assert latest_commit.sha is not None
        print(f"✓ Can access PR commits. Found {len(commits)} commits, latest: {latest_commit.sha[:8]}")
