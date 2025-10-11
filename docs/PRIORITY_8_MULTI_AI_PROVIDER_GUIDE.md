# PRIORITY 8: Multi-AI Provider Support - Complete Guide

## Overview

The Multi-AI Provider Support system allows the `code-developer` daemon to work with multiple AI providers (Claude, OpenAI, Gemini) seamlessly. This removes the Claude-only barrier, provides cost flexibility, and ensures the daemon continues working even if one provider fails.

**Status**: ✅ Complete
**Impact**: ⭐⭐⭐⭐⭐ (Critical for user adoption)
**Strategic Goal**: Increase user adoption by supporting multiple AI providers

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Supported Providers](#supported-providers)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Provider Comparison](#provider-comparison)
7. [Fallback Strategy](#fallback-strategy)
8. [Cost Management](#cost-management)
9. [Integration with Daemon](#integration-with-daemon)
10. [Troubleshooting](#troubleshooting)
11. [API Reference](#api-reference)

---

## Quick Start

### 1. Configure Providers

Edit `config/ai_providers.yaml`:

```yaml
default_provider: claude

providers:
  claude:
    enabled: true
    api_key_env: ANTHROPIC_API_KEY
    model: claude-sonnet-4-5-20250929
    use_cli: true

  openai:
    enabled: true
    api_key_env: OPENAI_API_KEY
    model: gpt-4-turbo

  gemini:
    enabled: true
    api_key_env: GOOGLE_API_KEY
    model: gemini-1.5-pro
```

### 2. Set API Keys

```bash
export ANTHROPIC_API_KEY="your-claude-key"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

### 3. Use in Code

```python
from coffee_maker.ai_providers import get_provider

# Get default provider (Claude)
provider = get_provider()
result = provider.execute_prompt("Implement feature X")
print(result.content)

# Get specific provider
openai = get_provider('openai')
result = openai.execute_prompt("Write a function")
```

### 4. Use with Fallback

```python
from coffee_maker.ai_providers import FallbackStrategy

strategy = FallbackStrategy()
result = strategy.execute_with_fallback(
    prompt="Implement PRIORITY 5 from ROADMAP.md",
    working_dir="/path/to/project"
)
# Automatically tries Claude → OpenAI → Gemini until one succeeds
```

---

## Architecture

### Component Overview

```
coffee_maker/ai_providers/
├── __init__.py                 # Public API exports
├── base.py                     # BaseAIProvider abstract class
├── provider_config.py          # Configuration management
├── provider_factory.py         # Factory for creating providers
├── fallback_strategy.py        # Fallback/retry logic
└── providers/
    ├── __init__.py
    ├── claude_provider.py      # Claude implementation
    ├── openai_provider.py      # OpenAI implementation
    └── gemini_provider.py      # Gemini implementation

config/
└── ai_providers.yaml           # Provider configuration
```

### Design Principles

1. **Abstraction**: All providers implement `BaseAIProvider` interface
2. **Configurability**: Settings in YAML, not hardcoded
3. **Resilience**: Automatic fallback on provider failures
4. **Cost Control**: Built-in cost estimation and limits
5. **Extensibility**: Easy to add new providers

---

## Supported Providers

### 1. Claude (Anthropic)

**Status**: ✅ Fully Supported (Default)

**Modes**:
- **CLI Mode** (default): Uses Claude CLI for tool use and file operations
- **API Mode**: Direct API calls via `anthropic` Python SDK

**Configuration**:
```yaml
claude:
  enabled: true
  api_key_env: ANTHROPIC_API_KEY
  model: claude-sonnet-4-5-20250929
  use_cli: true  # Set to false for API mode
  max_tokens: 8000
  temperature: 0.7
  cost_per_1m_input_tokens: 15.0
  cost_per_1m_output_tokens: 75.0
```

**Best For**: Complex code generation, reasoning-heavy tasks

**Location**: `coffee_maker/ai_providers/providers/claude_provider.py:1`

---

### 2. OpenAI (GPT-4)

**Status**: ✅ Fully Supported

**Models Supported**:
- `gpt-4-turbo` (recommended)
- `gpt-4`
- `gpt-3.5-turbo`
- `o1`, `o3` (if available)

**Configuration**:
```yaml
openai:
  enabled: true
  api_key_env: OPENAI_API_KEY
  model: gpt-4-turbo
  fallback_models:
    - gpt-4
    - gpt-3.5-turbo
  max_tokens: 8000
  temperature: 0.7
  cost_per_1m_input_tokens: 10.0
  cost_per_1m_output_tokens: 30.0
```

**Best For**: General-purpose development, widely available

**Location**: `coffee_maker/ai_providers/providers/openai_provider.py:1`

---

### 3. Google Gemini

**Status**: ✅ Fully Supported

**Models Supported**:
- `gemini-1.5-pro` (recommended)
- `gemini-pro`

**Configuration**:
```yaml
gemini:
  enabled: true
  api_key_env: GOOGLE_API_KEY
  model: gemini-1.5-pro
  max_tokens: 8000
  temperature: 0.7
  cost_per_1m_input_tokens: 7.0
  cost_per_1m_output_tokens: 21.0
```

**Best For**: Cost-effective, high-volume tasks, large context windows (1M tokens)

**Location**: `coffee_maker/ai_providers/providers/gemini_provider.py:1`

---

## Configuration

### Configuration File Location

`config/ai_providers.yaml` (relative to project root)

### Full Configuration Example

```yaml
# Default provider (can be overridden with DEFAULT_AI_PROVIDER env var)
default_provider: claude

# Provider configurations
providers:
  claude:
    enabled: true
    api_key_env: ANTHROPIC_API_KEY
    model: claude-sonnet-4-5-20250929
    use_cli: true
    max_tokens: 8000
    temperature: 0.7
    cost_per_1m_input_tokens: 15.0
    cost_per_1m_output_tokens: 75.0

  openai:
    enabled: true
    api_key_env: OPENAI_API_KEY
    model: gpt-4-turbo
    fallback_models:
      - gpt-4
      - gpt-3.5-turbo
    max_tokens: 8000
    temperature: 0.7
    cost_per_1m_input_tokens: 10.0
    cost_per_1m_output_tokens: 30.0

  gemini:
    enabled: true
    api_key_env: GOOGLE_API_KEY
    model: gemini-1.5-pro
    max_tokens: 8000
    temperature: 0.7
    cost_per_1m_input_tokens: 7.0
    cost_per_1m_output_tokens: 21.0

# Fallback strategy
fallback:
  enabled: true
  retry_attempts: 3
  retry_delay: 1.0
  max_retry_delay: 60.0
  fallback_order:
    - claude
    - openai
    - gemini

# Cost controls
cost_controls:
  daily_limit: 50.0
  per_task_limit: 5.0
  warn_threshold: 0.8
  tracking_file: "data/cost_tracking.json"
```

### Environment Variables

Override configuration at runtime:

- `DEFAULT_AI_PROVIDER`: Override default provider (e.g., `export DEFAULT_AI_PROVIDER=openai`)
- `ANTHROPIC_API_KEY`: Claude API key
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_API_KEY`: Google Gemini API key

---

## Usage Examples

### Example 1: Basic Usage

```python
from coffee_maker.ai_providers import get_provider

# Get default provider
provider = get_provider()
print(f"Using: {provider.name}")  # 'claude'

# Execute a prompt
result = provider.execute_prompt(
    prompt="Write a Python function to calculate fibonacci numbers",
    system_prompt="You are an expert Python developer"
)

print(result.content)
print(f"Tokens: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")
```

### Example 2: Specific Provider

```python
from coffee_maker.ai_providers import get_provider

# Use OpenAI specifically
openai = get_provider('openai')
result = openai.execute_prompt("Refactor this code for better readability")

# Use Gemini specifically
gemini = get_provider('gemini')
result = gemini.execute_prompt("Add type hints to this Python code")
```

### Example 3: Fallback Strategy

```python
from coffee_maker.ai_providers import FallbackStrategy

strategy = FallbackStrategy()

# Automatically tries providers in fallback_order until one succeeds
result = strategy.execute_with_fallback(
    prompt="Implement user authentication",
    working_dir="/path/to/project",
    check_cost=True  # Check cost limits before execution
)

print(f"Succeeded with provider: {result.model}")
```

### Example 4: Custom Fallback Order

```python
from coffee_maker.ai_providers import FallbackStrategy

strategy = FallbackStrategy()

# Use custom provider order (try OpenAI first, then Claude)
result = strategy.execute_with_fallback(
    prompt="Fix this bug",
    providers=['openai', 'claude', 'gemini']
)
```

### Example 5: Cost Estimation

```python
from coffee_maker.ai_providers import get_provider

provider = get_provider('openai')

# Estimate cost before execution
prompt = "Implement a REST API with authentication"
estimated_cost = provider.estimate_cost(prompt)

print(f"Estimated cost: ${estimated_cost:.4f}")

if estimated_cost < 1.0:
    result = provider.execute_prompt(prompt)
else:
    print("Cost too high, using cheaper model")
    gemini = get_provider('gemini')
    result = gemini.execute_prompt(prompt)
```

### Example 6: Check Provider Availability

```python
from coffee_maker.ai_providers import list_enabled_providers, list_available_providers

# List enabled providers (from config)
enabled = list_enabled_providers()
print(f"Enabled: {enabled}")  # ['claude', 'openai', 'gemini']

# List actually available providers (API keys set + reachable)
available = list_available_providers(check_connectivity=True)
print(f"Available: {available}")  # ['claude', 'openai']  # gemini offline
```

### Example 7: Integration with Daemon

```python
# In coffee_maker/autonomous/daemon.py
from coffee_maker.ai_providers import FallbackStrategy

class CodeDeveloperDaemon:
    def __init__(self):
        self.fallback_strategy = FallbackStrategy()

    def execute_priority(self, priority: str):
        """Execute a priority from ROADMAP."""
        prompt = f"Read docs/ROADMAP.md and implement {priority}"

        try:
            result = self.fallback_strategy.execute_with_fallback(
                prompt=prompt,
                working_dir=self.working_dir,
                check_cost=True
            )

            self.log(f"✅ Completed {priority} using {result.model}")
            return result

        except AllProvidersFailedError as e:
            self.notify_user(
                "⚠️ All AI providers failed",
                str(e),
                priority="high"
            )
            raise
```

---

## Provider Comparison

| Feature | Claude | OpenAI (GPT-4) | Gemini 1.5 Pro |
|---------|--------|----------------|----------------|
| **Code Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Context Window** | 200K tokens | 128K tokens | 1M tokens |
| **Cost (Input)** | $15/1M tokens | $10/1M tokens | $7/1M tokens |
| **Cost (Output)** | $75/1M tokens | $30/1M tokens | $21/1M tokens |
| **Function Calling** | Excellent | Good | Good |
| **Vision Support** | Yes | Yes | Yes |
| **Streaming** | Yes | Yes | Yes |
| **CLI Integration** | ✅ Native | ❌ API only | ❌ API only |
| **Availability** | Most regions | Global | Most regions |
| **Reasoning Quality** | Excellent | Very Good | Very Good |
| **Best For** | Complex tasks | General use | High volume |

### When to Use Each Provider

**Use Claude when**:
- You need best-in-class code generation
- Task requires deep reasoning
- Using CLI mode for autonomous development
- Quality matters more than cost

**Use OpenAI when**:
- You need wide availability
- Team is familiar with GPT-4
- Balanced cost and quality
- Need reliable API uptime

**Use Gemini when**:
- Cost is a primary concern
- High-volume tasks (many requests)
- Need large context window (>200K tokens)
- Tasks are straightforward

---

## Fallback Strategy

### How It Works

1. **Try Primary Provider** (with retry)
   - Attempts 3 times with exponential backoff
   - Delays: 1s, 2s, 4s

2. **On Rate Limit** → Skip to next provider immediately

3. **On Unavailable** → Retry 3x, then try next provider

4. **On Cost Limit** → Skip provider, try next

5. **All Failed** → Raise `AllProvidersFailedError`

### Fallback Flow Diagram

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Try Claude     │
│  (3 retries)    │
└────┬────────────┘
     │ Success? ──────> ✅ Return Result
     │
     │ Rate Limit?
     ▼
┌─────────────────┐
│  Try OpenAI     │
│  (3 retries)    │
└────┬────────────┘
     │ Success? ──────> ✅ Return Result
     │
     │ Unavailable?
     ▼
┌─────────────────┐
│  Try Gemini     │
│  (3 retries)    │
└────┬────────────┘
     │ Success? ──────> ✅ Return Result
     │
     │ All Failed?
     ▼
┌─────────────────┐
│ ❌ Raise Error  │
│ AllProviders    │
│ FailedError     │
└─────────────────┘
```

### Configuring Fallback

```yaml
fallback:
  enabled: true
  retry_attempts: 3
  retry_delay: 1.0
  max_retry_delay: 60.0
  fallback_order:
    - claude
    - openai
    - gemini
```

**Parameters**:
- `enabled`: Enable/disable fallback (default: `true`)
- `retry_attempts`: Retries per provider (default: `3`)
- `retry_delay`: Initial retry delay in seconds (default: `1.0`)
- `max_retry_delay`: Max backoff delay (default: `60.0`)
- `fallback_order`: Provider sequence to try

---

## Cost Management

### Cost Estimation

Every provider implements `estimate_cost()`:

```python
provider = get_provider('openai')
cost = provider.estimate_cost(
    prompt="Long prompt here...",
    system_prompt="System prompt...",
    max_output_tokens=4000
)
print(f"Estimated: ${cost:.4f}")
```

### Cost Limits

Configure in `config/ai_providers.yaml`:

```yaml
cost_controls:
  daily_limit: 50.0        # Max $50/day across all providers
  per_task_limit: 5.0      # Max $5 per single task
  warn_threshold: 0.8      # Warn at 80% of limits
  tracking_file: "data/cost_tracking.json"
```

### Cost Tracking

```python
from coffee_maker.ai_providers import FallbackStrategy

strategy = FallbackStrategy()

# Automatic cost checking before execution
result = strategy.execute_with_fallback(
    prompt="Implement feature",
    check_cost=True  # Raises CostLimitExceededError if over limit
)

# Get cost statistics (future feature)
costs = strategy.get_provider_costs()
print(costs)  # {'claude': 23.50, 'openai': 8.20, 'gemini': 1.80}
```

### Current Pricing (as of 2025)

**Claude Sonnet 4.5**:
- Input: $15 per 1M tokens
- Output: $75 per 1M tokens

**GPT-4 Turbo**:
- Input: $10 per 1M tokens
- Output: $30 per 1M tokens

**Gemini 1.5 Pro**:
- Input: $7 per 1M tokens
- Output: $21 per 1M tokens

---

## Integration with Daemon

### Using in code-developer Daemon

The daemon automatically uses the provider system:

```python
# coffee_maker/autonomous/daemon.py
from coffee_maker.ai_providers import FallbackStrategy

class CodeDeveloperDaemon:
    def __init__(self):
        self.fallback_strategy = FallbackStrategy()

    def run(self):
        """Main daemon loop."""
        while True:
            priority = self.get_next_priority()

            result = self.fallback_strategy.execute_with_fallback(
                prompt=f"Implement {priority}",
                working_dir=self.working_dir
            )

            self.commit_changes(priority, result)
            self.update_roadmap(priority, 'complete')
```

### Command-Line Options

```bash
# Use default provider (from config)
poetry run code-developer

# Override provider
DEFAULT_AI_PROVIDER=openai poetry run code-developer

# Check available providers
poetry run code-developer --list-providers
```

---

## Troubleshooting

### Problem: "Provider 'openai' is not enabled"

**Solution**: Enable in config:
```yaml
providers:
  openai:
    enabled: true  # Make sure this is true
```

---

### Problem: "OPENAI_API_KEY not set"

**Solution**: Set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

Or add to `.env` file:
```
OPENAI_API_KEY=sk-...
```

---

### Problem: "All providers failed"

**Causes**:
1. All API keys are invalid
2. All providers are rate limited
3. Network connectivity issue

**Solution**:
```bash
# Check which providers are available
poetry run python3 -c "
from coffee_maker.ai_providers import list_available_providers
print(list_available_providers(check_connectivity=True))
"

# Test each provider individually
poetry run python3 -c "
from coffee_maker.ai_providers import get_provider
provider = get_provider('claude')
print(provider.check_available())
"
```

---

### Problem: "Cost limit exceeded"

**Solution**: Increase limits in config:
```yaml
cost_controls:
  daily_limit: 100.0      # Increase from 50 to 100
  per_task_limit: 10.0    # Increase from 5 to 10
```

---

### Problem: "Claude CLI not found"

**Cause**: Claude CLI not installed or not in PATH

**Solution**:
1. Install Claude CLI (see https://docs.anthropic.com)
2. Or use API mode instead:
```yaml
claude:
  use_cli: false  # Use API instead
```

---

## API Reference

### get_provider()

```python
def get_provider(
    provider_name: Optional[str] = None,
    config: Optional[ProviderConfig] = None
) -> BaseAIProvider
```

Get an AI provider instance.

**Parameters**:
- `provider_name` (str, optional): Provider to use ('claude', 'openai', 'gemini'). Defaults to config default.
- `config` (ProviderConfig, optional): Custom config. Defaults to loading from `config/ai_providers.yaml`.

**Returns**: Provider instance (`ClaudeProvider`, `OpenAIProvider`, or `GeminiProvider`)

**Raises**:
- `ProviderNotFoundError`: Provider not in registry
- `ProviderNotEnabledError`: Provider not enabled in config
- `ProviderConfigError`: Invalid configuration

**Example**:
```python
provider = get_provider('openai')
```

---

### BaseAIProvider.execute_prompt()

```python
def execute_prompt(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    working_dir: Optional[str] = None,
    timeout: Optional[int] = None,
    **kwargs
) -> ProviderResult
```

Execute a prompt and get result.

**Parameters**:
- `prompt` (str): User prompt/task description
- `system_prompt` (str, optional): System prompt for context
- `working_dir` (str, optional): Working directory path
- `timeout` (int, optional): Request timeout in seconds
- `**kwargs`: Provider-specific parameters

**Returns**: `ProviderResult` with:
- `content` (str): Response text
- `model` (str): Model used
- `usage` (dict): Token usage `{'input_tokens': X, 'output_tokens': Y}`
- `stop_reason` (str): Why generation stopped
- `error` (str, optional): Error message if failed
- `metadata` (dict): Provider-specific metadata

---

### FallbackStrategy.execute_with_fallback()

```python
def execute_with_fallback(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    working_dir: Optional[str] = None,
    timeout: Optional[int] = None,
    providers: Optional[List[str]] = None,
    check_cost: bool = True,
    **kwargs
) -> ProviderResult
```

Execute with automatic fallback on failure.

**Parameters**:
- `prompt` (str): User prompt
- `system_prompt` (str, optional): System prompt
- `working_dir` (str, optional): Working directory
- `timeout` (int, optional): Timeout in seconds
- `providers` (list, optional): Custom provider order
- `check_cost` (bool): Check cost limits (default: True)
- `**kwargs`: Additional parameters

**Returns**: `ProviderResult` from first successful provider

**Raises**:
- `AllProvidersFailedError`: All providers failed
- `CostLimitExceededError`: Cost limit exceeded

---

### list_enabled_providers()

```python
def list_enabled_providers(config: Optional[ProviderConfig] = None) -> List[str]
```

Get list of enabled providers from config.

**Returns**: List of provider names (e.g., `['claude', 'openai', 'gemini']`)

---

### list_available_providers()

```python
def list_available_providers(
    config: Optional[ProviderConfig] = None,
    check_connectivity: bool = False
) -> List[str]
```

Get list of available providers (enabled + API keys set + reachable).

**Parameters**:
- `config` (ProviderConfig, optional): Custom config
- `check_connectivity` (bool): Test actual connectivity (default: False)

**Returns**: List of available provider names

---

## Summary

The Multi-AI Provider Support system provides:

✅ **Flexibility**: Use Claude, OpenAI, or Gemini
✅ **Reliability**: Automatic fallback on failures
✅ **Cost Control**: Built-in cost estimation and limits
✅ **Ease of Use**: Simple API, configured via YAML
✅ **Extensibility**: Easy to add new providers

**Next Steps**:
1. Configure your providers in `config/ai_providers.yaml`
2. Set API keys via environment variables
3. Use `get_provider()` for simple cases
4. Use `FallbackStrategy` for production robustness

For questions or issues, see:
- [ROADMAP.md](../ROADMAP.md) - Project roadmap
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues
- [GitHub Issues](https://github.com/your-repo/issues) - Report bugs
