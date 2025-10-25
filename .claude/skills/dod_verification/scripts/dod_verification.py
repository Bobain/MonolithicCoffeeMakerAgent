#!/usr/bin/env python3
"""
DoD Verification: Main entry point for Definition of Done verification.

This script orchestrates all DoD checks:
- Parse DoD criteria from priority
- Run automated checks (tests, formatting, security)
- Verify code quality
- Test functionality
- Check documentation
- Verify integration
- Generate comprehensive report

Usage:
    python dod_verification.py --priority "US-066" \\
        --description "Implement feature..." \\
        --files-changed "file1.py,file2.py" \\
        --report-output "data/dod_reports/"

Author: code_developer
Date: 2025-10-19
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from coffee_maker.skills.dod_verification.automated_checks import AutomatedChecks
from coffee_maker.skills.dod_verification.code_quality_checker import CodeQualityChecker
from coffee_maker.skills.dod_verification.criteria_parser import CriteriaParser
from coffee_maker.skills.dod_verification.documentation_checker import DocumentationChecker
from coffee_maker.skills.dod_verification.functionality_tester import FunctionalityTester
from coffee_maker.skills.dod_verification.integration_verifier import IntegrationVerifier
from coffee_maker.skills.dod_verification.report_generator import ReportGenerator


@dataclass
class DoDResult:
    """Result of DoD verification."""

    priority: str
    status: str  # "PASS" or "FAIL"
    timestamp: str
    criteria_tested: int
    criteria_passed: int
    criteria_failed: int
    checks: Dict[str, Dict] = field(default_factory=dict)
    recommendation: str = ""
    report_path: str = ""
    execution_time_seconds: float = 0.0
    evidence_files: List[str] = field(default_factory=list)


class DoDVerifier:
    """Main DoD verification orchestrator."""

    def __init__(self, codebase_root: str = "."):
        self.codebase_root = Path(codebase_root)
        self.criteria_parser = CriteriaParser()
        self.automated_checks = AutomatedChecks(self.codebase_root)
        self.code_quality = CodeQualityChecker(self.codebase_root)
        self.functionality_tester = FunctionalityTester(self.codebase_root)
        self.documentation_checker = DocumentationChecker(self.codebase_root)
        self.integration_verifier = IntegrationVerifier(self.codebase_root)
        self.report_generator = ReportGenerator()

    def verify_priority(
        self,
        priority: str,
        description: str,
        files_changed: Optional[List[str]] = None,
        check_types: Optional[List[str]] = None,
        app_url: Optional[str] = None,
    ) -> DoDResult:
        """
        Verify DoD for a priority.

        Args:
            priority: Priority identifier (e.g., "US-066")
            description: Full priority description with acceptance criteria
            files_changed: List of files changed in implementation
            check_types: Types of checks to run (default: all)
            app_url: Application URL for Puppeteer testing

        Returns:
            DoDResult with verification results
        """
        start_time = datetime.now()
        files_changed = files_changed or []
        check_types = check_types or ["all"]

        print(f"\n{'='*80}")
        print(f"DoD Verification: {priority}")
        print(f"{'='*80}\n")

        # Step 1: Parse DoD criteria
        print("📋 Parsing DoD criteria...")
        criteria = self.criteria_parser.parse_criteria(description)
        print(f"   Found {len(criteria)} acceptance criteria\n")

        # Initialize results
        checks = {}
        evidence_files = []
        total_passed = 0
        total_failed = 0

        # Step 2: Run checks based on check_types
        if "all" in check_types or "automated" in check_types:
            print("🔧 Running automated checks...")
            automated_result = self.automated_checks.run_all_checks()
            checks["automated"] = automated_result
            if automated_result["status"] == "PASS":
                total_passed += 1
            else:
                total_failed += 1
            print(f"   Status: {automated_result['status']}\n")

        if "all" in check_types or "code_quality" in check_types:
            print("✨ Verifying code quality...")
            quality_result = self.code_quality.check_quality(files_changed)
            checks["code_quality"] = quality_result
            if quality_result["status"] == "PASS":
                total_passed += 1
            else:
                total_failed += 1
            print(f"   Status: {quality_result['status']}\n")

        if "all" in check_types or "functionality" in check_types:
            print("🧪 Testing functionality...")
            functionality_result = self.functionality_tester.test_criteria(criteria, app_url)
            checks["functionality"] = functionality_result
            evidence_files.extend(functionality_result.get("screenshots", []))
            if functionality_result["status"] == "PASS":
                total_passed += 1
            else:
                total_failed += 1
            print(f"   Status: {functionality_result['status']}\n")

        if "all" in check_types or "documentation" in check_types:
            print("📚 Checking documentation...")
            docs_result = self.documentation_checker.check_documentation(files_changed)
            checks["documentation"] = docs_result
            if docs_result["status"] == "PASS":
                total_passed += 1
            else:
                total_failed += 1
            print(f"   Status: {docs_result['status']}\n")

        if "all" in check_types or "integration" in check_types:
            print("🔗 Verifying integration...")
            integration_result = self.integration_verifier.verify_integration(files_changed)
            checks["integration"] = integration_result
            if integration_result["status"] == "PASS":
                total_passed += 1
            else:
                total_failed += 1
            print(f"   Status: {integration_result['status']}\n")

        # Determine overall status
        overall_status = "PASS" if total_failed == 0 else "FAIL"
        recommendation = "READY TO MERGE" if overall_status == "PASS" else "FIX ISSUES BEFORE MERGE"

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Create result
        result = DoDResult(
            priority=priority,
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            criteria_tested=len(criteria),
            criteria_passed=total_passed,
            criteria_failed=total_failed,
            checks=checks,
            recommendation=recommendation,
            execution_time_seconds=execution_time,
            evidence_files=evidence_files,
        )

        # Print summary
        print(f"\n{'='*80}")
        print(f"DoD Verification Summary")
        print(f"{'='*80}")
        print(f"Priority: {priority}")
        print(f"Status: {overall_status}")
        print(f"Criteria Tested: {len(criteria)}")
        print(f"Checks Passed: {total_passed}/{total_passed + total_failed}")
        print(f"Recommendation: {recommendation}")
        print(f"Execution Time: {execution_time:.2f}s")
        print(f"{'='*80}\n")

        return result

    def generate_report(self, result: DoDResult, output_dir: str = "data/dod_reports", format: str = "markdown") -> str:
        """
        Generate DoD verification report.

        Args:
            result: DoD verification result
            output_dir: Output directory for reports
            format: Report format ("markdown" or "json")

        Returns:
            Path to generated report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        priority_safe = result.priority.replace(" ", "_").replace("/", "-")

        if format == "markdown":
            report_content = self.report_generator.generate_markdown_report(result)
            report_file = output_path / f"{priority_safe}_dod_{timestamp}.md"
            report_file.write_text(report_content, encoding="utf-8")
        else:  # json
            report_content = json.dumps(asdict(result), indent=2)
            report_file = output_path / f"{priority_safe}_dod_{timestamp}.json"
            report_file.write_text(report_content, encoding="utf-8")

        result.report_path = str(report_file)
        print(f"📄 Report generated: {report_file}\n")
        return str(report_file)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="DoD Verification for priorities")
    parser.add_argument("--priority", required=True, help="Priority identifier (e.g., US-066)")
    parser.add_argument("--description", help="Full priority description with acceptance criteria")
    parser.add_argument("--files-changed", help="Comma-separated list of files changed")
    parser.add_argument(
        "--check-type",
        choices=["all", "automated", "code_quality", "functionality", "documentation", "integration"],
        default="all",
        help="Type of checks to run",
    )
    parser.add_argument("--app-url", help="Application URL for Puppeteer testing")
    parser.add_argument("--report-output", default="data/dod_reports", help="Output directory for reports")
    parser.add_argument("--report-format", choices=["markdown", "json"], default="markdown", help="Report format")
    parser.add_argument("--report-only", action="store_true", help="Only generate report from previous results")

    args = parser.parse_args()

    # Parse files changed
    files_changed = args.files_changed.split(",") if args.files_changed else []

    # Initialize verifier
    verifier = DoDVerifier()

    if args.report_only:
        print("Report-only mode not yet implemented. Run full verification instead.")
        sys.exit(1)

    if not args.description:
        print("Error: --description is required for DoD verification")
        sys.exit(1)

    # Run verification
    result = verifier.verify_priority(
        priority=args.priority,
        description=args.description,
        files_changed=files_changed,
        check_types=[args.check_type],
        app_url=args.app_url,
    )

    # Generate report
    report_path = verifier.generate_report(result, args.report_output, args.report_format)

    # Exit with appropriate code
    if result.status == "PASS":
        print(f"✅ DoD verification PASSED for {args.priority}")
        sys.exit(0)
    else:
        print(f"❌ DoD verification FAILED for {args.priority}")
        print(f"   See report: {report_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
