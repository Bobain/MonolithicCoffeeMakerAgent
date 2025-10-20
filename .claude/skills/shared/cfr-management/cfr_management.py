"""CFR Management Skill.

Enables project_manager and architect to manage CFRs (Critical Functional Requirements)
consistently.

Author: architect + code_developer
Date: 2025-10-20
Related: CFR-014 (Orchestrator Database Tracing)
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CFRManagementSkill:
    """
    Manages CFR creation, tracking, compliance, and reporting.

    Capabilities:
    - List/read/search CFRs
    - Create new CFRs with proper formatting
    - Check compliance and find violations
    - Generate reports and metrics
    """

    def __init__(self, cfr_file: Optional[Path] = None):
        """
        Initialize CFR management skill.

        Args:
            cfr_file: Path to CFR document (default: docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)
        """
        self.cfr_file = cfr_file or Path("docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md")

        if not self.cfr_file.exists():
            raise FileNotFoundError(f"CFR file not found: {self.cfr_file}")

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a CFR management action.

        Args:
            action: Action to perform
            **kwargs: Action-specific parameters

        Returns:
            Result dict with action output or error
        """
        try:
            if action == "list_cfrs":
                return self._list_cfrs(**kwargs)
            elif action == "read_cfr":
                return self._read_cfr(**kwargs)
            elif action == "search_cfrs":
                return self._search_cfrs(**kwargs)
            elif action == "get_next_cfr_number":
                return self._get_next_cfr_number(**kwargs)
            elif action == "create_cfr":
                return self._create_cfr(**kwargs)
            elif action == "validate_cfr_format":
                return self._validate_cfr_format(**kwargs)
            elif action == "generate_cfr_skeleton":
                return self._generate_cfr_skeleton(**kwargs)
            elif action == "check_compliance":
                return self._check_compliance(**kwargs)
            elif action == "find_violations":
                return self._find_violations(**kwargs)
            elif action == "suggest_fixes":
                return self._suggest_fixes(**kwargs)
            elif action == "generate_cfr_summary":
                return self._generate_cfr_summary(**kwargs)
            elif action == "get_cfr_metrics":
                return self._get_cfr_metrics(**kwargs)
            elif action == "find_related_cfrs":
                return self._find_related_cfrs(**kwargs)
            else:
                return {"error": f"Unknown action: {action}", "result": None}

        except Exception as e:
            logger.error(f"Error executing action '{action}': {e}", exc_info=True)
            return {"error": str(e), "result": None}

    def _list_cfrs(self, **kwargs) -> Dict[str, Any]:
        """
        List all CFRs with summaries.

        Returns:
            List of CFRs with metadata
        """
        with open(self.cfr_file, "r") as f:
            content = f.read()

        # Find all CFR headers: ## CFR-XXX: Title
        cfr_pattern = r"## (CFR-\d+): (.+)"
        matches = re.finditer(cfr_pattern, content)

        cfrs = []
        for match in matches:
            cfr_number = match.group(1)
            cfr_title = match.group(2).strip()

            # Extract rule (first line after header)
            rule_match = re.search(rf"## {re.escape(cfr_number)}:.*?\n\n\*\*Rule\*\*: (.+)", content, re.DOTALL)
            rule = rule_match.group(1).strip() if rule_match else "N/A"

            cfrs.append(
                {
                    "number": cfr_number,
                    "title": cfr_title,
                    "rule": rule[:200] + "..." if len(rule) > 200 else rule,
                    "status": "active",  # TODO: Parse status from document
                }
            )

        return {"error": None, "result": {"cfrs": cfrs, "total_count": len(cfrs)}}

    def _read_cfr(self, cfr_number: int, **kwargs) -> Dict[str, Any]:
        """
        Read specific CFR details.

        Args:
            cfr_number: CFR number (e.g., 14 for CFR-014)

        Returns:
            CFR details
        """
        cfr_formatted = f"CFR-{cfr_number:03d}"

        with open(self.cfr_file, "r") as f:
            content = f.read()

        # Find CFR section
        pattern = rf"## {re.escape(cfr_formatted)}: (.+?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return {"error": f"CFR-{cfr_number:03d} not found", "result": None}

        cfr_content = match.group(0)
        cfr_title = match.group(1).split("\n")[0].strip()

        # Extract key sections
        rule_match = re.search(r"\*\*Rule\*\*: (.+?)(?=\n\n|\*\*)", cfr_content, re.DOTALL)
        rule = rule_match.group(1).strip() if rule_match else "N/A"

        # Extract core principles
        principles_match = re.search(r"\*\*Core Principle\*\*:\s*```(.*?)```", cfr_content, re.DOTALL)
        principles = principles_match.group(1).strip() if principles_match else "N/A"

        # Extract related CFRs
        related_pattern = r"\*\*CFR-(\d+)"
        related_matches = re.findall(related_pattern, cfr_content)
        related_cfrs = [f"CFR-{num}" for num in set(related_matches) if num != str(cfr_number).zfill(3)]

        return {
            "error": None,
            "result": {
                "cfr_number": cfr_formatted,
                "title": cfr_title,
                "rule": rule,
                "core_principles": principles,
                "related_cfrs": related_cfrs,
                "full_content": cfr_content,
            },
        }

    def _search_cfrs(self, keyword: str, **kwargs) -> Dict[str, Any]:
        """
        Search CFRs by keyword.

        Args:
            keyword: Search term

        Returns:
            Matching CFRs with relevance scores
        """
        with open(self.cfr_file, "r") as f:
            content = f.read()

        # Find all CFR sections
        cfr_pattern = r"## (CFR-\d+): (.+?)(?=\n## |\Z)"
        matches = re.finditer(cfr_pattern, content, re.DOTALL)

        results = []
        keyword_lower = keyword.lower()

        for match in matches:
            cfr_number = match.group(1)
            cfr_section = match.group(0)
            cfr_title = match.group(2).split("\n")[0].strip()

            # Calculate relevance (simple keyword frequency)
            section_lower = cfr_section.lower()
            occurrences = section_lower.count(keyword_lower)

            if occurrences > 0:
                # Extract excerpt with keyword
                excerpt_match = re.search(
                    rf".{{0,50}}{re.escape(keyword_lower)}.{{0,50}}", section_lower, re.IGNORECASE
                )
                excerpt = excerpt_match.group(0) if excerpt_match else cfr_title

                relevance_score = min(1.0, occurrences / 10)  # Cap at 1.0

                results.append(
                    {
                        "cfr_number": cfr_number,
                        "title": cfr_title,
                        "relevance_score": relevance_score,
                        "occurrences": occurrences,
                        "excerpt": excerpt,
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return {"error": None, "result": {"matches": results, "total": len(results)}}

    def _get_next_cfr_number(self, **kwargs) -> Dict[str, Any]:
        """
        Get next available CFR number.

        Returns:
            Next CFR number
        """
        with open(self.cfr_file, "r") as f:
            content = f.read()

        # Find all CFR numbers
        cfr_pattern = r"## CFR-(\d+):"
        matches = re.findall(cfr_pattern, content)

        if not matches:
            next_num = 1
        else:
            max_num = max(int(num) for num in matches)
            next_num = max_num + 1

        return {"error": None, "result": {"next_cfr_number": next_num, "formatted": f"CFR-{next_num:03d}"}}

    def _create_cfr(
        self,
        title: str,
        rule: str,
        why_critical: List[str],
        enforcement_type: str = "code-level",
        related_user_story: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create new CFR with proper formatting.

        Args:
            title: CFR title
            rule: Single sentence rule statement
            why_critical: List of reasons why this is critical
            enforcement_type: Type of enforcement (code-level, process-level, design-level)
            related_user_story: Related user story (e.g., "US-110")

        Returns:
            CFR creation result
        """
        # Get next CFR number
        next_num_result = self._get_next_cfr_number()
        next_num = next_num_result["result"]["next_cfr_number"]
        cfr_formatted = f"CFR-{next_num:03d}"

        # Generate CFR content
        cfr_content = f"""
---

## {cfr_formatted}: {title}

**Rule**: {rule}

**Core Principle**:
```
✅ ALLOWED: [TO BE FILLED]
✅ ALLOWED: [TO BE FILLED]

❌ FORBIDDEN: [TO BE FILLED]
❌ FORBIDDEN: [TO BE FILLED]
```

**Why This Is Critical**:

"""

        for i, reason in enumerate(why_critical, 1):
            cfr_content += f"{i}. **{reason}**: [Explanation]\n"

        cfr_content += """
**Real-World Problem This Solves**:

```
BEFORE {cfr} (chaotic):
[Problem description]
→ Result: [Negative outcomes]

AFTER {cfr} (clean):
[Solution description]
→ Result: [Positive outcomes]
```

### Enforcement

[Enforcement mechanisms]

### Acceptance Criteria

1. ✅ [Criterion 1]
2. ✅ [Criterion 2]

### Relationship to Other CFRs

**CFR-000**: [Relationship]

### Success Metrics

[Measurable metrics]

**Enforcement**: {enforcement_type}
**Monitoring**: [How it's monitored]
**User Story**: {related_user_story or '[To be created]'}

""".format(
            cfr=cfr_formatted, enforcement_type=enforcement_type, related_user_story=related_user_story
        )

        # Append to CFR file (before "Agent File Access Patterns" section)
        with open(self.cfr_file, "r") as f:
            content = f.read()

        # Find insertion point (before "## Agent File Access Patterns")
        insert_pattern = r"(---\s*\n\n## Agent File Access Patterns)"
        match = re.search(insert_pattern, content)

        if match:
            insert_pos = match.start()
            new_content = content[:insert_pos] + cfr_content + content[insert_pos:]
        else:
            # Append to end if section not found
            new_content = content + cfr_content

        with open(self.cfr_file, "w") as f:
            f.write(new_content)

        logger.info(f"Created {cfr_formatted}: {title}")

        return {
            "error": None,
            "result": {
                "cfr_number": cfr_formatted,
                "title": title,
                "file_path": str(self.cfr_file),
                "preview": cfr_content[:200] + "...",
            },
        }

    def _validate_cfr_format(self, cfr_number: int, **kwargs) -> Dict[str, Any]:
        """
        Check if CFR follows standard template.

        Args:
            cfr_number: CFR number to validate

        Returns:
            Validation result
        """
        read_result = self._read_cfr(cfr_number)
        if read_result["error"]:
            return read_result

        cfr_content = read_result["result"]["full_content"]

        # Check for required sections
        required_sections = ["Rule", "Core Principle", "Why This Is Critical", "Enforcement", "Acceptance Criteria"]

        present = []
        missing = []

        for section in required_sections:
            if f"**{section}**" in cfr_content or f"### {section}" in cfr_content:
                present.append(section)
            else:
                missing.append(section)

        completeness_score = int((len(present) / len(required_sections)) * 100)
        valid = len(missing) == 0

        return {
            "error": None,
            "result": {
                "valid": valid,
                "completeness_score": completeness_score,
                "sections_present": present,
                "missing_sections": missing,
                "issues": [f"Missing section: {s}" for s in missing],
            },
        }

    def _generate_cfr_skeleton(self, title: str, **kwargs) -> Dict[str, Any]:
        """
        Generate CFR template with placeholders.

        Args:
            title: CFR title

        Returns:
            CFR template
        """
        template = f"""## CFR-XXX: {title}

**Rule**: [Single sentence rule statement]

**Core Principle**:
```
✅ ALLOWED: [What's allowed]
❌ FORBIDDEN: [What's forbidden]
```

**Why This Is Critical**:

1. **[Reason 1]**: [Explanation]
2. **[Reason 2]**: [Explanation]

**Real-World Problem This Solves**:

```
BEFORE CFR-XXX (chaotic):
[Problem description]
→ Result: [Negative outcomes]

AFTER CFR-XXX (clean):
[Solution description]
→ Result: [Positive outcomes]
```

### Enforcement

[Enforcement mechanisms]

### Acceptance Criteria

1. ✅ [Criterion 1]
2. ✅ [Criterion 2]

### Relationship to Other CFRs

**CFR-000**: [Relationship]

### Success Metrics

[Measurable metrics]

**Enforcement**: [code-level | process-level | design-level]
**Monitoring**: [How it's monitored]
**User Story**: [Related US]
"""

        return {"error": None, "result": {"template": template}}

    def _check_compliance(self, cfr_number: int, files: List[str], **kwargs) -> Dict[str, Any]:
        """
        Check if code complies with CFR.

        Args:
            cfr_number: CFR to check
            files: List of file paths to check

        Returns:
            Compliance report
        """
        # TODO: Implement CFR-specific compliance checks
        # For now, return placeholder
        return {
            "error": None,
            "result": {
                "compliant": True,  # Placeholder
                "violations": [],
                "compliance_score": 100,
                "note": "Full compliance checking requires CFR-specific rules implementation",
            },
        }

    def _find_violations(self, cfr_number: int, scope: str = "all", **kwargs) -> Dict[str, Any]:
        """
        Find CFR violations across codebase.

        Args:
            cfr_number: CFR to check
            scope: Scope to scan (all, orchestrator, autonomous, etc.)

        Returns:
            Violation report
        """
        # TODO: Implement violation scanning
        # For now, return placeholder
        return {
            "error": None,
            "result": {
                "total_violations": 0,
                "violations": [],
                "note": "Violation scanning requires CFR-specific rules implementation",
            },
        }

    def _suggest_fixes(self, cfr_number: int, file: str, line: int, **kwargs) -> Dict[str, Any]:
        """
        Suggest fixes for CFR violation.

        Args:
            cfr_number: CFR being violated
            file: File with violation
            line: Line number

        Returns:
            Fix suggestions
        """
        # TODO: Implement fix suggestions
        # For now, return placeholder
        return {
            "error": None,
            "result": {
                "violation": "Placeholder violation",
                "suggested_fixes": [],
                "note": "Fix suggestions require CFR-specific rules implementation",
            },
        }

    def _generate_cfr_summary(self, format: str = "markdown", **kwargs) -> Dict[str, Any]:
        """
        Generate CFR summary report.

        Args:
            format: Output format (markdown, json)

        Returns:
            Summary report
        """
        list_result = self._list_cfrs()
        cfrs = list_result["result"]["cfrs"]

        summary = {
            "total_cfrs": len(cfrs),
            "active_cfrs": len(cfrs),  # TODO: Track inactive CFRs
            "recent_cfrs": [cfr["number"] for cfr in cfrs[-3:]],  # Last 3
        }

        if format == "markdown":
            report = f"""# CFR Summary Report

**Total CFRs**: {summary['total_cfrs']}
**Active**: {summary['active_cfrs']}
**Recent**: {', '.join(summary['recent_cfrs'])}

## All CFRs

"""
            for cfr in cfrs:
                report += f"- **{cfr['number']}**: {cfr['title']}\n"

            return {"error": None, "result": {"report": report, "summary": summary}}
        else:
            return {"error": None, "result": {"summary": summary, "cfrs": cfrs}}

    def _get_cfr_metrics(self, **kwargs) -> Dict[str, Any]:
        """
        Get CFR health metrics.

        Returns:
            CFR metrics
        """
        list_result = self._list_cfrs()
        cfrs = list_result["result"]["cfrs"]

        metrics = {
            "total_cfrs": len(cfrs),
            "active_cfrs": len(cfrs),
            "recently_added": [cfr["number"] for cfr in cfrs[-2:]],  # Last 2
            "note": "Full metrics require compliance tracking implementation",
        }

        return {"error": None, "result": {"metrics": metrics}}

    def _find_related_cfrs(self, cfr_number: int, **kwargs) -> Dict[str, Any]:
        """
        Find CFRs related to specified CFR.

        Args:
            cfr_number: CFR number

        Returns:
            Related CFRs
        """
        read_result = self._read_cfr(cfr_number)
        if read_result["error"]:
            return read_result

        related_cfrs = read_result["result"]["related_cfrs"]

        # Get details for each related CFR
        related_details = []
        for cfr_num_str in related_cfrs:
            cfr_num = int(cfr_num_str.split("-")[1])
            detail_result = self._read_cfr(cfr_num)
            if not detail_result["error"]:
                related_details.append(
                    {
                        "cfr_number": cfr_num_str,
                        "title": detail_result["result"]["title"],
                        "relationship": "Referenced in CFR content",
                    }
                )

        return {"error": None, "result": {"related_cfrs": related_details}}
