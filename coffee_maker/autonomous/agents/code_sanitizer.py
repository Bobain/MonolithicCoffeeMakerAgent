"""Code-sanitizer agent with automatic ACE integration.

Monitors code quality and provides refactoring recommendations.

Responsibilities:
- Analyze code complexity and maintainability
- Detect refactoring opportunities
- Generate quality reports for project_manager
- Track code metrics over time
- Enforce style guidelines from .gemini.styleguide.md
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

logger = logging.getLogger(__name__)


class CodeSanitizer(ACEAgent):
    """Code-sanitizer agent with automatic ACE integration.

    Wakes up when code_developer makes changes.
    Analyzes code quality and generates refactoring recommendations.

    Owned Directory:
    - docs/refacto/ (refactoring recommendations and analysis)

    ACE Integration:
    - Automatic via ACEAgent base class
    - Enable/disable: ACE_ENABLED_CODE_SANITIZER environment variable
    """

    @property
    def agent_name(self) -> str:
        """Agent name for ACE."""
        return "code_sanitizer"

    @property
    def agent_objective(self) -> str:
        """Agent objective for ACE context."""
        return "Monitor code quality, detect refactoring opportunities, and ensure maintainability"

    @property
    def success_criteria(self) -> str:
        """Success criteria for ACE evaluation."""
        return "Accurate complexity analysis, actionable refactoring recommendations, and improved code quality over time"

    def __init__(self):
        """Initialize code-sanitizer agent."""
        # Initialize ACE (automatic via base class)
        super().__init__()

        # Skip agent-specific initialization if already initialized (singleton)
        if hasattr(self, "_agent_initialized") and self._agent_initialized:
            logger.debug("CodeSanitizer agent-specific components already initialized (singleton)")
            return

        # Initialize agent-specific components
        self.refacto_dir = Path("docs/refacto")
        self.refacto_dir.mkdir(parents=True, exist_ok=True)

        self.style_guide_path = Path(".gemini.styleguide.md")

        # Mark agent-specific init as complete
        self._agent_initialized = True

        logger.info("CodeSanitizer initialized (with automatic ACE)")

    def _execute_implementation(
        self, code_path: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Core code analysis logic.

        Args:
            code_path: Path to analyze (default: coffee_maker/)
            context: Optional context (recent commits, changed files, etc.)

        Returns:
            Analysis result with refactoring recommendations
        """
        # Set plan
        self._set_plan(
            [
                "Load style guide",
                "Analyze code complexity",
                "Detect code duplication",
                "Check style compliance",
                "Generate refactoring recommendations",
                "Write report to docs/refacto/",
            ]
        )

        # Default to coffee_maker/ directory
        if code_path is None:
            code_path = "coffee_maker/"

        # Step 1: Load style guide
        self._update_plan_progress("Load style guide", "in_progress")
        style_guide = self._load_style_guide()
        self._update_plan_progress("Load style guide", "completed")

        # Step 2: Analyze complexity
        self._update_plan_progress("Analyze code complexity", "in_progress")
        complexity_results = self._analyze_complexity(code_path)
        self._update_plan_progress("Analyze code complexity", "completed")

        # Step 3: Detect duplication
        self._update_plan_progress("Detect code duplication", "in_progress")
        duplication_results = self._detect_duplication(code_path)
        self._update_plan_progress("Detect code duplication", "completed")

        # Step 4: Check style
        self._update_plan_progress("Check style compliance", "in_progress")
        style_results = self._check_style_compliance(code_path)
        self._update_plan_progress("Check style compliance", "completed")

        # Step 5: Generate recommendations
        self._update_plan_progress("Generate refactoring recommendations", "in_progress")
        recommendations = self._generate_recommendations(
            complexity_results, duplication_results, style_results, style_guide
        )
        self._update_plan_progress("Generate refactoring recommendations", "completed")

        # Step 6: Write report
        self._update_plan_progress("Write report to docs/refacto/", "in_progress")
        report_path = self._write_report(recommendations, code_path, context or {})
        self._update_plan_progress("Write report to docs/refacto/", "completed")

        return {
            "status": "success",
            "report_path": str(report_path),
            "recommendations": recommendations,
            "summary": {
                "high_priority": len([r for r in recommendations if r["priority"] == "high"]),
                "medium_priority": len([r for r in recommendations if r["priority"] == "medium"]),
                "low_priority": len([r for r in recommendations if r["priority"] == "low"]),
            },
        }

    def _load_style_guide(self) -> Dict[str, Any]:
        """Load style guide from .gemini.styleguide.md."""
        if not self.style_guide_path.exists():
            self._report_concern("Style guide not found: .gemini.styleguide.md")
            return {}

        # Parse style guide (simplified)
        content = self.style_guide_path.read_text()
        return {"content": content, "loaded": True}

    def _analyze_complexity(self, path: str) -> Dict[str, Any]:
        """Analyze code complexity using radon."""
        try:
            # Run radon complexity analysis
            result = subprocess.run(
                ["radon", "cc", path, "-a", "--json"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout else {}
            else:
                self._report_difficulty(f"radon failed: {result.stderr}", severity="low")
                return {}
        except FileNotFoundError:
            self._report_concern("radon not installed (pip install radon)")
            return {}
        except Exception as e:
            self._report_difficulty(f"Complexity analysis error: {e}", severity="medium")
            return {}

    def _detect_duplication(self, path: str) -> Dict[str, Any]:
        """Detect code duplication."""
        # Placeholder - would use tool like 'jscpd' or 'pylint --disable=all --enable=duplicate-code'
        # For now, return empty results
        return {"duplicates_found": 0, "details": []}

    def _check_style_compliance(self, path: str) -> Dict[str, Any]:
        """Check PEP 8 compliance using flake8."""
        try:
            result = subprocess.run(["flake8", path, "--count", "--statistics"], capture_output=True, text=True, timeout=30)

            return {"total_violations": result.stdout.count("\n"), "details": result.stdout}
        except FileNotFoundError:
            self._report_concern("flake8 not installed (pip install flake8)")
            return {}
        except Exception as e:
            self._report_difficulty(f"Style check error: {e}", severity="low")
            return {}

    def _generate_recommendations(
        self,
        complexity: Dict[str, Any],
        duplication: Dict[str, Any],
        style: Dict[str, Any],
        style_guide: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate refactoring recommendations."""
        recommendations = []

        # Complexity-based recommendations
        for file_path, functions in complexity.items():
            if isinstance(functions, list):
                for func in functions:
                    complexity_score = func.get("complexity", 0)
                    if complexity_score > 15:
                        recommendations.append(
                            {
                                "type": "complexity",
                                "priority": "high",
                                "file": file_path,
                                "function": func.get("name", "unknown"),
                                "complexity": complexity_score,
                                "recommendation": f"Reduce complexity from {complexity_score} to < 10",
                                "pattern": "Extract Function",
                            }
                        )
                    elif complexity_score > 10:
                        recommendations.append(
                            {
                                "type": "complexity",
                                "priority": "medium",
                                "file": file_path,
                                "function": func.get("name", "unknown"),
                                "complexity": complexity_score,
                                "recommendation": f"Consider reducing complexity from {complexity_score} to < 10",
                                "pattern": "Extract Function",
                            }
                        )

        # Duplication-based recommendations
        if duplication.get("duplicates_found", 0) > 0:
            recommendations.append(
                {
                    "type": "duplication",
                    "priority": "medium",
                    "recommendation": "Extract duplicated code to shared utilities",
                    "pattern": "DRY (Don't Repeat Yourself)",
                }
            )

        # Style-based recommendations
        if style.get("total_violations", 0) > 10:
            recommendations.append(
                {
                    "type": "style",
                    "priority": "low",
                    "violations": style.get("total_violations", 0),
                    "recommendation": "Fix PEP 8 violations",
                    "pattern": "Style Consistency",
                }
            )

        return recommendations

    def _write_report(self, recommendations: List[Dict[str, Any]], code_path: str, context: Dict[str, Any]) -> Path:
        """Write refactoring report to docs/refacto/."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_filename = f"refactoring_analysis_{timestamp}.md"
        report_path = self.refacto_dir / report_filename

        # Generate report content
        content = f"""# Code Refactoring Analysis

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Analyzed Path**: {code_path}
**Total Recommendations**: {len(recommendations)}

## Summary

- **High Priority**: {len([r for r in recommendations if r['priority'] == 'high'])}
- **Medium Priority**: {len([r for r in recommendations if r['priority'] == 'medium'])}
- **Low Priority**: {len([r for r in recommendations if r['priority'] == 'low'])}

## Context

{self._format_context(context)}

## Recommendations

"""

        # Group by priority
        for priority in ["high", "medium", "low"]:
            priority_recs = [r for r in recommendations if r["priority"] == priority]
            if priority_recs:
                content += f"\n### {priority.upper()} Priority\n\n"
                for rec in priority_recs:
                    content += f"**{rec['type'].title()}**: {rec['recommendation']}\n"
                    if "file" in rec:
                        content += f"  - File: `{rec['file']}`\n"
                    if "function" in rec:
                        content += f"  - Function: `{rec['function']}`\n"
                    if "pattern" in rec:
                        content += f"  - Pattern: {rec['pattern']}\n"
                    if "complexity" in rec:
                        content += f"  - Complexity Score: {rec['complexity']}\n"
                    content += "\n"

        content += f"""
## Next Steps

1. **Review high-priority items** immediately
2. **Schedule medium-priority refactoring** in next sprint
3. **Backlog low-priority items** for future cleanup

## For project_manager

Use this report to decide:
- **Should next priority be refactoring?** (if many high-priority items)
- **Or continue with new features?** (if code quality acceptable)

---

**Generated by**: code-sanitizer
**Review Required**: Yes (project_manager decision)
"""

        report_path.write_text(content)
        logger.info(f"Refactoring report written: {report_path}")

        return report_path

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for report."""
        if not context:
            return "No additional context provided."

        lines = []
        if "changed_files" in context:
            lines.append(f"**Changed Files**: {len(context['changed_files'])}")
            for file in context["changed_files"][:5]:  # Show max 5 files
                lines.append(f"  - {file}")
            if len(context["changed_files"]) > 5:
                lines.append(f"  - ... and {len(context['changed_files']) - 5} more")

        if "recent_commit" in context:
            lines.append(f"**Recent Commit**: {context['recent_commit']}")

        return "\n".join(lines) if lines else "No additional context provided."

    def wake_on_code_change(self, changed_files: List[str]) -> Dict[str, Any]:
        """Wake up when code_developer makes changes.

        Args:
            changed_files: List of files changed by code_developer

        Returns:
            Analysis result
        """
        logger.info(f"code-sanitizer waking up: {len(changed_files)} files changed")

        # Analyze changed files
        return self.execute_task(code_path="coffee_maker/", context={"changed_files": changed_files})
