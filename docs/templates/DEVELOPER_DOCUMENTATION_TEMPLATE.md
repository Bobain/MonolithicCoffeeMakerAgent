# Developer Documentation Template

**Purpose**: This template defines what documentation the developer MUST create when implementing any feature, so that assistants can effectively help users.

**When to use**: Every time you implement a feature, user story, or priority.

**Who needs this**: Assistants helping users, project managers answering questions, future developers

---

## 📋 Required Documentation Checklist

When implementing [FEATURE_NAME], you must create:

- [ ] **1. User Guide** - How to use the feature
- [ ] **2. API Reference** - Commands/functions (if applicable)
- [ ] **3. Troubleshooting** - Common errors and solutions
- [ ] **4. Changelog Entry** - What changed
- [ ] **5. Updated Technical Spec** - Actual implementation vs plan

---

## 1. User Guide

**File**: Either create new `docs/USER_GUIDE_[FEATURE].md` or add section to existing user guide

**Template**:

```markdown
# [Feature Name] - User Guide

## What is [Feature]?

[1-2 sentence description of what this feature does and why it's useful]

## Quick Start (2 minutes)

[Simplest possible example to get started]

### Step 1: [First Step]
```bash
command-example
```

**Expected Output**:
```
output example
```

### Step 2: [Second Step]
```bash
next-command
```

## Common Use Cases

### Use Case 1: [Common Scenario]

**Scenario**: [When would user do this]

**Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Example**:
```bash
# Example commands
command --option value
```

**Result**: [What happens]

### Use Case 2: [Another Scenario]
[Repeat format]

## All Available Options

| Option | Description | Example | Default |
|--------|-------------|---------|---------|
| `--option` | What it does | `cmd --option value` | `default` |

## When to Use vs When Not to Use

✅ **Use this feature when**:
- You need to [scenario 1]
- You want to [scenario 2]

❌ **Don't use this feature when**:
- You just need [simpler alternative]
- The use case is [not appropriate scenario]

## Examples

### Example 1: [Descriptive Name]
```bash
# Complete working example
command with parameters
```

**What this does**: [Explanation]

### Example 2: [Another Example]
[Repeat]

## Related Features

- [Related Feature 1]: [How they work together]
- [Related Feature 2]: [Connection]

## Next Steps

- [What to learn next]
- [Advanced features to explore]
```

---

## 2. API Reference (if applicable)

**File**: Create `docs/API_REFERENCE_[FEATURE].md` or add section to existing API docs

**Template**:

```markdown
# [Feature Name] - API Reference

## Overview

[Brief description of the API/interface]

## Functions/Commands

### function_name()

**Description**: [What this function does]

**Parameters**:
- `param1` (type, required/optional): Description
- `param2` (type, required/optional): Description

**Returns**:
- Type: [return type]
- Description: [what it returns]

**Raises/Errors**:
- `ErrorType`: When [condition]

**Example**:
```python
result = function_name(param1="value", param2=123)
print(result)  # Output: expected output
```

**Real-World Use Case**:
```python
# Practical example
from module import function_name

# Common pattern
result = function_name(
    param1="real value",
    param2=456
)

if result.success:
    print("Success!")
```

### command-name

**Description**: [What this command does]

**Syntax**:
```bash
command-name [options] <required-arg> [optional-arg]
```

**Options**:
| Option | Type | Required | Description | Default |
|--------|------|----------|-------------|---------|
| `--flag` | bool | No | What it does | `false` |
| `--value` | string | Yes | Parameter desc | None |

**Exit Codes**:
- `0`: Success
- `1`: Error type 1
- `2`: Error type 2

**Examples**:
```bash
# Basic usage
command-name --value "hello"

# Advanced usage with all options
command-name --flag --value "world" optional-arg

# Error case
command-name  # Missing required --value
# Error: --value is required
```

## Classes (if applicable)

### ClassName

**Description**: [What this class does]

**Constructor**:
```python
ClassName(param1, param2=default)
```

**Attributes**:
- `attribute1` (type): Description
- `attribute2` (type): Description

**Methods**:

#### method_name()
[Follow function template above]

**Example**:
```python
obj = ClassName(param1="value")
result = obj.method_name()
```

## Error Reference

| Error Code/Name | Meaning | Solution |
|-----------------|---------|----------|
| `ERROR_1` | Why this happens | How to fix |
| `ERROR_2` | Cause | Resolution |
```

---

## 3. Troubleshooting

**File**: Add section to `docs/TROUBLESHOOTING.md` or create new file

**Template**:

```markdown
# [Feature Name] - Troubleshooting

## Common Issues

### Issue 1: [Error Message or Symptom]

**Symptoms**:
```
Error message or what user sees
```

**Cause**: [Why this happens]

**Solution**:
```bash
# Step 1: Check X
command to diagnose

# Step 2: Fix Y
command to fix

# Step 3: Verify
command to verify fix
```

**Prevention**: [How to avoid this in future]

---

### Issue 2: Feature Not Working as Expected

**Symptoms**: [What user sees]

**Possible Causes**:

1. **Cause A**: [Description]
   - Check: `command to check`
   - Fix: `command to fix`

2. **Cause B**: [Description]
   - Check: `command to check`
   - Fix: `command to fix`

---

### Issue 3: Performance Problems

**Symptoms**: [Slow, hanging, high CPU, etc.]

**Diagnosis**:
```bash
# Check resource usage
diagnostic command

# Check logs
log command
```

**Solutions**:
1. [Solution 1]: `command`
2. [Solution 2]: `command`

---

## Debug Mode

**Enable debug output**:
```bash
# Set environment variable
export DEBUG=1

# Or use flag
command --debug
```

**Read logs**:
```bash
# Location of logs
cat /path/to/logs

# Follow live
tail -f /path/to/logs
```

---

## Getting Help

If none of these solutions work:

1. **Check logs**: [where logs are located]
2. **Minimal reproduction**: [how to create minimal test case]
3. **Report issue**: [where to report]

**Include in bug report**:
- Command used
- Full error message
- OS and version
- Relevant logs
```

---

## 4. Changelog Entry

**File**: Add to `docs/CHANGELOG.md`

**Template**:

```markdown
## [Version] - YYYY-MM-DD

### Added
- [Feature Name]: [Brief description]
  - [Specific capability 1]
  - [Specific capability 2]
  - See [docs/USER_GUIDE_FEATURE.md] for usage

### Changed
- [What changed]: [Why and how it affects users]
  - **Breaking Change**: [If any]
  - **Migration**: [How to update code]

### Fixed
- [What was fixed]: [Issue description]

### Deprecated
- [What's deprecated]: [Alternative to use]
  - Will be removed in [version]

### Security
- [Security fix]: [What was patched]
```

---

## 5. Updated Technical Spec

**File**: Update `docs/US-XXX_TECHNICAL_SPEC.md` or `docs/roadmap/PRIORITY_X_TECHNICAL_SPEC.md`

**Add this section AFTER implementation**:

```markdown
## Implementation Results

### What Was Actually Built

[Describe what was implemented - may differ from original plan]

**Deviations from Original Spec**:
- Changed X because Y
- Added Z for reason W
- Removed A due to B

### How It Works

[Explain the actual implementation]

**Architecture**:
```
[Updated architecture diagram or description]
```

**Key Components**:
1. Component A: [What it does, where it is]
2. Component B: [What it does, where it is]

**Data Flow**:
```
Input → Processing → Output
```

### Performance Characteristics

- Response time: [actual measurements]
- Resource usage: [CPU, memory]
- Scalability: [tested limits]

### Known Limitations

- [Limitation 1]: [Workaround]
- [Limitation 2]: [Future improvement]

### Future Improvements

- [Improvement 1]: [Why and when]
- [Improvement 2]: [Priority]
```

---

## Example: Complete Documentation for a Feature

**Feature**: `/status` command (from US-009)

### ✅ What Developer Should Have Created:

**1. User Guide** (`docs/USER_GUIDE_DAEMON_CONTROL.md`):
```markdown
# Daemon Control - User Guide

## What is Daemon Control?

Daemon Control allows you to start, stop, and monitor the code_developer
daemon directly from the project-manager chat interface.

## Quick Start

```bash
poetry run project-manager chat

# In chat:
/status  # Check if daemon is running
```

[... rest of user guide following template]
```

**2. API Reference** (`docs/API_REFERENCE_DAEMON_CONTROL.md`):
```markdown
# Daemon Control - API Reference

## Commands

### /status

**Description**: Show detailed daemon status

**Syntax**: `/status`

**Output**:
```
🟢 Daemon Status: RUNNING
- PID: 12345
- Status: WORKING
- Current Task: US-009
- Uptime: 2 hours
- CPU: 15.2%
- Memory: 45.3 MB
```

[... rest of API reference]
```

**3. Troubleshooting** (section in `docs/TROUBLESHOOTING.md`):
```markdown
## Daemon Control Issues

### Issue: Daemon Won't Start

**Symptoms**:
```
❌ Failed to Start Daemon
```

**Solution**:
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY='your-key'
```

[... rest of troubleshooting]
```

**4. Changelog Entry**:
```markdown
## [0.2.0] - 2025-10-10

### Added
- **Daemon Control** (US-009): Monitor and control daemon from chat
  - `/status` command shows daemon status
  - `/start` launches daemon
  - `/stop` shuts down daemon
  - Bidirectional communication via natural language
  - See docs/USER_GUIDE_DAEMON_CONTROL.md
```

**5. Updated Technical Spec**:
```markdown
# US-009 Technical Specification

[... original spec ...]

## Implementation Results

### What Was Actually Built

Implemented all 4 phases of process management with 18/18 acceptance
criteria met. Key addition: Natural language detection allows users to
send commands like "Ask daemon to implement X" without using /commands.

[... rest of implementation results]
```

---

## ❌ What Assistants Can't Do Without These Docs

**Without User Guide**:
- Assistant: "I don't know how to use /status command, check the code?"
- User: "That's not helpful!"

**Without API Reference**:
- User: "What parameters does create_notification() take?"
- Assistant: "Let me guess... probably title and message?"
- User: "Wrong! It failed!"

**Without Troubleshooting**:
- User: "Daemon won't start, help!"
- Assistant: "Umm... try restarting your computer?"
- User: "That's terrible advice!"

**Without Changelog**:
- User: "What changed in this version?"
- Assistant: "I have no idea what was added."

**Without Implementation Results**:
- User: "Why doesn't it work like the spec says?"
- Assistant: "The spec might be outdated, I don't know what actually was built."

---

## ✅ Definition of Done (Updated)

**A feature is NOT complete until developer has created**:

- [ ] ✅ Code implementation working
- [ ] ✅ Tests passing
- [ ] ✅ **User Guide section** (how to use it)
- [ ] ✅ **API Reference** (if applicable)
- [ ] ✅ **Troubleshooting section** (common errors)
- [ ] ✅ **Changelog entry** (what changed)
- [ ] ✅ **Updated Technical Spec** (implementation results)
- [ ] ✅ User validated

**Remember**: If assistants can't help users with your feature, the feature isn't done!

---

## 📝 Quick Reference

| Document | Purpose | Audience |
|----------|---------|----------|
| User Guide | How to use | End users |
| API Reference | Function/command details | Developers, assistants |
| Troubleshooting | Error solutions | End users, support |
| Changelog | What changed | All users |
| Tech Spec (updated) | How it works | Developers, PM |

---

**Questions?** See [COLLABORATION_METHODOLOGY.md](../COLLABORATION_METHODOLOGY.md) Section 6 (Definition of Done)

---

**Version**: 1.0
**Created**: 2025-10-10 (US-011)
**Maintained By**: project_manager
