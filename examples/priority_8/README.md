# PRIORITY 8: Multi-AI Provider Support - Examples

This directory contains practical examples demonstrating the multi-AI provider system.

## Overview

The examples show how to:
- Use different AI providers (Claude, OpenAI, Gemini)
- Implement automatic fallback strategies
- Estimate and control costs
- Compare provider performance
- Integrate providers into your applications

## Prerequisites

### 1. Install Dependencies

```bash
poetry install
```

### 2. Set API Keys

You need at least one provider configured:

```bash
# Claude (default)
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# OpenAI (optional, for fallback)
export OPENAI_API_KEY="sk-xxxxx"

# Google Gemini (optional, for fallback)
export GOOGLE_API_KEY="AIzaxxxxx"
```

Or add to `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=AIzaxxxxx
```

### 3. Verify Installation

```bash
python3 -c "from coffee_maker.ai_providers import get_provider; print('✓ Installation successful')"
```

## Examples

### basic_usage.py

Demonstrates fundamental usage patterns:

```bash
python3 examples/priority_8/basic_usage.py
```

**What it covers**:
- Using the default provider
- Selecting a specific provider
- Listing available providers
- Comparing responses from different providers
- Estimating costs before execution

**Example output**:
```
Example 1: Default Provider
✓ Using provider: claude
  Model: claude-sonnet-4-5-20250929
✓ Response: Hello from the multi-provider system!
  Tokens: 15 in, 8 out
```

---

### fallback_strategy.py

Shows automatic fallback and retry logic:

```bash
python3 examples/priority_8/fallback_strategy.py
```

**What it covers**:
- Basic fallback usage
- Custom fallback provider order
- Cost-aware execution
- Error handling when all providers fail
- Smart routing based on task complexity

**Example output**:
```
Example 1: Basic Fallback
✓ Success with provider: claude-sonnet-4-5-20250929
  Response: def is_palindrome(s: str) -> bool:
  Tokens: 45 in, 120 out
```

---

### daemon_integration.py (Coming Soon)

Will demonstrate integration with the code-developer daemon:

```bash
python3 examples/priority_8/daemon_integration.py
```

**What it will cover**:
- Using providers in autonomous daemon
- Switching providers at runtime
- Cost tracking across tasks
- Performance monitoring

---

## Running All Examples

Run all examples in sequence:

```bash
# Run all examples
for f in examples/priority_8/*.py; do
    echo "Running $f..."
    python3 "$f"
    echo ""
done
```

## Configuration

Examples use the default configuration from `config/ai_providers.yaml`.

To customize configuration:

```yaml
# config/ai_providers.yaml
default_provider: claude  # Change to 'openai' or 'gemini'

providers:
  claude:
    enabled: true
    model: claude-sonnet-4-5-20250929

  openai:
    enabled: true
    model: gpt-4-turbo

  gemini:
    enabled: true
    model: gemini-1.5-pro

fallback:
  enabled: true
  fallback_order:
    - claude
    - openai
    - gemini
```

## Troubleshooting

### "Provider not enabled"

**Solution**: Enable provider in `config/ai_providers.yaml`:
```yaml
providers:
  openai:
    enabled: true  # Set to true
```

### "API key not set"

**Solution**: Export API key:
```bash
export OPENAI_API_KEY="sk-xxxxx"
```

### "All providers failed"

**Causes**:
1. No API keys configured
2. All providers rate limited
3. Network issue

**Solution**: Check provider availability:
```bash
python3 -c "
from coffee_maker.ai_providers import list_available_providers
print(list_available_providers(check_connectivity=True))
"
```

## Additional Resources

- **Complete Guide**: [docs/PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md](../../docs/PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md)
- **Technical Spec**: [docs/PRIORITY_8_TECHNICAL_SPEC.md](../../docs/PRIORITY_8_TECHNICAL_SPEC.md)
- **Migration Guide**: [docs/PRIORITY_8_MIGRATION_GUIDE.md](../../docs/PRIORITY_8_MIGRATION_GUIDE.md)
- **Provider Comparison**: [docs/PRIORITY_8_PROVIDER_COMPARISON.md](../../docs/PRIORITY_8_PROVIDER_COMPARISON.md)

## Contributing

To add new examples:

1. Create a new `.py` file in this directory
2. Follow the existing example structure:
   - Shebang and module docstring
   - Add project root to path
   - Define example functions
   - Add `main()` function
3. Update this README with your example
4. Test with multiple providers

## Questions?

See the [FAQ in the main guide](../../docs/PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md#troubleshooting).
