"""Code Navigation Skill - Fast codebase navigation and symbol lookup.

Provides efficient navigation for exploring codebases, finding definitions,
locating usages, and understanding code structure.

Author: assistant
Date: 2025-10-19
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CodeNavigationSkill:
    """Intelligent codebase navigation and symbol lookup."""

    def __init__(self, repo_root: Path = None):
        """Initialize code navigation skill.

        Args:
            repo_root: Repository root directory (default: current directory)
        """
        self.repo_root = repo_root or Path.cwd()

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a navigation action.

        Args:
            action: Action to perform
            **kwargs: Action-specific parameters

        Returns:
            Dict with results
        """
        try:
            if action == "find_file":
                return self._find_file(kwargs.get("query"), kwargs.get("file_pattern", "*.py"))

            elif action == "find_symbol":
                return self._find_symbol(kwargs.get("query"), kwargs.get("file_pattern", "*.py"))

            elif action == "get_definition":
                return self._get_definition(kwargs.get("query"), kwargs.get("file"))

            elif action == "find_references":
                return self._find_references(kwargs.get("query"), kwargs.get("file_pattern", "*.py"))

            elif action == "analyze_file":
                return self._analyze_file(kwargs.get("file"))

            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Error in code navigation: {e}", exc_info=True)
            return {"error": str(e)}

    def _find_file(self, query: str, file_pattern: str) -> Dict[str, Any]:
        """Find files matching query pattern.

        Args:
            query: File name or pattern to search for
            file_pattern: Glob pattern (default: *.py)

        Returns:
            Dict with matched files and scores
        """
        results = []

        # Search in common directories
        search_dirs = [
            self.repo_root / "coffee_maker",
            self.repo_root / "tests",
            self.repo_root / ".claude",
            self.repo_root / "docs",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for file_path in search_dir.rglob(file_pattern):
                if file_path.is_file():
                    # Score based on name match
                    score = self._score_file_match(file_path.name, query)
                    if score > 0:
                        results.append({"path": str(file_path.relative_to(self.repo_root)), "score": score})

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        return {"files": results[:20], "count": len(results)}

    def _find_symbol(self, query: str, file_pattern: str) -> Dict[str, Any]:
        """Find symbol (class, function) by name.

        Args:
            query: Symbol name to search for
            file_pattern: Glob pattern (default: *.py)

        Returns:
            Dict with symbol locations
        """
        symbols = []

        # Search Python files
        for py_file in self.repo_root.rglob(file_pattern):
            if not py_file.is_file() or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and query.lower() in node.name.lower():
                        symbols.append(
                            {
                                "name": node.name,
                                "type": "class",
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": node.lineno,
                                "signature": f"class {node.name}",
                            }
                        )

                    elif isinstance(node, ast.FunctionDef) and query.lower() in node.name.lower():
                        args = [arg.arg for arg in node.args.args]
                        symbols.append(
                            {
                                "name": node.name,
                                "type": "function",
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": node.lineno,
                                "signature": f"def {node.name}({', '.join(args)})",
                            }
                        )

            except Exception as e:
                logger.debug(f"Error parsing {py_file}: {e}")
                continue

        return {"symbols": symbols[:50], "count": len(symbols)}

    def _get_definition(self, query: str, file: str = None) -> Dict[str, Any]:
        """Get definition of a symbol.

        Args:
            query: Symbol name
            file: File path (optional, searches all if not provided)

        Returns:
            Dict with definition details
        """
        if file:
            # Search in specific file
            file_path = self.repo_root / file
            if file_path.exists():
                return self._extract_definition_from_file(file_path, query)

        # Search all Python files
        for py_file in self.repo_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            result = self._extract_definition_from_file(py_file, query)
            if result.get("definition"):
                return result

        return {"definition": None, "error": f"Definition not found for: {query}"}

    def _extract_definition_from_file(self, file_path: Path, query: str) -> Dict[str, Any]:
        """Extract definition from a specific file.

        Args:
            file_path: Path to file
            query: Symbol name

        Returns:
            Dict with definition or None
        """
        try:
            content = file_path.read_text()
            lines = content.split("\n")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == query:
                    # Get signature
                    signature_line = lines[node.lineno - 1].strip()

                    # Get docstring
                    docstring = ast.get_docstring(node) or ""

                    return {
                        "definition": {
                            "name": node.name,
                            "type": "class" if isinstance(node, ast.ClassDef) else "function",
                            "file": str(file_path.relative_to(self.repo_root)),
                            "line": node.lineno,
                            "signature": signature_line,
                            "docstring": docstring[:200] if docstring else "",
                        }
                    }

        except Exception as e:
            logger.debug(f"Error extracting from {file_path}: {e}")

        return {"definition": None}

    def _find_references(self, query: str, file_pattern: str) -> Dict[str, Any]:
        """Find all references to a symbol.

        Args:
            query: Symbol name
            file_pattern: Glob pattern (default: *.py)

        Returns:
            Dict with reference locations
        """
        references = []

        # Use regex to find usages
        pattern = re.compile(rf"\b{re.escape(query)}\b")

        for py_file in self.repo_root.rglob(file_pattern):
            if not py_file.is_file() or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, start=1):
                    if pattern.search(line):
                        references.append(
                            {
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": line_num,
                                "context": line.strip()[:100],
                            }
                        )

            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
                continue

        return {"references": references[:100], "count": len(references)}

    def _analyze_file(self, file: str) -> Dict[str, Any]:
        """Analyze file structure.

        Args:
            file: File path to analyze

        Returns:
            Dict with file structure details
        """
        file_path = self.repo_root / file

        if not file_path.exists():
            return {"error": f"File not found: {file}"}

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            imports = []
            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))

                elif isinstance(node, ast.ClassDef):
                    methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    classes.append({"name": node.name, "line": node.lineno, "methods": methods})

                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if node.col_offset == 0:
                        args = [arg.arg for arg in node.args.args]
                        functions.append(
                            {
                                "name": node.name,
                                "line": node.lineno,
                                "signature": f"def {node.name}({', '.join(args)})",
                            }
                        )

            return {
                "structure": {
                    "imports": imports[:20],
                    "classes": classes,
                    "functions": functions,
                    "lines": len(content.split("\n")),
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}", exc_info=True)
            return {"error": str(e)}

    def _score_file_match(self, filename: str, query: str) -> int:
        """Score how well a filename matches query.

        Args:
            filename: File name
            query: Search query

        Returns:
            Score (0-100)
        """
        filename_lower = filename.lower()
        query_lower = query.lower()

        # Exact match
        if filename_lower == query_lower:
            return 100

        # Contains exact query
        if query_lower in filename_lower:
            return 90

        # All query chars present in order
        query_chars = list(query_lower)
        file_chars = list(filename_lower)

        i = 0
        for qc in query_chars:
            try:
                idx = file_chars[i:].index(qc)
                i += idx + 1
            except ValueError:
                return 0

        return 70

        return 0


def main(args: Dict[str, Any]) -> Dict[str, Any]:
    """Skill entry point.

    Args:
        args: {"action": "find_file", "query": "foo.py", ...}

    Returns:
        Dict with results
    """
    action = args.get("action")
    if not action:
        return {"error": "Missing 'action' parameter"}

    skill = CodeNavigationSkill()
    return skill.execute(action, **args)


if __name__ == "__main__":
    # Test examples
    skill = CodeNavigationSkill()

    # Test find_file
    print("=== Find File ===")
    result = skill.execute(action="find_file", query="daemon")
    print(f"Found {result['count']} files")
    for file in result["files"][:3]:
        print(f"  {file['path']} (score: {file['score']})")

    # Test find_symbol
    print("\n=== Find Symbol ===")
    result = skill.execute(action="find_symbol", query="DevDaemon")
    print(f"Found {result['count']} symbols")
    for symbol in result["symbols"][:3]:
        print(f"  {symbol['name']} ({symbol['type']}) in {symbol['file']}:{symbol['line']}")
