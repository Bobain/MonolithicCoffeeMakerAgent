"""
Test suite for Code Index infrastructure (indexer and query engine).

Tests the 3-level hierarchical code index used by all skills.
"""

import json
import tempfile
from pathlib import Path

import pytest

from coffee_maker.skills.code_index.indexer import CodeIndexer
from coffee_maker.skills.code_index.query_engine import CodeIndexQueryEngine


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create some test Python files
        (tmpdir / "auth").mkdir()
        (tmpdir / "auth" / "jwt.py").write_text(
            """
'''JWT authentication module'''
import jwt
import cryptography

def validate_jwt(token):
    '''Validate JWT token'''
    try:
        payload = jwt.decode(token, 'secret')
        return payload
    except Exception:
        raise ValueError("Invalid token")

class JWTValidator:
    '''Validates JWT tokens'''
    pass
"""
        )

        (tmpdir / "auth" / "oauth.py").write_text(
            """
'''OAuth authentication module'''
import requests

def validate_oauth(token):
    '''Validate OAuth token'''
    pass
"""
        )

        (tmpdir / "database").mkdir()
        (tmpdir / "database" / "models.py").write_text(
            """
'''Database models'''
from sqlalchemy import Column, String

class User:
    '''User model'''
    name = Column(String)
"""
        )

        yield tmpdir


class TestCodeIndexer:
    """Test CodeIndexer functionality."""

    def test_indexer_init(self, temp_codebase):
        """Test indexer initialization."""
        indexer = CodeIndexer(str(temp_codebase))
        assert indexer.codebase_root == temp_codebase
        assert indexer.index == {"categories": {}, "metadata": {}}

    def test_find_python_files(self, temp_codebase):
        """Test finding Python files."""
        indexer = CodeIndexer(str(temp_codebase))
        files = indexer._find_python_files()

        assert len(files) == 3
        file_names = [f.name for f in files]
        assert "jwt.py" in file_names
        assert "oauth.py" in file_names
        assert "models.py" in file_names

    def test_categorize_file(self, temp_codebase):
        """Test file categorization."""
        indexer = CodeIndexer(str(temp_codebase))
        jwt_file = temp_codebase / "auth" / "jwt.py"
        with open(jwt_file) as f:
            content = f.read()

        categories = indexer._categorize_file(jwt_file, content)
        assert "Authentication" in categories

    def test_extract_definitions(self, temp_codebase):
        """Test extracting function and class definitions."""
        import ast

        indexer = CodeIndexer(str(temp_codebase))
        jwt_file = temp_codebase / "auth" / "jwt.py"
        with open(jwt_file) as f:
            content = f.read()

        tree = ast.parse(content)
        definitions = indexer._extract_definitions(tree, content, jwt_file)

        # Should have validate_jwt function and JWTValidator class
        names = [d["name"] for d in definitions]
        assert "validate_jwt" in names
        assert "JWTValidator" in names

    def test_rebuild_index(self, temp_codebase):
        """Test index rebuild."""
        indexer = CodeIndexer(str(temp_codebase))
        indexer.rebuild_index()

        assert len(indexer.index["categories"]) > 0
        assert "Authentication" in indexer.index["categories"]
        assert "Database" in indexer.index["categories"]

    def test_save_and_load_index(self, temp_codebase):
        """Test saving and loading index."""
        index_dir = temp_codebase / "data" / "code_index"
        index_dir.mkdir(parents=True)

        indexer = CodeIndexer(str(temp_codebase))
        indexer.rebuild_index()
        indexer.save_index()

        assert indexer.index_path.exists()

        # Load and verify
        with open(indexer.index_path) as f:
            loaded = json.load(f)

        assert loaded["categories"]


class TestCodeIndexQueryEngine:
    """Test CodeIndexQueryEngine functionality."""

    @pytest.fixture
    def query_engine(self, temp_codebase):
        """Create and populate query engine."""
        indexer = CodeIndexer(str(temp_codebase))
        indexer.rebuild_index()

        index_dir = temp_codebase / "data" / "code_index"
        index_dir.mkdir(parents=True)
        indexer.save_index()

        return CodeIndexQueryEngine(str(indexer.index_path))

    def test_query_engine_init(self, query_engine):
        """Test query engine initialization."""
        assert query_engine.index is not None

    def test_functional_search(self, query_engine):
        """Test functional search."""
        results = query_engine.functional_search("authentication")

        assert "results" in results
        assert len(results["results"]) > 0

    def test_find_implementations(self, query_engine):
        """Test finding implementations by category."""
        impls = query_engine.find_implementations("Authentication")
        assert isinstance(impls, list)

    def test_get_categories(self, query_engine):
        """Test getting available categories."""
        categories = query_engine.get_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_get_statistics(self, query_engine):
        """Test getting index statistics."""
        stats = query_engine.get_statistics()

        assert "total_categories" in stats
        assert "total_components" in stats
        assert "total_implementations" in stats

    def test_search_by_pattern(self, query_engine):
        """Test pattern-based search."""
        results = query_engine.search_by_pattern("validate", regex=False)

        assert isinstance(results, dict)

    def test_get_related_files(self, query_engine):
        """Test finding related files."""
        # This test depends on the index structure
        related = query_engine.get_related_files("coffee_maker/auth/jwt.py")
        assert isinstance(related, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
