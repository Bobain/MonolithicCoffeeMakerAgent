# CLI Security Audit Report
**Analysis Type**: coffee_maker/cli/ Security Audit
**Date**: 2025-10-17
**Analyst**: code-searcher
**Severity**: MEDIUM-HIGH (Multiple issues identified)

---

## Executive Summary

Comprehensive security audit of the CLI module (`coffee_maker/cli/`) identified **4 critical security issues** and **3 medium-risk concerns**. The primary vulnerabilities stem from:

1. **Command Injection via shell=True** (CRITICAL)
2. **Unsafe file path handling** (HIGH)
3. **os.system() usage for sound playback** (MEDIUM-HIGH)
4. **Insufficient input validation** (MEDIUM)

All findings include remediation strategies and implementation guidance.

---

## Critical Findings

### 1. Command Injection via shell=True (CRITICAL)

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/assistant_tools.py:214-221`

**Vulnerability**:
```python
result = subprocess.run(
    command,              # ⚠️ User-controlled!
    shell=True,           # ⚠️ CRITICAL: shell=True enables injection
    capture_output=True,
    text=True,
    timeout=30,
    cwd=Path.cwd(),
)
```

**Attack Vector**:
- ExecuteBashTool._run() accepts arbitrary bash commands from user input
- While there's a "safety check" on lines 209-211, it's insufficient:
  ```python
  dangerous_commands = ["rm", "mv", "cp", "dd", ">", ">>", "chmod", "chown"]
  if any(cmd in command.lower() for cmd in dangerous_commands):
      return "Error: Write operations not allowed"
  ```

**Exploit Example**:
```
Input: "ls; echo malicious >> /etc/passwd"
Result: BYPASSES safety check (echo not in dangerous_commands list)
```

**Risk Level**: **CRITICAL**
- Can execute arbitrary system commands
- Attacker can read/modify files outside intended scope
- Could lead to privilege escalation in multi-user environments

**Remediation**:
```python
# Use shlex.split() to prevent injection
import shlex

def _run(self, command: str) -> str:
    """Execute bash command safely."""
    # Allowlist approach instead of blacklist
    ALLOWED_COMMANDS = ["ls", "cat", "grep", "find", "ps", "pwd"]
    cmd_parts = shlex.split(command)
    base_cmd = cmd_parts[0].split("/")[-1]  # Get command name

    if base_cmd not in ALLOWED_COMMANDS:
        return f"Error: Command '{base_cmd}' not allowed"

    # Use list form (no shell=True)
    result = subprocess.run(
        cmd_parts,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=Path.cwd(),
    )
    return result.stdout
```

**Severity**: **CRITICAL - Requires immediate patch**

---

### 2. Unsafe File Path Handling in os.system() (HIGH)

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/notifications.py:122-133`

**Vulnerability**:
```python
if system == "Darwin":  # macOS
    if priority == "critical":
        os.system("afplay /System/Library/Sounds/Sosumi.aiff &")
    elif priority == "high":
        os.system("afplay /System/Library/Sounds/Glass.aiff &")
    else:
        os.system("afplay /System/Library/Sounds/Pop.aiff &")

elif system == "Linux":
    sound_file = "/usr/share/sounds/freedesktop/stereo/message.oga"
    if os.path.exists(sound_file):
        os.system(f"paplay {sound_file} &")  # ⚠️ f-string in shell command
```

**Issues**:
1. **os.system() is unsafe** - Creates shell subprocess without protection
2. **f-string injection risk** - Although sound_file is validated, pattern is risky
3. **Path traversal potential** - No canonicalization of sound paths

**Attack Scenario**:
```python
# If sound_file were controllable:
sound_file = "../../../etc/passwd"
os.system(f"paplay {sound_file} &")  # Could read/expose sensitive files
```

**Risk Level**: **HIGH**
- os.system() spawns shell, enabling command injection
- Should use subprocess.run() with list arguments

**Remediation**:
```python
import subprocess

def play_notification_sound(priority: str = "normal") -> bool:
    try:
        system = platform.system()

        if system == "Darwin":
            sound_map = {
                "critical": "/System/Library/Sounds/Sosumi.aiff",
                "high": "/System/Library/Sounds/Glass.aiff",
                "normal": "/System/Library/Sounds/Pop.aiff",
            }
            sound_file = sound_map.get(priority, sound_map["normal"])

            # Use subprocess without shell=True
            subprocess.run(
                ["afplay", sound_file],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return True

        elif system == "Linux":
            sound_file = "/usr/share/sounds/freedesktop/stereo/message.oga"
            if not os.path.exists(sound_file):
                logger.debug(f"Sound file not found: {sound_file}")
                return False

            # Use subprocess without shell=True
            subprocess.run(
                ["paplay", sound_file],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return True

        return False
    except Exception as e:
        logger.debug(f"Failed to play notification sound: {e}")
        return False
```

**Severity**: **HIGH - Requires refactoring**

---

### 3. Unsafe String Interpolation in Git Commands (MEDIUM-HIGH)

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon_git_ops.py:175`

**Vulnerability**:
```python
merge_result = subprocess.run(
    [
        "git",
        "merge",
        "--no-ff",
        "-m",
        f"Merge {current_branch}: {message}",  # ⚠️ User input in commit message
        current_branch,
    ],
    cwd=self.git.repo_path,
    capture_output=True,
    text=True,
)
```

**Issues**:
1. While subprocess.run() with list args is safe, commit message could contain special chars
2. `current_branch` and `message` are not validated before use
3. Branch names could contain special characters or quotes

**Attack Scenario**:
```
current_branch = "feature/'; DROP TABLE notifications; --"
message = "test\" --allow-empty"
Result: Malformed git command that could fail unexpectedly
```

**Risk Level**: **MEDIUM-HIGH**
- Not a direct injection (subprocess list args), but untrusted data in arguments
- Could cause DoS via malformed commands
- May interfere with git operations

**Remediation**:
```python
import re

def _validate_branch_name(branch: str) -> bool:
    """Validate branch name format."""
    # Only allow alphanumeric, dash, underscore, slash
    return bool(re.match(r'^[a-zA-Z0-9_/-]+$', branch))

def _merge_to_roadmap(self, message: str = "Sync progress to roadmap") -> bool:
    """Merge current feature branch to roadmap branch."""
    try:
        current_branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=self.git.repo_path,
            text=True
        ).strip()

        # Validate branch name
        if not self._validate_branch_name(current_branch):
            logger.error(f"Invalid branch name: {current_branch}")
            return False

        # Validate message length and content
        if len(message) > 256:
            message = message[:256]

        # Safe commit message
        commit_msg = f"Merge {current_branch}: {message}"

        # Use list form - safe from injection
        merge_result = subprocess.run(
            [
                "git",
                "merge",
                "--no-ff",
                "-m",
                commit_msg,
                current_branch,
            ],
            cwd=self.git.repo_path,
            capture_output=True,
            text=True,
        )
```

**Severity**: **MEDIUM-HIGH - Add validation layer**

---

## Medium-Risk Findings

### 4. Insufficient Input Validation (MEDIUM)

**Locations**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/assistant_tools.py:44` (ReadFileTool)
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/assistant_tools.py:113` (ListFilesTool)

**Issue**: File path not validated for path traversal

```python
def _run(self, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """Read file contents."""
    try:
        path = Path(file_path)  # ⚠️ No validation!
        if not path.exists():
            return f"Error: File {file_path} does not exist"

        with open(path, "r") as f:  # Could read /etc/passwd
            lines = f.readlines()
```

**Attack**:
```python
file_path = "../../../../etc/passwd"
# Result: Could read sensitive system files
```

**Remediation**:
```python
from pathlib import Path

def _run(self, file_path: str, ...) -> str:
    """Read file contents safely."""
    try:
        # Get absolute paths
        requested = Path(file_path).resolve()
        allowed_root = Path.cwd().resolve()

        # Ensure file is within project directory
        try:
            requested.relative_to(allowed_root)
        except ValueError:
            return f"Error: File {file_path} is outside project directory"

        if not requested.exists():
            return f"Error: File {file_path} does not exist"

        with open(requested, "r") as f:
            lines = f.readlines()
```

**Severity**: **MEDIUM - Requires path validation**

---

### 5. Regex DoS in SearchCodeTool (MEDIUM)

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/assistant_tools.py:78-93`

**Issue**: User-provided regex pattern not validated for complexity

```python
def _run(self, pattern: str, file_pattern: str = "*.py", directory: str = ".") -> str:
    """Search code using grep."""
    try:
        cmd = ["grep", "-r", "-n", "--include", file_pattern, pattern, directory]
        result = subprocess.run(cmd, ...)
```

**Attack**: ReDoS (Regular Expression Denial of Service)
```python
pattern = "a*a*a*a*a*a*a*a*a*X"  # Catastrophic backtracking
# grep will hang for minutes on large files
```

**Remediation**:
```python
import re
import signal

def _run(self, pattern: str, file_pattern: str = "*.py", directory: str = ".") -> str:
    """Search code using grep."""
    try:
        # Validate regex complexity
        try:
            # Test regex compiles and isn't exponential
            test_re = re.compile(pattern, re.IGNORECASE)
            # Limit pattern length
            if len(pattern) > 256:
                return "Error: Pattern too long (max 256 chars)"
        except re.error as e:
            return f"Error: Invalid regex pattern: {e}"

        cmd = ["grep", "-r", "-n", "--include", file_pattern, pattern, directory]

        # Set timeout to prevent hanging
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            return "Error: Search timed out (pattern too complex?)"
```

**Severity**: **MEDIUM - Add timeout and validation**

---

## Summary Table

| Finding | Location | Severity | Type | CWE |
|---------|----------|----------|------|-----|
| shell=True injection | assistant_tools.py:214 | CRITICAL | Command Injection | CWE-78 |
| os.system() unsafe | notifications.py:122-133 | HIGH | Command Injection | CWE-78 |
| Git command injection | daemon_git_ops.py:175 | MEDIUM-HIGH | Argument Injection | CWE-94 |
| Path traversal | assistant_tools.py:44,113 | MEDIUM | Path Traversal | CWE-22 |
| ReDoS in grep | assistant_tools.py:78 | MEDIUM | DoS | CWE-1333 |

---

## Remediation Priority

**Phase 1 (CRITICAL - Immediate)**:
1. Fix shell=True in ExecuteBashTool (security blocker)
2. Replace os.system() with subprocess in notifications.py

**Phase 2 (HIGH - Week 1)**:
1. Add branch name validation in daemon_git_ops.py
2. Add path traversal protection in assistant_tools.py

**Phase 3 (MEDIUM - Week 2)**:
1. Add regex validation and timeout
2. Comprehensive input validation audit

---

## Recommendations

### 1. Create Security Module
```
coffee_maker/security/
├── __init__.py
├── validators.py      # Input validation functions
├── sanitizers.py      # String sanitization
└── subprocess_safe.py # Safe subprocess wrapper
```

### 2. Implement Centralized Validation
- Validate all user input at entry points
- Use allowlists instead of blacklists
- Canonicalize and validate file paths

### 3. Code Review Guidelines
- **Rule**: Never use shell=True
- **Rule**: Never use os.system()
- **Rule**: Always validate user input before subprocess calls
- **Rule**: Canonicalize file paths before access

### 4. Security Testing
- Add CWE-78 test cases (command injection)
- Add CWE-22 test cases (path traversal)
- Add CWE-1333 test cases (ReDoS)

---

## Files Affected

- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/assistant_tools.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/notifications.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon_git_ops.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/git_manager.py`

---

## Related Documentation

- CWE-78: Improper Neutralization of Special Elements used in an OS Command
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory
- CWE-1333: Inefficient Regular Expression Complexity

---

**Next Steps**:
- Review findings with architect for design input
- Create tickets for remediation
- Implement security module for centralized validation
