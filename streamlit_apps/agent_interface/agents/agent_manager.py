"""Agent Manager for handling agent instances and conversations.

This module provides a manager class for:
- Creating and managing agent instances
- Handling conversations with streaming support
- Tracking metrics (tokens, cost, latency)
- Managing agent state and configuration

The AgentManager provides a clean interface between the Streamlit UI
and the underlying AI models.
"""

import time
from typing import Dict, Generator, List, Optional

from .agent_templates import AgentTemplates


class AgentManager:
    """Manages agent instances and their conversations.

    The AgentManager handles:
    - Agent initialization with templates
    - Conversation management
    - Streaming response generation
    - Metrics tracking (tokens, cost, latency)

    Attributes:
        agent_name: Name of the current agent
        config: Agent configuration (model, temperature, etc.)
        conversation_history: List of messages in current conversation
        total_tokens: Total tokens used in conversation
        total_cost: Total cost of conversation
    """

    def __init__(self, agent_name: str = "General Assistant", config: Optional[Dict] = None):
        """Initialize the agent manager.

        Args:
            agent_name: Name of the agent template to use
            config: Optional configuration override
        """
        self.agent_name = agent_name
        self.template = AgentTemplates.get_template(agent_name)

        # Use config override or template defaults
        if config:
            self.config = config
        else:
            self.config = AgentTemplates.get_recommended_config(agent_name)

        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.total_tokens = 0
        self.total_cost = 0.0

        # System prompt
        self.system_prompt = self.template["system_prompt"]

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        self.conversation_history.append({"role": role, "content": content})

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history.

        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()

    def clear_history(self) -> None:
        """Clear conversation history and reset metrics."""
        self.conversation_history = []
        self.total_tokens = 0
        self.total_cost = 0.0

    def generate_response(self, user_message: str) -> str:
        """Generate a response to user message.

        This is a placeholder that returns mock responses.
        In a full implementation, this would call the actual AI model.

        Args:
            user_message: The user's message

        Returns:
            The assistant's response

        Note:
            This is a mock implementation for demonstration purposes.
            To integrate with real models:
            1. Import the actual LLM client (Anthropic, OpenAI, etc.)
            2. Build the prompt with system + conversation history
            3. Call the model API
            4. Parse and return the response
        """
        # Add user message to history
        self.add_message("user", user_message)

        # Mock response based on agent type
        response = self._generate_mock_response(user_message)

        # Add assistant response to history
        self.add_message("assistant", response)

        # Update metrics (mock values)
        tokens_used = len(user_message.split()) + len(response.split())
        cost = tokens_used * 0.00001  # Mock cost calculation

        self.total_tokens += tokens_used
        self.total_cost += cost

        return response

    def generate_response_stream(self, user_message: str) -> Generator[str, None, None]:
        """Generate a streaming response to user message.

        This is a placeholder that yields mock streaming responses.
        In a full implementation, this would stream from the actual AI model.

        Args:
            user_message: The user's message

        Yields:
            Chunks of the assistant's response

        Note:
            This is a mock implementation for demonstration purposes.
            To integrate with real streaming:
            1. Import the streaming LLM client
            2. Use the streaming API (e.g., Claude's streaming)
            3. Yield each chunk as it arrives
            4. Track metrics as chunks come in
        """
        # Add user message to history
        self.add_message("user", user_message)

        # Generate response
        response = self._generate_mock_response(user_message)

        # Stream response word by word (mock streaming)
        words = response.split()
        streamed_response = []

        for word in words:
            streamed_response.append(word)
            yield word + " "
            time.sleep(0.02)  # Mock streaming delay

        # Add complete response to history
        full_response = " ".join(streamed_response)
        self.add_message("assistant", full_response)

        # Update metrics
        tokens_used = len(user_message.split()) + len(words)
        cost = tokens_used * 0.00001

        self.total_tokens += tokens_used
        self.total_cost += cost

    def _generate_mock_response(self, user_message: str) -> str:
        """Generate a mock response based on agent type.

        This is a placeholder implementation that returns canned responses
        customized by agent type.

        Args:
            user_message: The user's message

        Returns:
            Mock response string
        """
        if self.agent_name == "Code Reviewer":
            return f"""### Code Review

**Overall Assessment**: 8/10

I've reviewed your code. Here's my analysis:

**Strengths:**
- Clear variable names
- Good function structure
- Proper error handling

**Issues Found:**
1. **Performance**: Consider using list comprehension instead of loops
2. **Type Safety**: Add type hints to function parameters
3. **Documentation**: Missing docstrings

**Recommendations:**
- Add unit tests for edge cases
- Consider extracting complex logic into helper functions
- Add input validation

**Your Message:** "{user_message[:100]}..."

*Note: This is a placeholder response. Real code review coming soon!*"""

        elif self.agent_name == "Architecture Expert":
            return f"""### Architecture Guidance

For your system design question, here's my recommendation:

**Approach:** Microservices with Event-Driven Architecture

**Key Components:**
1. API Gateway (entry point)
2. Service Layer (business logic)
3. Data Layer (persistence)
4. Message Queue (async communication)

**Trade-offs:**
- ✅ **Pros**: Scalability, independence, fault isolation
- ❌ **Cons**: Complexity, distributed transactions, operational overhead

**Recommended Technologies:**
- FastAPI for services
- PostgreSQL for data
- RabbitMQ for messaging
- Docker for deployment

**Your Question:** "{user_message[:100]}..."

*Note: This is a placeholder response. Real architecture guidance coming soon!*"""

        elif self.agent_name == "Python Developer":
            return f"""### Python Development Assistance

Here's a code example for your request:

```python
def example_function(data: list[str]) -> dict[str, int]:
    \"\"\"Process data and return counts.

    Args:
        data: List of strings to process

    Returns:
        Dictionary mapping strings to their counts

    Example:
        >>> example_function(['a', 'b', 'a'])
        {{'a': 2, 'b': 1}}
    \"\"\"
    from collections import Counter
    return dict(Counter(data))


# Tests
def test_example_function():
    result = example_function(['a', 'b', 'a'])
    assert result == {{'a': 2, 'b': 1}}
```

**Key Points:**
- Type hints for clarity
- Docstring with example
- Using standard library (Counter)
- Included test case

**Your Request:** "{user_message[:100]}..."

*Note: This is a placeholder response. Real Python assistance coming soon!*"""

        elif self.agent_name == "Documentation Writer":
            return f"""### Documentation

# Feature Name

## Overview

This feature provides [description of what it does].

## Usage

```python
# Basic usage
result = function_name(param1, param2)

# Advanced usage
with context_manager() as ctx:
    ctx.do_something()
```

## Parameters

- `param1` (type): Description of param1
- `param2` (type): Description of param2

## Returns

Returns a `ResultType` containing [description].

## Examples

### Example 1: Basic Usage

```python
# Simple example
result = function_name("hello", 42)
print(result)  # Output: ...
```

### Example 2: Advanced Usage

```python
# Complex example
with advanced_feature() as feature:
    feature.configure(option="value")
    feature.execute()
```

## Troubleshooting

**Issue**: Common problem
**Solution**: How to fix it

**Your Topic:** "{user_message[:100]}..."

*Note: This is a placeholder response. Real documentation coming soon!*"""

        elif self.agent_name == "Test Generator":
            return f"""### Generated Tests

```python
import pytest
from unittest.mock import Mock, patch


class TestYourFunction:
    \"\"\"Test suite for your_function.\"\"\"

    def test_happy_path(self):
        \"\"\"Test the basic happy path.\"\"\"
        result = your_function("input")
        assert result == "expected"

    def test_edge_case_empty(self):
        \"\"\"Test with empty input.\"\"\"
        result = your_function("")
        assert result is None

    def test_error_handling(self):
        \"\"\"Test error handling.\"\"\"
        with pytest.raises(ValueError):
            your_function(None)

    @pytest.mark.parametrize("input,expected", [
        ("a", "A"),
        ("b", "B"),
        ("c", "C"),
    ])
    def test_multiple_cases(self, input, expected):
        \"\"\"Test multiple input cases.\"\"\"
        result = your_function(input)
        assert result == expected

    def test_with_mock(self):
        \"\"\"Test with mocked dependency.\"\"\"
        with patch('module.dependency') as mock_dep:
            mock_dep.return_value = "mocked"
            result = your_function("input")
            assert result == "mocked"
            mock_dep.assert_called_once()
```

**Test Coverage:**
- ✅ Happy path
- ✅ Edge cases
- ✅ Error handling
- ✅ Multiple scenarios (parametrize)
- ✅ Mocking dependencies

**Your Code:** "{user_message[:100]}..."

*Note: This is a placeholder response. Real test generation coming soon!*"""

        else:  # General Assistant
            return f"""Thank you for your message!

I'm here to help with your questions and tasks. Based on your message, here's my response:

**What you asked about:** {user_message[:200]}

**My response:**
I understand you're interested in this topic. Here's what I can tell you:

1. This is a demonstration of the Chat Interface
2. The full AI integration is coming next
3. This shows the UI framework and structure

**Current Configuration:**
- Agent: {self.agent_name}
- Model: {self.config.get('model', 'unknown')}
- Temperature: {self.config.get('temperature', 0.7)}

**Next Steps:**
1. The UI framework is complete
2. Agent integration is in progress
3. You'll soon be able to have real conversations!

*Note: This is a placeholder response showing the interface works. Real AI responses coming soon!*"""

    def get_metrics(self) -> Dict[str, any]:
        """Get current conversation metrics.

        Returns:
            Dictionary containing tokens, cost, message count
        """
        return {
            "message_count": len(self.conversation_history),
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "agent_name": self.agent_name,
            "model": self.config.get("model", "unknown"),
        }

    def export_conversation(self, format: str = "markdown") -> str:
        """Export conversation to specified format.

        Args:
            format: Export format ("markdown", "json", "text")

        Returns:
            Formatted conversation string

        Raises:
            ValueError: If format is not supported
        """
        if format == "markdown":
            return self._export_markdown()
        elif format == "json":
            import json

            return json.dumps(
                {
                    "agent": self.agent_name,
                    "config": self.config,
                    "messages": self.conversation_history,
                    "metrics": self.get_metrics(),
                },
                indent=2,
            )
        elif format == "text":
            return self._export_text()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_markdown(self) -> str:
        """Export conversation as Markdown."""
        lines = [
            f"# Conversation with {self.agent_name}",
            "",
            f"**Model:** {self.config.get('model')}",
            f"**Messages:** {len(self.conversation_history)}",
            f"**Tokens:** {self.total_tokens}",
            f"**Cost:** ${self.total_cost:.4f}",
            "",
            "---",
            "",
        ]

        for msg in self.conversation_history:
            role = msg["role"].title()
            content = msg["content"]
            lines.append(f"## {role}")
            lines.append("")
            lines.append(content)
            lines.append("")

        return "\n".join(lines)

    def _export_text(self) -> str:
        """Export conversation as plain text."""
        lines = [f"Conversation with {self.agent_name}", "=" * 50, ""]

        for msg in self.conversation_history:
            role = msg["role"].upper()
            content = msg["content"]
            lines.append(f"{role}:")
            lines.append(content)
            lines.append("")

        return "\n".join(lines)
