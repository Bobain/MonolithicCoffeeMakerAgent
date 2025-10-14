# PRIORITY 8: Migration Guide - Transitioning to Multi-AI Provider Support

**Version**: 1.0
**Created**: 2025-10-12
**Target Audience**: Developers migrating existing code to use the multi-provider system

---

## Table of Contents

1. [Overview](#overview)
2. [Why Migrate?](#why-migrate)
3. [Before You Start](#before-you-start)
4. [Migration Path](#migration-path)
5. [Code Examples](#code-examples)
6. [Testing Your Migration](#testing-your-migration)
7. [Rollback Strategy](#rollback-strategy)
8. [FAQ](#faq)

---

## Overview

This guide helps you transition from the Claude-only implementation to the multi-AI provider system. The migration is designed to be **incremental** and **backward-compatible**, allowing you to adopt the new system gradually.

### What's Changing

**Before** (Claude-only):
```python
# Direct Claude API/CLI usage
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

cli = ClaudeCLIInterface()
result = cli.execute_with_context(prompt="Implement feature", working_dir="/path")
```

**After** (Multi-provider):
```python
# Provider abstraction
from coffee_maker.ai_providers import get_provider

provider = get_provider()  # Defaults to Claude
result = provider.execute_prompt("Implement feature", working_dir="/path")
```

### Benefits of Migrating

1. **Flexibility**: Switch between Claude, OpenAI, and Gemini without code changes
2. **Resilience**: Automatic fallback if one provider fails
3. **Cost Control**: Built-in cost estimation and limits
4. **Future-Proof**: Easy to add new providers as they emerge
5. **Consistent API**: Same interface across all providers

---

## Why Migrate?

### Current Pain Points (Claude-only)

1. **Single Point of Failure**: If Claude is down, everything stops
2. **Regional Restrictions**: Some users can't access Claude
3. **Cost Inflexibility**: Can't choose cheaper models for simple tasks
4. **Hard-Coded Dependencies**: Claude logic scattered throughout codebase

### After Migration (Multi-provider)

1. **Automatic Fallback**: If Claude fails, automatically try OpenAI → Gemini
2. **Global Access**: Users choose their preferred/available provider
3. **Cost Optimization**: Use Gemini for high-volume tasks, Claude for complex ones
4. **Clean Architecture**: All AI logic through unified interface

---

## Before You Start

### Prerequisites

1. **Update Dependencies** (`pyproject.toml`):
```bash
poetry add openai google-generativeai tenacity tiktoken pyyaml
```

2. **Verify Installation**:
```bash
poetry install
python3 -c "from coffee_maker.ai_providers import get_provider; print('✅ Installation successful')"
```

3. **Set API Keys** (Optional - only for providers you want to use):
```bash
# Add to .env or export
export ANTHROPIC_API_KEY="sk-ant-xxxxx"  # Claude (existing)
export OPENAI_API_KEY="sk-xxxxx"         # OpenAI (new)
export GOOGLE_API_KEY="AIzaxxxxx"        # Gemini (new)
```

4. **Backup Your Code**:
```bash
git checkout -b backup-before-migration
git commit -am "Backup before multi-provider migration"
git checkout main
git checkout -b feature/multi-provider-migration
```

---

## Migration Path

### Phase 1: Non-Breaking Changes (Low Risk)

Start with **new code** using the provider system while keeping existing code unchanged.

#### Step 1.1: New Features Use Providers

For any **new** features, use the provider system:

```python
# NEW CODE - Use provider system
from coffee_maker.ai_providers import get_provider

def new_feature():
    provider = get_provider()
    result = provider.execute_prompt("Implement new feature")
    return result.content
```

**No changes to existing code required yet!**

#### Step 1.2: Add Provider Support to New Modules

New modules should accept a provider parameter:

```python
# coffee_maker/new_module/processor.py
from coffee_maker.ai_providers import BaseAIProvider, get_provider

class NewProcessor:
    def __init__(self, provider: BaseAIProvider = None):
        self.provider = provider or get_provider()

    def process(self, task: str):
        result = self.provider.execute_prompt(task)
        return result.content
```

### Phase 2: Gradual Refactoring (Medium Risk)

Refactor existing code module by module.

#### Step 2.1: Identify Claude Usage

Find all direct Claude API/CLI usage:

```bash
# Search for ClaudeAPI usage
grep -r "ClaudeAPI" coffee_maker/

# Search for ClaudeCLIInterface usage
grep -r "ClaudeCLIInterface" coffee_maker/

# Search for anthropic imports
grep -r "from anthropic import" coffee_maker/
```

**Common Patterns to Migrate**:
- `coffee_maker/autonomous/daemon.py:29` - ClaudeCLIInterface instantiation
- `coffee_maker/autonomous/daemon.py:118-124` - Direct CLI calls
- Any module importing `ClaudeAPI` or `ClaudeCLIInterface`

#### Step 2.2: Refactor Module by Module

**Example: Migrating `daemon.py`**

**Before**:
```python
# coffee_maker/autonomous/daemon.py
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

class CodeDeveloperDaemon:
    def __init__(self):
        self.claude_cli = ClaudeCLIInterface(model="claude-sonnet-4-5-20250929")

    def execute_priority(self, priority: str):
        prompt = f"Implement {priority} from docs/roadmap/ROADMAP.md"
        result = self.claude_cli.execute_with_context(
            prompt=prompt,
            working_dir=self.working_dir
        )
        return result
```

**After**:
```python
# coffee_maker/autonomous/daemon.py
from coffee_maker.ai_providers import FallbackStrategy, get_provider

class CodeDeveloperDaemon:
    def __init__(self, provider_name: str = None):
        # Option 1: Use specific provider
        # self.provider = get_provider(provider_name)

        # Option 2: Use fallback strategy (recommended)
        self.fallback_strategy = FallbackStrategy()

    def execute_priority(self, priority: str):
        prompt = f"Implement {priority} from docs/roadmap/ROADMAP.md"

        # Use fallback strategy for automatic retries
        result = self.fallback_strategy.execute_with_fallback(
            prompt=prompt,
            working_dir=self.working_dir
        )

        self.log(f"✅ Completed with {result.model}")
        return result
```

#### Step 2.3: Update Tests

**Before**:
```python
# tests/test_daemon.py
from coffee_maker.autonomous.daemon import CodeDeveloperDaemon

def test_daemon_execution():
    daemon = CodeDeveloperDaemon()
    result = daemon.execute_priority("PRIORITY 1")
    assert result.success
```

**After** (with provider mocking):
```python
# tests/test_daemon.py
from coffee_maker.autonomous.daemon import CodeDeveloperDaemon
from coffee_maker.ai_providers import ProviderResult
from unittest.mock import Mock, patch

def test_daemon_execution():
    # Mock provider
    mock_provider = Mock()
    mock_provider.execute_prompt.return_value = ProviderResult(
        content="Feature implemented",
        model="claude-sonnet-4-5-20250929",
        usage={"input_tokens": 100, "output_tokens": 200},
        stop_reason="end_turn"
    )

    with patch('coffee_maker.ai_providers.get_provider', return_value=mock_provider):
        daemon = CodeDeveloperDaemon()
        result = daemon.execute_priority("PRIORITY 1")
        assert result.success
```

### Phase 3: Configuration Migration (Low Risk)

Update configuration to use the new system.

#### Step 3.1: Configure Providers

Create or verify `config/ai_providers.yaml`:

```yaml
default_provider: claude  # Keep Claude as default for backward compatibility

providers:
  claude:
    enabled: true
    use_cli: true  # Maintains existing behavior
    model: claude-sonnet-4-5-20250929

  openai:
    enabled: true  # Enable for fallback
    model: gpt-4-turbo

  gemini:
    enabled: true  # Enable for fallback
    model: gemini-1.5-pro

fallback:
  enabled: true
  fallback_order:
    - claude    # Try Claude first (existing behavior)
    - openai    # Fall back to OpenAI if Claude fails
    - gemini    # Last resort
```

#### Step 3.2: Environment Variables

Update `.env.example` and documentation:

```bash
# .env.example

# Claude (existing - still required by default)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# OpenAI (optional - for fallback)
OPENAI_API_KEY=sk-xxxxx

# Google Gemini (optional - for fallback)
GOOGLE_API_KEY=AIzaxxxxx
```

### Phase 4: Enable Fallback (High Value, Low Risk)

The safest migration: Keep using Claude by default, but enable automatic fallback.

```python
# coffee_maker/autonomous/daemon.py
from coffee_maker.ai_providers import FallbackStrategy

class CodeDeveloperDaemon:
    def __init__(self):
        # Automatic fallback: Claude → OpenAI → Gemini
        self.fallback_strategy = FallbackStrategy()

    def execute_priority(self, priority: str):
        try:
            result = self.fallback_strategy.execute_with_fallback(
                prompt=f"Implement {priority}",
                working_dir=self.working_dir
            )
            return result
        except AllProvidersFailedError as e:
            self.notify_user("All AI providers failed", str(e))
            raise
```

**Benefits**:
- ✅ Keeps Claude as primary (existing behavior)
- ✅ Adds resilience with automatic fallback
- ✅ Zero code changes needed elsewhere
- ✅ Works even if OpenAI/Gemini keys aren't set

---

## Code Examples

### Example 1: Minimal Migration (Daemon Only)

If you want to migrate **only** the daemon:

```python
# coffee_maker/autonomous/daemon.py
from coffee_maker.ai_providers import FallbackStrategy, get_provider
from typing import Optional

class CodeDeveloperDaemon:
    def __init__(
        self,
        provider_name: Optional[str] = None,
        use_fallback: bool = True
    ):
        if use_fallback:
            self.provider = FallbackStrategy()
        else:
            self.provider = get_provider(provider_name)

    def execute_priority(self, priority: str):
        """Execute priority with automatic fallback."""
        result = self.provider.execute_with_fallback(
            prompt=f"Read docs/roadmap/ROADMAP.md and implement {priority}",
            working_dir=self.working_dir,
            check_cost=True  # Enable cost checking
        )

        self.log(f"Completed {priority} using {result.model}")
        return result
```

**Usage**:
```bash
# Use default (Claude with fallback)
poetry run code-developer

# Use specific provider (no fallback)
DEFAULT_AI_PROVIDER=openai poetry run code-developer
```

### Example 2: Custom Module Migration

Migrate a custom module:

**Before**:
```python
# coffee_maker/custom/analyzer.py
from coffee_maker.autonomous.claude_api_interface import ClaudeAPI

class CodeAnalyzer:
    def __init__(self):
        self.claude = ClaudeAPI()

    def analyze_code(self, code: str):
        prompt = f"Analyze this code:\n{code}"
        result = self.claude.complete(prompt)
        return result.content
```

**After**:
```python
# coffee_maker/custom/analyzer.py
from coffee_maker.ai_providers import BaseAIProvider, get_provider

class CodeAnalyzer:
    def __init__(self, provider: BaseAIProvider = None):
        self.provider = provider or get_provider()

    def analyze_code(self, code: str):
        prompt = f"Analyze this code:\n{code}"
        result = self.provider.execute_prompt(prompt)
        return result.content
```

### Example 3: Cost-Aware Migration

Add cost controls:

```python
from coffee_maker.ai_providers import FallbackStrategy, CostLimitExceededError

class SmartDaemon:
    def __init__(self):
        self.fallback = FallbackStrategy()

    def execute_task(self, task: str):
        # Estimate cost before executing
        provider = get_provider()
        estimated_cost = provider.estimate_cost(task)

        if estimated_cost > 1.0:
            self.log(f"⚠️  High cost: ${estimated_cost:.2f}, using cheaper provider")
            # Use Gemini for expensive tasks
            provider = get_provider('gemini')
            result = provider.execute_prompt(task)
        else:
            # Use fallback strategy for normal tasks
            result = self.fallback.execute_with_fallback(
                prompt=task,
                check_cost=True
            )

        return result
```

---

## Testing Your Migration

### Step 1: Unit Tests

Test each migrated module:

```bash
# Run specific test file
pytest tests/unit/test_daemon.py -v

# Run all tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=coffee_maker --cov-report=html
```

### Step 2: Integration Tests

Test with real providers (requires API keys):

```python
# tests/integration/test_providers.py
import pytest
from coffee_maker.ai_providers import get_provider, list_available_providers

def test_all_providers():
    """Test all available providers."""
    available = list_available_providers()

    for provider_name in available:
        provider = get_provider(provider_name)
        result = provider.execute_prompt("Say 'Hello, World!'")

        assert result.success
        assert "Hello" in result.content
        print(f"✅ {provider_name}: {result.model}")
```

Run integration tests:
```bash
# Set all API keys first
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
export OPENAI_API_KEY="sk-xxxxx"
export GOOGLE_API_KEY="AIzaxxxxx"

# Run integration tests
pytest tests/integration/ -v --log-cli-level=INFO
```

### Step 3: Manual Testing

Test the daemon end-to-end:

```bash
# Terminal 1: Start daemon with Claude (default)
poetry run code-developer --verbose

# Terminal 2: Start daemon with OpenAI
DEFAULT_AI_PROVIDER=openai poetry run code-developer --verbose

# Terminal 3: Start daemon with fallback enabled
poetry run code-developer --verbose --fallback
```

### Step 4: Fallback Testing

Test fallback behavior:

```python
# tests/integration/test_fallback.py
from coffee_maker.ai_providers import FallbackStrategy, get_provider
from unittest.mock import patch

def test_fallback_on_rate_limit():
    """Test fallback when Claude is rate-limited."""
    strategy = FallbackStrategy()

    # Mock Claude to fail with rate limit
    with patch('coffee_maker.ai_providers.providers.claude_provider.ClaudeProvider.execute_prompt') as mock_claude:
        mock_claude.side_effect = RateLimitError("Rate limited")

        # Should automatically fall back to OpenAI
        result = strategy.execute_with_fallback(
            prompt="Test fallback",
            providers=['claude', 'openai', 'gemini']
        )

        assert result.success
        assert result.model.startswith('gpt')  # OpenAI model
```

---

## Rollback Strategy

If you encounter issues, rollback is easy:

### Option 1: Git Rollback

```bash
# Rollback to before migration
git checkout backup-before-migration

# Or revert specific commits
git revert <commit-hash>
```

### Option 2: Keep Old Code Alongside New

During migration, keep both systems:

```python
# coffee_maker/autonomous/daemon.py
USE_MULTI_PROVIDER = os.getenv('USE_MULTI_PROVIDER', 'false').lower() == 'true'

class CodeDeveloperDaemon:
    def __init__(self):
        if USE_MULTI_PROVIDER:
            from coffee_maker.ai_providers import FallbackStrategy
            self.provider = FallbackStrategy()
        else:
            # Old system (fallback)
            from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
            self.provider = ClaudeCLIInterface()
```

Toggle via environment variable:
```bash
# Use new system
USE_MULTI_PROVIDER=true poetry run code-developer

# Use old system
poetry run code-developer
```

### Option 3: Feature Flag

Use a feature flag system:

```python
# coffee_maker/config/features.py
FEATURES = {
    'multi_provider': os.getenv('FEATURE_MULTI_PROVIDER', 'false').lower() == 'true'
}

# In daemon.py
from coffee_maker.config.features import FEATURES

if FEATURES['multi_provider']:
    # Use new provider system
    pass
else:
    # Use old Claude-only system
    pass
```

---

## FAQ

### Q: Do I have to migrate all at once?

**A**: No! Migrate incrementally:
1. Start with new features using providers
2. Refactor one module at a time
3. Keep old code working during migration

### Q: Will this break existing functionality?

**A**: No, if done correctly:
- Claude remains the default provider
- Existing Claude CLI behavior is preserved
- Fallback only activates on failures

### Q: Do I need API keys for all providers?

**A**: No, only for:
- **Claude**: Required if using default config
- **OpenAI/Gemini**: Optional, only needed for fallback

### Q: What if I only want Claude?

**A**: Set `fallback.enabled: false` in `config/ai_providers.yaml`:

```yaml
default_provider: claude

fallback:
  enabled: false  # Disable fallback

providers:
  claude:
    enabled: true
  openai:
    enabled: false  # Disable OpenAI
  gemini:
    enabled: false  # Disable Gemini
```

### Q: How do I test without real API calls?

**A**: Mock the providers:

```python
from unittest.mock import Mock, patch
from coffee_maker.ai_providers import ProviderResult

mock_result = ProviderResult(
    content="Mocked response",
    model="mock-model",
    usage={"input_tokens": 10, "output_tokens": 20},
    stop_reason="end_turn"
)

with patch('coffee_maker.ai_providers.get_provider') as mock_get:
    mock_provider = Mock()
    mock_provider.execute_prompt.return_value = mock_result
    mock_get.return_value = mock_provider

    # Your test code here
```

### Q: What's the performance impact?

**A**: Minimal:
- Provider abstraction: <1ms overhead
- Fallback logic: Only runs on failures
- Token counting: Cached where possible

### Q: Can I add custom providers?

**A**: Yes! Create a class extending `BaseAIProvider`:

```python
from coffee_maker.ai_providers.base import BaseAIProvider, ProviderResult

class MyCustomProvider(BaseAIProvider):
    def execute_prompt(self, prompt, **kwargs):
        # Your implementation
        return ProviderResult(...)

    # Implement other abstract methods...
```

Register it:
```python
from coffee_maker.ai_providers.provider_factory import register_provider

register_provider('my_provider', MyCustomProvider)
```

### Q: How do I monitor which provider is being used?

**A**: Check logs:

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
poetry run code-developer

# Logs will show:
# INFO: Using provider: claude
# INFO: Completed with model: claude-sonnet-4-5-20250929
# WARNING: Claude failed, falling back to OpenAI
# INFO: Completed with model: gpt-4-turbo
```

Or check result metadata:
```python
result = provider.execute_prompt("Task")
print(f"Used model: {result.model}")
print(f"Provider: {result.metadata.get('provider')}")
```

---

## Summary

### Migration Checklist

- [ ] Update dependencies (openai, google-generativeai, etc.)
- [ ] Verify installation (`from coffee_maker.ai_providers import get_provider`)
- [ ] Set API keys (at least ANTHROPIC_API_KEY)
- [ ] Create git backup branch
- [ ] Configure `config/ai_providers.yaml`
- [ ] Migrate daemon.py to use FallbackStrategy
- [ ] Update tests to mock providers
- [ ] Run unit tests (`pytest tests/unit/`)
- [ ] Run integration tests (`pytest tests/integration/`)
- [ ] Test fallback manually (disable Claude temporarily)
- [ ] Update documentation
- [ ] Deploy and monitor

### Next Steps

1. **Read**: [PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md](./PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md) - Full usage guide
2. **Review**: [PRIORITY_8_TECHNICAL_SPEC.md](./PRIORITY_8_TECHNICAL_SPEC.md) - Architecture details
3. **Compare**: [PROVIDER_COMPARISON.md](./PROVIDER_COMPARISON.md) - Provider benchmarks
4. **Explore**: Example scripts in `examples/priority_8/`

### Support

- **Issues**: Check [ROADMAP.md](./ROADMAP.md) for known issues
- **Questions**: See [PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md](./PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md) FAQ section
- **Bugs**: Report in GitHub Issues

---

**Happy Migrating! 🚀**

*Last Updated: 2025-10-12*
