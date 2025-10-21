# Claude CLI Mode - Default Backend for Code Developer Daemon

**Status**: ✅ Implemented (Priority 2.5 - US-004)
**Date**: October 2025

---

## Overview

The `code-developer` daemon **uses Claude CLI by default** instead of the Anthropic API. This means:

- ✅ Uses your existing **Claude subscription** (€200/month)
- ✅ **No API credits required**
- ✅ Same functionality as API mode
- ✅ Automatic fallback guidance if Claude CLI not installed

---

## Quick Start

### Running the Daemon

```bash
# Default mode (Claude CLI)
poetry run code-developer --auto-approve

# Force API mode (requires ANTHROPIC_API_KEY)
poetry run code-developer --use-api --auto-approve
```

### If Claude CLI Not Installed

When you run the daemon without Claude CLI installed, you'll see:

```
======================================================================
⚠️  Claude CLI not found (default mode)
======================================================================

Claude CLI not found at: /opt/homebrew/bin/claude

The daemon uses Claude CLI by default (uses your Claude subscription).

📋 CHOOSE AN OPTION:

  Option A: Install Claude CLI (Recommended)
  ─────────────────────────────────────────
    1. Install from: https://docs.claude.com/docs/claude-cli
    2. Verify: claude --version
    3. Run: code-developer --auto-approve

  Option B: Use Anthropic API (Requires Credits)
  ───────────────────────────────────────────────
    1. Get API key: https://console.anthropic.com/
    2. Set: export ANTHROPIC_API_KEY='your-key'
    3. Run: code-developer --use-api --auto-approve

======================================================================
```

---

## Why Claude CLI is the Default

### Cost Efficiency

| Mode | Cost Model | Best For |
|------|-----------|----------|
| **Claude CLI (default)** | €200/month subscription | Regular users with existing subscription |
| **Anthropic API** | Pay-per-token (~$3-15 per million tokens) | One-time tasks, API integrations |

### Benefits

1. **No Additional Costs**: Uses your existing Claude subscription
2. **Unlimited Usage**: No per-request billing within subscription
3. **Familiar Authentication**: Same login as Claude web/CLI
4. **Simplified Setup**: No API key management needed

---

## Installation Guide

### Installing Claude CLI

```bash
# macOS (Homebrew)
brew install claude

# Verify installation
claude --version

# Test it works
claude -p <<< "Hello"
```

For other platforms, see: https://docs.claude.com/docs/claude-cli

### Configuration

The daemon looks for Claude CLI at `/opt/homebrew/bin/claude` by default.

To use a different path:

```bash
poetry run code-developer --claude-path /usr/local/bin/claude --auto-approve
```

---

## How It Works

### Architecture

```
┌─────────────────────┐
│  code-developer     │
│     daemon          │
└──────────┬──────────┘
           │
           ├─────────────────────┐
           │                     │
    ┌──────▼──────────┐   ┌─────▼────────────┐
    │  ClaudeCLIInterface│   │  ClaudeAPI     │
    │  (default)          │   │  (--use-api)   │
    └──────┬──────────┘   └─────┬────────────┘
           │                     │
    ┌──────▼──────────┐   ┌─────▼────────────┐
    │  claude CLI      │   │  Anthropic API   │
    │  (subscription)  │   │  (API credits)   │
    └──────────────────┘   └──────────────────┘
```

### Drop-In Replacement Pattern

Both `ClaudeCLIInterface` and `ClaudeAPI` implement the **same interface**:

```python
class ClaudeInterface:
    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> APIResult:
        """Execute a prompt and return result."""
        ...
```

This allows the daemon to **switch backends transparently** without code changes.

### Execution Flow

```python
# 1. Daemon initializes appropriate backend
if use_cli_mode:
    self.claude = ClaudeCLIInterface(
        claude_path="/opt/homebrew/bin/claude",
        model="claude-sonnet-4"
    )
else:
    self.claude = ClaudeAPI(model="claude-sonnet-4")

# 2. Execute prompt (same interface for both)
result = self.claude.execute_prompt(
    prompt="Read docs/roadmap/ROADMAP.md and implement PRIORITY 2.6",
    timeout=3600
)

# 3. Handle result (same format for both)
if result.success:
    print(f"✅ Complete! Tokens: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")
else:
    print(f"❌ Error: {result.error}")
```

---

## Technical Details

### ClaudeCLIInterface Implementation

**File**: `coffee_maker/autonomous/claude_cli_interface.py`

```python
class ClaudeCLIInterface:
    """Interface to Claude via CLI instead of Anthropic API.

    Uses subprocess to execute claude CLI in non-interactive mode:
    - `claude -p`: Print mode (non-interactive)
    - `--dangerously-skip-permissions`: Skip file access confirmations
    """

    def execute_prompt(self, prompt: str, ...) -> APIResult:
        """Execute via subprocess.run()."""
        cmd = [
            self.claude_path,
            "-p",  # Print mode
            "--model", self.model,
            "--dangerously-skip-permissions",
        ]

        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return APIResult(
            content=result.stdout.strip(),
            model=self.model,
            usage={
                "input_tokens": len(prompt) // 4,  # Estimated
                "output_tokens": len(result.stdout) // 4,
            },
            stop_reason="end_turn",
        )
```

### APIResult Format

Both backends return the same `APIResult` dataclass:

```python
@dataclass
class APIResult:
    content: str              # Claude's response
    model: str                # Model used (e.g., "claude-sonnet-4")
    usage: dict               # {"input_tokens": 1234, "output_tokens": 5678}
    stop_reason: str          # "end_turn", "timeout", or "error"
    error: Optional[str]      # Error message if failed

    @property
    def success(self) -> bool:
        return self.error is None
```

---

## Switching Between Modes

### Default: Claude CLI

```bash
# Just run it
poetry run code-developer --auto-approve

# Daemon output:
# Backend: Claude CLI (subscription)
# ✅ Using Claude CLI mode (subscription)
```

### Force API Mode

```bash
# Set API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Run with --use-api
poetry run code-developer --use-api --auto-approve

# Daemon output:
# Backend: Anthropic API (credits)
# ✅ Using Claude API mode (requires credits)
```

---

## Troubleshooting

### Claude CLI Not Found

**Error**:
```
⚠️  Claude CLI not found (default mode)
```

**Solution**:
```bash
# Install Claude CLI
brew install claude

# Or specify custom path
poetry run code-developer --claude-path /path/to/claude --auto-approve
```

### API Key Not Set (--use-api mode)

**Error**:
```
❌ ERROR: ANTHROPIC_API_KEY not set!
```

**Solution**:
```bash
# Get API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY='sk-ant-...'

# Run again
poetry run code-developer --use-api --auto-approve
```

### Claude CLI Timeout

**Symptom**: Daemon hangs during execution

**Solution**:
```bash
# Increase timeout
poetry run code-developer --auto-approve --verbose

# Check Claude CLI directly
claude -p <<< "Hello"
```

---

## Testing

### Test Claude CLI Availability

```bash
# Check if installed
which claude
# Output: /opt/homebrew/bin/claude

# Test basic execution
claude -p --dangerously-skip-permissions <<< "Hello, respond with just 'OK'"
# Output: OK
```

### Test Daemon with CLI Mode

```bash
# Test with small task
poetry run code-developer --auto-approve --sleep 60
```

### Test Daemon with API Mode

```bash
# Set API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Test with API
poetry run code-developer --use-api --auto-approve --sleep 60
```

---

## Performance Comparison

| Metric | Claude CLI | Anthropic API |
|--------|-----------|---------------|
| **Latency** | ~2-5s (subprocess overhead) | ~1-3s (direct HTTP) |
| **Token Estimation** | Rough (1 char ≈ 0.25 tokens) | Exact (from API) |
| **Cost** | Fixed (subscription) | Variable (per-token) |
| **Rate Limits** | Subscription limits | API tier limits |
| **Best Use Case** | Daily daemon runs | Bursts, integrations |

---

## Future Improvements

### Potential Enhancements

1. **Token Counting**: Use `tiktoken` for accurate token estimates in CLI mode
2. **Streaming**: Support streaming responses from CLI (if available)
3. **Caching**: Cache CLI results for repeated prompts
4. **Auto-Detection**: Automatically switch to API if CLI unavailable

### Related User Stories

- **US-004**: Claude CLI integration (✅ Complete)
- **US-006**: Enhanced UX with streaming (🔄 Sprint 7)
- **Future**: WebSocket-based communication for real-time updates

---

## References

- **Claude CLI Docs**: https://docs.claude.com/docs/claude-cli
- **Anthropic API**: https://docs.anthropic.com/
- **Implementation**: `coffee_maker/autonomous/claude_cli_interface.py`
- **CLI Tool**: `coffee_maker/autonomous/daemon_cli.py`

---

## Summary

✅ **Claude CLI is now the default backend** for the code-developer daemon
✅ **Automatic fallback guidance** when CLI not installed
✅ **Drop-in replacement pattern** allows transparent backend switching
✅ **Cost-efficient** for users with existing Claude subscriptions

**Next Steps**:
1. Install Claude CLI: `brew install claude`
2. Run daemon: `poetry run code-developer --auto-approve`
3. Enjoy autonomous development with your existing subscription!

---

**Last Updated**: October 10, 2025
**Implementation Status**: ✅ Complete (US-004)
