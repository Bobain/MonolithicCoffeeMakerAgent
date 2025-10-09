#!/usr/bin/env python3
"""Documentation validation script for Coffee Maker Agent.

This script validates that all Python modules have proper docstrings:
- Module-level docstrings
- Class docstrings
- Function docstrings (public functions)
- Google-style docstring format

Usage:
    python scripts/validate_docs.py

    # Check specific module
    python scripts/validate_docs.py --module coffee_maker.autonomous

    # Strict mode (fail on warnings)
    python scripts/validate_docs.py --strict

    # Generate report
    python scripts/validate_docs.py --report docs/doc_validation_report.md
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


class DocstringValidator:
    """Validates Python docstrings for completeness and style.

    Checks:
    - Module docstrings exist
    - Class docstrings exist
    - Public function docstrings exist
    - Docstring format (basic check)

    Attributes:
        errors: List of error messages
        warnings: List of warning messages
        info: List of info messages
    """

    def __init__(self):
        """Initialize the validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_file(self, filepath: Path) -> Tuple[int, int, int]:
        """Validate docstrings in a Python file.

        Args:
            filepath: Path to Python file to validate

        Returns:
            Tuple of (errors, warnings, info_count)
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(filepath))

            # Check module docstring
            module_docstring = ast.get_docstring(tree)
            if not module_docstring:
                self.errors.append(f"{filepath}: Missing module docstring")
            elif len(module_docstring) < 20:
                self.warnings.append(f"{filepath}: Module docstring too short (< 20 chars)")

            # Check classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._validate_class(node, filepath)
                elif isinstance(node, ast.FunctionDef):
                    self._validate_function(node, filepath)

        except SyntaxError as e:
            self.errors.append(f"{filepath}: Syntax error: {e}")
        except Exception as e:
            self.errors.append(f"{filepath}: Error parsing: {e}")

        return len(self.errors), len(self.warnings), len(self.info)

    def _validate_class(self, node: ast.ClassDef, filepath: Path) -> None:
        """Validate a class definition.

        Args:
            node: AST node for class
            filepath: Path to file containing class
        """
        class_name = node.name

        # Skip private classes
        if class_name.startswith("_"):
            return

        docstring = ast.get_docstring(node)

        if not docstring:
            self.errors.append(f"{filepath}:{node.lineno}: Class `{class_name}` missing docstring")
        elif len(docstring) < 20:
            self.warnings.append(f"{filepath}:{node.lineno}: Class `{class_name}` docstring too short")
        else:
            # Check for basic Google-style sections
            if "Attributes:" in docstring or "Args:" in docstring or "Example:" in docstring:
                self.info.append(f"{filepath}:{node.lineno}: Class `{class_name}` has structured docstring")

    def _validate_function(self, node: ast.FunctionDef, filepath: Path) -> None:
        """Validate a function definition.

        Args:
            node: AST node for function
            filepath: Path to file containing function
        """
        func_name = node.name

        # Skip private functions and special methods
        if func_name.startswith("_") and not func_name.startswith("__"):
            return

        # Skip test functions
        if func_name.startswith("test_"):
            return

        docstring = ast.get_docstring(node)

        if not docstring:
            self.errors.append(f"{filepath}:{node.lineno}: Function `{func_name}` missing docstring")
        elif len(docstring) < 10:
            self.warnings.append(f"{filepath}:{node.lineno}: Function `{func_name}` docstring too short")
        else:
            # Check for Args and Returns sections if function has parameters/return
            has_params = len(node.args.args) > 0
            has_return = any(isinstance(n, ast.Return) and n.value for n in ast.walk(node))

            if has_params and "Args:" not in docstring:
                self.warnings.append(
                    f"{filepath}:{node.lineno}: Function `{func_name}` has parameters but no Args section"
                )

            if has_return and "Returns:" not in docstring:
                self.warnings.append(
                    f"{filepath}:{node.lineno}: Function `{func_name}` has return but no Returns section"
                )


def find_python_files(directory: Path, exclude: List[str] = None) -> List[Path]:
    """Find all Python files in directory.

    Args:
        directory: Root directory to search
        exclude: List of patterns to exclude

    Returns:
        List of Python file paths
    """
    if exclude is None:
        exclude = ["__pycache__", ".git", ".venv", "venv", "build", "dist", ".eggs"]

    python_files = []

    for path in directory.rglob("*.py"):
        # Check if any exclude pattern is in the path
        if any(ex in str(path) for ex in exclude):
            continue

        python_files.append(path)

    return sorted(python_files)


def generate_report(validator: DocstringValidator, files_checked: int, output_file: Path = None) -> str:
    """Generate validation report.

    Args:
        validator: Validator instance with results
        files_checked: Number of files checked
        output_file: Optional file to write report to

    Returns:
        Report string
    """
    error_count = len(validator.errors)
    warning_count = len(validator.warnings)
    info_count = len(validator.info)

    report_lines = [
        "# Documentation Validation Report",
        "",
        f"**Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Files Checked**: {files_checked}",
        f"**Errors**: {error_count}",
        f"**Warnings**: {warning_count}",
        f"**Info**: {info_count}",
        "",
    ]

    if error_count > 0:
        report_lines.extend(["## Errors", ""])
        for error in validator.errors:
            report_lines.append(f"- {error}")
        report_lines.append("")

    if warning_count > 0:
        report_lines.extend(["## Warnings", ""])
        for warning in validator.warnings:
            report_lines.append(f"- {warning}")
        report_lines.append("")

    if info_count > 0:
        report_lines.extend(["## Info", ""])
        for info in validator.info[:10]:  # Limit to 10
            report_lines.append(f"- {info}")
        if info_count > 10:
            report_lines.append(f"- ... and {info_count - 10} more")
        report_lines.append("")

    report_lines.extend(
        [
            "## Summary",
            "",
            f"**Status**: {'✅ PASS' if error_count == 0 else '❌ FAIL'}",
            "",
            "**Next Steps**:",
        ]
    )

    if error_count > 0:
        report_lines.append("- Fix missing docstrings")
    if warning_count > 0:
        report_lines.append("- Address warnings for better documentation")
    if error_count == 0 and warning_count == 0:
        report_lines.append("- Documentation is in good shape!")

    report = "\n".join(report_lines)

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report)
        print(f"\n{GREEN}Report written to: {output_file}{RESET}")

    return report


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description="Validate Python docstrings in Coffee Maker Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--module",
        help="Specific module to check (e.g., coffee_maker.autonomous)",
        default="coffee_maker",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings (not just errors)",
    )

    parser.add_argument(
        "--report",
        help="Generate report file (Markdown)",
        type=Path,
    )

    parser.add_argument(
        "--exclude",
        nargs="*",
        help="Patterns to exclude",
        default=["test", "tests", "__pycache__", ".git"],
    )

    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Determine directory to check
    module_path = project_root / args.module.replace(".", "/")

    if not module_path.exists():
        print(f"{RED}Error: Module path not found: {module_path}{RESET}")
        sys.exit(1)

    print(f"{BOLD}Coffee Maker Agent - Documentation Validator{RESET}")
    print(f"Checking: {module_path}")
    print(f"Exclude patterns: {', '.join(args.exclude)}")
    print()

    # Find Python files
    python_files = find_python_files(module_path, exclude=args.exclude)

    if not python_files:
        print(f"{YELLOW}No Python files found{RESET}")
        sys.exit(0)

    print(f"Found {len(python_files)} Python files\n")

    # Validate each file
    validator = DocstringValidator()
    files_with_errors = 0
    files_with_warnings = 0

    for filepath in python_files:
        filepath.relative_to(project_root)
        errors, warnings, info = validator.validate_file(filepath)

        if errors > 0:
            files_with_errors += 1
        if warnings > 0:
            files_with_warnings += 1

    # Print summary
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"Files checked: {len(python_files)}")
    print(f"Files with errors: {files_with_errors}")
    print(f"Files with warnings: {files_with_warnings}")
    print()

    error_count = len(validator.errors)
    warning_count = len(validator.warnings)

    if error_count > 0:
        print(f"{RED}Errors: {error_count}{RESET}")
        for error in validator.errors[:5]:  # Show first 5
            print(f"  {error}")
        if error_count > 5:
            print(f"  ... and {error_count - 5} more")
        print()

    if warning_count > 0:
        print(f"{YELLOW}Warnings: {warning_count}{RESET}")
        for warning in validator.warnings[:5]:  # Show first 5
            print(f"  {warning}")
        if warning_count > 5:
            print(f"  ... and {warning_count - 5} more")
        print()

    # Generate report if requested
    if args.report:
        generate_report(validator, len(python_files), args.report)

    # Determine exit code
    if error_count > 0:
        print(f"{RED}❌ Validation FAILED{RESET}")
        sys.exit(1)
    elif args.strict and warning_count > 0:
        print(f"{YELLOW}⚠️  Validation FAILED (strict mode){RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}✅ Validation PASSED{RESET}")
        if warning_count > 0:
            print(f"{YELLOW}Note: {warning_count} warnings found{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
