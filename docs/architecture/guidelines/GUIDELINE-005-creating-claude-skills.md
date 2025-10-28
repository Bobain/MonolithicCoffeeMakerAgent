# GUIDELINE-005: Creating Claude Skills

**Category**: Best Practice

**Applies To**: All agents (skill creation)

**Author**: architect agent

**Date**: 2025-10-17

**Related**: SPEC-001-claude-skills-integration.md, ADR-002-integrate-claude-skills.md

---

## Purpose

This guideline provides step-by-step instructions for creating Claude Skills in the MonolithicCoffeeMakerAgent system. It covers when to create a skill, how to structure it, testing strategies, and integration with agents.

---

## When to Create a Skill

### Decision Framework

Use the following decision tree to determine if a task should be a skill:

```
Task requires reliable calculation? ────────── YES → CREATE SKILL
         │ NO
Task involves external API calls? ───────────── YES → CREATE SKILL
         │ NO
Task requires file/code parsing? ────────────── YES → CREATE SKILL
         │ NO
Task is repetitive (same logic)? ────────────── YES → CREATE SKILL
         │ NO
Task requires creative writing? ─────────────── YES → USE PROMPT (not skill)
         │ NO
Task requires complex reasoning? ────────────── YES → USE PROMPT (not skill)
         │ NO
Task is one-off (not reusable)? ─────────────── YES → USE PROMPT (not skill)
         │ NO
Need both data + interpretation? ────────────── YES → HYBRID (skill + prompt)
```

### Examples

**✅ GOOD Skill Candidates**:
- architect: Dependency security scanning (CVE lookup, license checks)
- assistant (using code analysis skills): Code vulnerability detection (regex patterns, AST analysis)
- assistant: Puppeteer demo creation (reproducible browser automation)
- project_manager: GitHub PR status checking (API calls)
- code_developer: Test scaffolding (boilerplate generation)

**❌ BAD Skill Candidates**:
- Writing ADRs (creative reasoning → use prompt)
- Strategic planning discussions (complex reasoning → use prompt)
- One-off code refactoring (not reusable → use prompt)
- Design critiques (subjective analysis → use prompt)

**✅ HYBRID Candidates**:
- architect: Dependency evaluation (skill scans data → prompt recommends)
- assistant (using code analysis skills): Security audit (skill finds vulnerabilities → prompt explains)
- assistant: Bug analysis (skill detects bug → prompt analyzes root cause)

---

## How to Create a Skill

### Step 1: Determine Skill Scope

**Question**: Who should have access to this skill?

- **Shared** (`.claude/skills/shared/`): All agents can use
  - Examples: git-operations, testing-automation, documentation-generation
  - Use when: Multiple agents need the same functionality

- **Agent-Specific** (`.claude/skills/<agent>/`): Only one agent uses
  - Examples: architect/dependency-analysis, assistant/demo-creator
  - Use when: Skill is tailored to specific agent role

**Rule of Thumb**: Start agent-specific. Move to shared if 2+ agents need it.

### Step 2: Create Skill Directory

```bash
# For agent-specific skill
mkdir -p .claude/skills/architect/dependency-analysis

# For shared skill
mkdir -p .claude/skills/shared/git-operations
```

**Naming Convention**: `<domain>-<action>` (kebab-case)
- ✅ dependency-analysis (not `DependencyAnalysis`, `analyze_dependency`)
- ✅ security-audit (not `securityAudit`, `SecurityAudit`)
- ✅ git-operations (not `GitOps`, `git_ops`)

### Step 3: Create SKILL.md (Metadata)

```bash
# Create SKILL.md with metadata
cat > .claude/skills/architect/dependency-analysis/SKILL.md << 'EOF'
---
name: dependency-analysis
version: 1.0.0
agent: architect
scope: agent-specific
description: >
  Analyzes Python package dependencies for security vulnerabilities,
  licensing compatibility, and maintenance status.

triggers:
  - "analyze dependency"
  - "check package security"
  - "evaluate license compatibility"
  - "assess dependency risk"

requires:
  - python>=3.9
  - requests
  - packaging

inputs:
  package_name:
    type: string
    required: true
    description: Name of package (e.g., "redis")

  version:
    type: string
    required: true
    description: Package version (e.g., "5.0.0")

outputs:
  security:
    type: object
    description: Security report with CVEs

  licensing:
    type: object
    description: License compatibility report

  maintenance:
    type: object
    description: Package maintenance status

examples:
  - task: "analyze redis 5.0.0 security"
    context:
      package_name: "redis"
      version: "5.0.0"
    expected_output: "examples/redis_analysis.json"

author: architect agent
created: 2025-10-17
updated: 2025-10-17
---

# Dependency Analysis Skill

This skill analyzes Python package dependencies for:
1. Security: CVE lookup, vulnerability scanning
2. Licensing: License compatibility check
3. Maintenance: Activity status, last update

## Usage

```python
result = skill_controller.execute_task(
    "analyze redis package security",
    context={"package_name": "redis", "version": "5.0.0"}
)
```

## Output Format

```json
{
  "security": {"cves": [], "score": 10.0},
  "licensing": {"license": "MIT", "compatible": true},
  "maintenance": {"last_update": "2025-09-01", "active": true}
}
```
EOF
```

**SKILL.md Structure**:
- **YAML Frontmatter**: Metadata (name, version, triggers, etc.)
- **Markdown Body**: Documentation (usage, examples, output format)

### Step 4: Implement Executable Code

**Option A: Python Script** (recommended):

```python
# .claude/skills/architect/dependency-analysis/check_security.py

import json
import argparse
import sys
from typing import Dict, List

def main():
    """Main entry point for skill execution."""
    parser = argparse.ArgumentParser(
        description="Check package security (CVEs, vulnerabilities)"
    )
    parser.add_argument(
        "--context",
        required=True,
        help="Path to context JSON file"
    )
    args = parser.parse_args()

    # Load context
    try:
        with open(args.context) as f:
            context = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Failed to load context: {e}"}), file=sys.stderr)
        sys.exit(1)

    # Extract inputs
    package_name = context.get("package_name")
    version = context.get("version")

    if not package_name or not version:
        print(json.dumps({"error": "Missing required inputs: package_name, version"}), file=sys.stderr)
        sys.exit(1)

    # Execute skill logic
    try:
        result = check_security(package_name, version)
        # Output JSON to stdout
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


def check_security(package_name: str, version: str) -> Dict:
    """Check package security (CVEs, vulnerabilities).

    Args:
        package_name: Name of package (e.g., "redis")
        version: Package version (e.g., "5.0.0")

    Returns:
        Security report with CVEs, vulnerabilities, score
    """
    # Implementation...
    cves = query_cve_database(package_name, version)
    vulnerabilities = scan_vulnerabilities(package_name, version)
    score = calculate_security_score(cves, vulnerabilities)

    return {
        "cves": cves,
        "vulnerabilities": vulnerabilities,
        "score": score
    }


def query_cve_database(package: str, version: str) -> List[Dict]:
    """Query CVE database for known vulnerabilities."""
    # Implementation: Query CVE API or local database
    return []


def scan_vulnerabilities(package: str, version: str) -> List[Dict]:
    """Scan for vulnerabilities."""
    # Implementation: Check for common vulnerability patterns
    return []


def calculate_security_score(cves: List, vulnerabilities: List) -> float:
    """Calculate security score (0-10, 10 is best)."""
    if cves or vulnerabilities:
        return 0.0  # Critical issues found
    return 10.0  # No issues found


if __name__ == "__main__":
    main()
```

**Option B: Shell Script** (for simple tasks):

```bash
# .claude/skills/shared/git-operations/commit.sh

#!/bin/bash
# Git commit skill

# Context is passed via environment variables
MESSAGE="${COMMIT_MESSAGE:-"Automated commit"}"
FILES="${FILES:-"."}"

# Perform git operations
git add $FILES
git commit -m "$MESSAGE"

# Output result as JSON
echo "{\"status\": \"success\", \"message\": \"$MESSAGE\"}"
```

**Key Requirements**:
- ✅ Accept `--context <path>` argument (Python) or env vars (shell)
- ✅ Output JSON to stdout
- ✅ Error messages to stderr
- ✅ Exit code 0 for success, non-zero for failure
- ✅ Handle missing/invalid inputs gracefully

### Step 5: Add Example Outputs

```bash
# Create examples directory
mkdir -p .claude/skills/architect/dependency-analysis/examples

# Add example output
cat > .claude/skills/architect/dependency-analysis/examples/redis_analysis.json << 'EOF'
{
  "security": {
    "cves": [],
    "vulnerabilities": [],
    "score": 10.0
  },
  "licensing": {
    "license": "MIT",
    "compatible": true,
    "osi_approved": true
  },
  "maintenance": {
    "last_update": "2025-09-01",
    "active": true,
    "maintainers": 15,
    "stars": 12500
  }
}
EOF
```

### Step 6: Test the Skill

**Unit Tests** (pytest):

```python
# tests/skills/test_dependency_analysis.py

import json
import tempfile
from pathlib import Path
import subprocess


def test_dependency_analysis_success():
    """Test dependency analysis skill with valid inputs."""
    # Create context file
    context = {
        "package_name": "redis",
        "version": "5.0.0"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(context, f)
        context_file = f.name

    try:
        # Execute skill
        result = subprocess.run(
            [
                "python",
                ".claude/skills/architect/dependency-analysis/check_security.py",
                "--context", context_file
            ],
            capture_output=True,
            text=True
        )

        # Verify success
        assert result.returncode == 0
        output = json.loads(result.stdout)

        # Verify output structure
        assert "security" in output
        assert "cves" in output["security"]
        assert "score" in output["security"]
        assert output["security"]["score"] >= 0
        assert output["security"]["score"] <= 10

    finally:
        Path(context_file).unlink(missing_ok=True)


def test_dependency_analysis_missing_input():
    """Test dependency analysis with missing inputs."""
    context = {"package_name": "redis"}  # Missing version

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(context, f)
        context_file = f.name

    try:
        result = subprocess.run(
            [
                "python",
                ".claude/skills/architect/dependency-analysis/check_security.py",
                "--context", context_file
            ],
            capture_output=True,
            text=True
        )

        # Should fail gracefully
        assert result.returncode != 0
        assert "error" in result.stderr.lower()

    finally:
        Path(context_file).unlink(missing_ok=True)
```

**Run tests**:
```bash
pytest tests/skills/test_dependency_analysis.py -v
```

### Step 7: Register Skill with Agent

**Update agent to use skill**:

```python
# coffee_maker/autonomous/architect.py (or wherever agent logic lives)

from coffee_maker.autonomous.agent_skill_controller import AgentSkillController
from coffee_maker.autonomous.agent_registry import AgentType


class ArchitectAgent:
    def __init__(self):
        # Initialize skill controller
        self.skill_controller = AgentSkillController(AgentType.ARCHITECT)

    def evaluate_dependency(self, package: str, version: str):
        """Evaluate dependency using dependency-analysis skill."""
        result = self.skill_controller.execute_task(
            task_description="analyze dependency security",
            context={
                "package_name": package,
                "version": version
            }
        )

        if not result.success:
            raise RuntimeError(f"Dependency analysis failed: {result.errors}")

        return result.output
```

**Refresh skill registry** (if skill added while agent running):

```python
# Force registry refresh
self.skill_controller.registry.refresh()
```

### Step 8: Document the Skill

**Add to agent skill catalog**:

```bash
# Create/update agent skill catalog
cat >> docs/skills/architect_skills.md << 'EOF'

## dependency-analysis

**Purpose**: Analyzes Python package dependencies for security, licensing, and maintenance.

**Triggers**:
- "analyze dependency"
- "check package security"
- "evaluate license compatibility"

**Inputs**:
- `package_name` (string): Package name (e.g., "redis")
- `version` (string): Package version (e.g., "5.0.0")

**Outputs**:
- `security` (object): CVE list, vulnerability scan, security score
- `licensing` (object): License type, compatibility
- `maintenance` (object): Last update, active status, maintainers

**Usage**:
```python
result = skill_controller.execute_task(
    "analyze redis package security",
    context={"package_name": "redis", "version": "5.0.0"}
)
print(result.output["security"]["score"])  # 10.0
```

**Example Output**:
```json
{
  "security": {"cves": [], "score": 10.0},
  "licensing": {"license": "MIT", "compatible": true},
  "maintenance": {"last_update": "2025-09-01", "active": true}
}
```

**Author**: architect agent
**Created**: 2025-10-17

EOF
```

---

## Testing Strategy

### Unit Tests (Required)

Test skill in isolation:

```python
def test_skill_success():
    """Test skill with valid inputs."""
    # Execute skill with test context
    # Verify output structure
    # Verify output values

def test_skill_missing_input():
    """Test skill with missing inputs."""
    # Execute skill with incomplete context
    # Verify graceful failure (non-zero exit code)
    # Verify error message

def test_skill_invalid_input():
    """Test skill with invalid inputs."""
    # Execute skill with malformed data
    # Verify graceful failure
```

### Integration Tests (Recommended)

Test skill with agent:

```python
def test_agent_uses_skill():
    """Test agent can discover and invoke skill."""
    agent = ArchitectAgent()
    result = agent.skill_controller.execute_task(
        "analyze redis security",
        context={"package_name": "redis", "version": "5.0.0"}
    )
    assert result.success
    assert "security" in result.output
```

### Manual Tests (Required)

Test skill via CLI:

```bash
# Create test context
cat > /tmp/test_context.json << 'EOF'
{
  "package_name": "redis",
  "version": "5.0.0"
}
EOF

# Execute skill
python .claude/skills/architect/dependency-analysis/check_security.py \
    --context /tmp/test_context.json

# Verify output
# Expected: JSON with security, licensing, maintenance
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Hardcoding Values

**BAD**:
```python
def check_security(package: str, version: str):
    # Hardcoded API URL
    url = "https://api.example.com/cve"
    # What if API changes? Skill breaks!
```

**GOOD**:
```python
def check_security(package: str, version: str):
    # Use environment variable or context
    api_url = os.getenv("CVE_API_URL", "https://api.example.com/cve")
    # Flexible, configurable
```

### ❌ Anti-Pattern 2: No Error Handling

**BAD**:
```python
def main():
    context = json.load(open(args.context))  # Crashes if file missing
    result = check_security(context["package"])  # Crashes if key missing
    print(json.dumps(result))  # No error handling
```

**GOOD**:
```python
def main():
    try:
        with open(args.context) as f:
            context = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    package = context.get("package_name")
    if not package:
        print(json.dumps({"error": "Missing package_name"}), file=sys.stderr)
        sys.exit(1)

    try:
        result = check_security(package)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
```

### ❌ Anti-Pattern 3: Non-JSON Output

**BAD**:
```python
def main():
    result = check_security(package)
    print(f"Security score: {result['score']}")  # Not JSON!
    # SkillInvoker expects JSON, will fail to parse
```

**GOOD**:
```python
def main():
    result = check_security(package)
    print(json.dumps(result, indent=2))  # Always JSON
```

### ❌ Anti-Pattern 4: Side Effects (File Writes, DB Updates)

**BAD**:
```python
def check_security(package: str):
    # Writes to file (side effect!)
    with open("/tmp/security_report.txt", "w") as f:
        f.write("Security report...")
    # What if multiple skills run concurrently? Race condition!
```

**GOOD**:
```python
def check_security(package: str):
    # Return data, let caller decide what to do
    return {"report": "Security report..."}
    # No side effects, pure function
```

### ❌ Anti-Pattern 5: Long-Running Skills (>5 minutes)

**BAD**:
```python
def check_security(package: str):
    time.sleep(600)  # 10 minutes! Timeout!
```

**GOOD**:
```python
def check_security(package: str):
    # Optimize for speed (<5 seconds if possible)
    # Use caching, parallel requests, etc.
    return quick_security_check(package)
```

---

## Code Examples

### Example 1: Simple Skill (Git Commit)

```python
# .claude/skills/shared/git-operations/commit.py

import json
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    args = parser.parse_args()

    with open(args.context) as f:
        context = json.load(f)

    message = context.get("commit_message", "Automated commit")
    files = context.get("files", ["."])

    # Execute git commit
    subprocess.run(["git", "add"] + files, check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)

    print(json.dumps({"status": "success", "message": message}))

if __name__ == "__main__":
    main()
```

### Example 2: Complex Skill (Security Audit)

```python
# .claude/skills/assistant (using code analysis skills)/security-audit/scan_vulnerabilities.py

import json
import argparse
import re
from pathlib import Path
from typing import List, Dict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    args = parser.parse_args()

    with open(args.context) as f:
        context = json.load(f)

    codebase_path = Path(context.get("codebase_path", "."))
    results = scan_codebase(codebase_path)

    print(json.dumps(results, indent=2))


def scan_codebase(path: Path) -> Dict:
    """Scan codebase for vulnerabilities."""
    vulnerabilities = []

    # Scan all Python files
    for py_file in path.rglob("*.py"):
        vulns = scan_file(py_file)
        vulnerabilities.extend(vulns)

    score = calculate_score(vulnerabilities)

    return {
        "vulnerabilities": vulnerabilities,
        "score": score,
        "scanned_files": len(list(path.rglob("*.py")))
    }


def scan_file(file_path: Path) -> List[Dict]:
    """Scan file for vulnerability patterns."""
    vulnerabilities = []
    content = file_path.read_text()

    # Pattern: SQL injection
    if re.search(r'execute\(.*?\+.*?\)', content):
        vulnerabilities.append({
            "type": "SQL_INJECTION",
            "file": str(file_path),
            "severity": "HIGH",
            "message": "Potential SQL injection via string concatenation"
        })

    # Pattern: XSS
    if re.search(r'innerHTML\s*=', content):
        vulnerabilities.append({
            "type": "XSS",
            "file": str(file_path),
            "severity": "MEDIUM",
            "message": "Potential XSS via innerHTML"
        })

    # Pattern: Insecure deserialization
    if re.search(r'pickle\.loads?\(', content):
        vulnerabilities.append({
            "type": "INSECURE_DESERIALIZATION",
            "file": str(file_path),
            "severity": "HIGH",
            "message": "Insecure pickle usage"
        })

    return vulnerabilities


def calculate_score(vulnerabilities: List[Dict]) -> float:
    """Calculate security score (0-10)."""
    if not vulnerabilities:
        return 10.0

    # Deduct points based on severity
    score = 10.0
    for vuln in vulnerabilities:
        if vuln["severity"] == "HIGH":
            score -= 2.0
        elif vuln["severity"] == "MEDIUM":
            score -= 1.0
        else:
            score -= 0.5

    return max(0.0, score)


if __name__ == "__main__":
    main()
```

### Example 3: Hybrid Skill (Puppeteer Demo)

```python
# .claude/skills/assistant/demo-creator/create_puppeteer_demo.py

import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    args = parser.parse_args()

    with open(args.context) as f:
        context = json.load(f)

    feature_name = context["feature_name"]
    url = context.get("url", "http://localhost:8000")

    # Create demo using Puppeteer MCP
    demo_result = create_demo(feature_name, url)

    print(json.dumps(demo_result, indent=2))


def create_demo(feature: str, url: str) -> dict:
    """Create Puppeteer demo for feature.

    This would use Puppeteer MCP to:
    1. Navigate to URL
    2. Interact with feature
    3. Take screenshots
    4. Generate video

    For now, returns mock data.
    """
    # TODO: Integrate with Puppeteer MCP
    return {
        "screenshots": [
            f"demo_{feature}_1.png",
            f"demo_{feature}_2.png"
        ],
        "video": f"demo_{feature}.mp4",
        "steps": [
            "Navigate to application",
            f"Interact with {feature}",
            "Capture results"
        ]
    }


if __name__ == "__main__":
    main()
```

---

## Related Guidelines

- [GUIDELINE-001: Error Handling Best Practices](./GUIDELINE-001-error-handling.md)
- [GUIDELINE-002: Testing Strategy](./GUIDELINE-002-testing-strategy.md)
- [ADR-002: Integrate Claude Skills](../decisions/ADR-002-integrate-claude-skills.md)
- [SPEC-001: Claude Skills Integration](../specs/SPEC-001-claude-skills-integration.md)

---

## Conclusion

Creating Claude Skills requires:
1. **Clear purpose**: Know when to use skills vs. prompts
2. **Structured implementation**: Follow directory structure, metadata format
3. **Robust error handling**: Handle missing/invalid inputs gracefully
4. **Comprehensive testing**: Unit + integration + manual tests
5. **Documentation**: SKILL.md + agent skill catalog

Follow this guideline to create reliable, maintainable, and well-integrated skills for the MonolithicCoffeeMakerAgent system.

---

**Version**: 1.0
**Last Updated**: 2025-10-17
**Created By**: architect agent
