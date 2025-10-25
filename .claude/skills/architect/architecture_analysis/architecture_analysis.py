"""
Architecture Analysis Skill for architect.

Automated analysis: scan → complexity → patterns → report.

Author: code_developer (implementing architect's spec)
Date: 2025-10-19
Related: SPEC-056, US-056
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute architecture analysis.

    Args:
        context: Context data containing optional 'scope' field

    Returns:
        Dict with complexity_score, recommendations, and report_path
    """
    scope = context.get("scope", "coffee_maker/")

    print(f"Analyzing architecture: {scope}")

    # Step 1: Scan codebase
    files = scan_codebase(scope)
    print(f"  Found {len(files)} Python files")

    # Step 2: Measure complexity
    complexity = measure_complexity(files)
    print(f"  Average complexity: {complexity['average']:.2f}")

    # Step 3: Identify patterns
    patterns = identify_patterns(files, complexity)
    print(f"  Identified {len(patterns)} patterns")

    # Step 4: Generate recommendations
    recommendations = generate_recommendations(complexity, patterns)
    print(f"  Generated {len(recommendations)} recommendations")

    # Step 5: Create report
    report_path = create_analysis_report(complexity, patterns, recommendations)
    print(f"  Report generated: {report_path}")

    return {
        "complexity_score": complexity["average"],
        "recommendations": recommendations,
        "report_path": str(report_path),
    }


def scan_codebase(scope: str) -> List[Path]:
    """Scan codebase and return Python files.

    Args:
        scope: Directory scope to scan

    Returns:
        List of Python file paths
    """
    scope_path = Path(scope)
    if not scope_path.exists():
        return []

    # Find all *.py files, exclude tests and __pycache__
    files = []
    for py_file in scope_path.rglob("*.py"):
        # Skip test files and pycache
        if "__pycache__" in str(py_file) or "test" in py_file.stem.lower():
            continue
        files.append(py_file)

    return sorted(files)


def measure_complexity(files: List[Path]) -> Dict[str, Any]:
    """Measure cyclomatic complexity using radon.

    Args:
        files: List of Python file paths

    Returns:
        Dict with average, max, min, distribution
    """
    if not files:
        return {"average": 0.0, "max": 0.0, "min": 0.0, "max_file": None, "file_count": 0, "distribution": {}}

    complexities = []
    max_complexity = 0.0
    max_file = None

    for file_path in files:
        try:
            # Run radon cc on each file
            result = subprocess.run(
                ["radon", "cc", str(file_path), "--json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                file_data = data.get(str(file_path), [])

                for item in file_data:
                    complexity_score = item.get("complexity", 0)
                    complexities.append(complexity_score)

                    if complexity_score > max_complexity:
                        max_complexity = complexity_score
                        max_file = file_path.name

        except Exception as e:
            print(f"  Warning: Could not analyze {file_path}: {e}")

    if not complexities:
        return {"average": 0.0, "max": 0.0, "min": 0.0, "max_file": None, "file_count": len(files), "distribution": {}}

    avg_complexity = sum(complexities) / len(complexities)
    min_complexity = min(complexities)

    # Distribution: A=1-5, B=6-10, C=11-20, D=21-50, F=51+
    distribution = {
        "A (1-5)": sum(1 for c in complexities if 1 <= c <= 5),
        "B (6-10)": sum(1 for c in complexities if 6 <= c <= 10),
        "C (11-20)": sum(1 for c in complexities if 11 <= c <= 20),
        "D (21-50)": sum(1 for c in complexities if 21 <= c <= 50),
        "F (51+)": sum(1 for c in complexities if c >= 51),
    }

    return {
        "average": avg_complexity,
        "max": max_complexity,
        "min": min_complexity,
        "max_file": max_file,
        "file_count": len(files),
        "distribution": distribution,
    }


def identify_patterns(files: List[Path], complexity: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify patterns (good and bad).

    Args:
        files: List of Python file paths
        complexity: Complexity metrics dictionary

    Returns:
        List of pattern dictionaries with type, name, location
    """
    patterns = []

    # Good patterns: detect mixins, singletons, decorators
    for file_path in files:
        try:
            content = file_path.read_text()

            # Detect Mixin pattern
            if "Mixin" in content:
                patterns.append(
                    {
                        "type": "good",
                        "name": "Mixin Pattern",
                        "location": file_path.name,
                        "description": "Composition with mixins for code reuse",
                    }
                )

            # Detect Singleton pattern
            if "__new__" in content and "cls._instance" in content:
                patterns.append(
                    {
                        "type": "good",
                        "name": "Singleton Pattern",
                        "location": file_path.name,
                        "description": "Singleton pattern for resource management",
                    }
                )

            # Detect Decorator pattern
            if "@observe" in content or "@langfuse" in content:
                patterns.append(
                    {
                        "type": "good",
                        "name": "Decorator Pattern",
                        "location": file_path.name,
                        "description": "Observability with decorators",
                    }
                )

        except Exception:
            pass

    # Bad patterns: high complexity, long files
    if complexity["max"] > 20:
        patterns.append(
            {
                "type": "bad",
                "name": "High Complexity",
                "location": complexity["max_file"],
                "description": f"Cyclomatic complexity {complexity['max']:.1f} (threshold: 20)",
            }
        )

    # Detect long files (>1000 lines)
    for file_path in files[:10]:  # Check top 10 files only
        try:
            lines = len(file_path.read_text().splitlines())
            if lines > 1000:
                patterns.append(
                    {
                        "type": "bad",
                        "name": "God Class",
                        "location": file_path.name,
                        "description": f"{lines} lines (threshold: 1000)",
                    }
                )
        except Exception:
            pass

    return patterns


def generate_recommendations(complexity: Dict[str, Any], patterns: List[Dict[str, Any]]) -> List[str]:
    """Generate improvement recommendations.

    Args:
        complexity: Complexity metrics dictionary
        patterns: List of pattern dictionaries

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # High complexity? → Recommend refactoring
    if complexity["average"] > 10:
        recommendations.append(
            f"Reduce average complexity from {complexity['average']:.1f} to <10 by extracting functions"
        )

    # God classes? → Recommend splitting
    god_classes = [p for p in patterns if p["name"] == "God Class"]
    if god_classes:
        recommendations.append(f"Split large files ({len(god_classes)} found) into smaller, focused modules")

    # High complexity files? → Recommend simplification
    if complexity["max"] > 20:
        recommendations.append(
            f"Simplify {complexity['max_file']} (complexity: {complexity['max']:.1f}) by reducing branching"
        )

    # Good patterns? → Recommend continuation
    good_patterns = [p for p in patterns if p["type"] == "good"]
    if good_patterns:
        recommendations.append(f"Continue using {len(good_patterns)} good patterns (mixins, singletons, decorators)")

    # Distribution skewed to high complexity? → Recommend review
    high_complexity_count = complexity["distribution"].get("D (21-50)", 0) + complexity["distribution"].get(
        "F (51+)", 0
    )
    if high_complexity_count > 5:
        recommendations.append(
            f"Review {high_complexity_count} high-complexity functions for refactoring opportunities"
        )

    # If no recommendations, add a positive one
    if not recommendations:
        recommendations.append("Architecture is healthy - continue current patterns and practices")

    return recommendations[:5]  # Limit to top 5


def create_analysis_report(
    complexity: Dict[str, Any], patterns: List[Dict[str, Any]], recommendations: List[str]
) -> Path:
    """Create synthetic architecture analysis report.

    Args:
        complexity: Complexity metrics dictionary
        patterns: List of pattern dictionaries
        recommendations: List of recommendation strings

    Returns:
        Path to generated report
    """
    good_patterns = [p for p in patterns if p["type"] == "good"]
    bad_patterns = [p for p in patterns if p["type"] == "bad"]

    report = f"""# Architecture Analysis Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Complexity Metrics

- **Average Complexity**: {complexity['average']:.2f}
- **Max Complexity**: {complexity['max']:.2f} ({complexity['max_file']})
- **Files Analyzed**: {complexity['file_count']}

### Complexity Distribution

"""

    for grade, count in complexity["distribution"].items():
        if count > 0:
            report += f"- **{grade}**: {count} functions\n"

    report += f"""
## Patterns Detected

### Good Patterns ✅

"""

    if not good_patterns:
        report += "_No good patterns detected yet. Consider adopting mixins, singletons, or decorators._\n\n"
    else:
        for pattern in good_patterns[:5]:  # Top 5
            report += f"- **{pattern['name']}** in `{pattern['location']}`: {pattern['description']}\n"
        report += "\n"

    report += "### Anti-Patterns ⚠️\n\n"

    if not bad_patterns:
        report += "_No anti-patterns detected. Codebase is healthy!_ ✅\n\n"
    else:
        for pattern in bad_patterns[:5]:  # Top 5
            report += f"- **{pattern['name']}** in `{pattern['location']}`: {pattern['description']}\n"
        report += "\n"

    report += "## Top Recommendations\n\n"

    for i, rec in enumerate(recommendations, 1):
        report += f"{i}. {rec}\n"

    report += "\n"

    # Save report
    evidence_dir = Path("evidence")
    evidence_dir.mkdir(exist_ok=True)

    report_path = evidence_dir / f"architecture-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    report_path.write_text(report)

    return report_path


if __name__ == "__main__":
    # Load context from stdin or use default
    try:
        if not sys.stdin.isatty():
            stdin_text = sys.stdin.read().strip()
            if stdin_text:
                context = json.loads(stdin_text)
            else:
                context = {"scope": "coffee_maker/"}
        else:
            # Default context for testing
            context = {"scope": "coffee_maker/"}
    except (json.JSONDecodeError, ValueError):
        # Fallback to default context
        context = {"scope": "coffee_maker/"}

    result = main(context)
    print("\nResult:")
    print(json.dumps(result, indent=2))
