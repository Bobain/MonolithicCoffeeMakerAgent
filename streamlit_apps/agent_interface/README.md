# Agent Interaction Interface - Streamlit UI

Interactive chat interface for Coffee Maker Agent built with Streamlit.

## 🎯 Overview

The Agent Interaction Interface provides a modern, web-based chat UI for interacting with various AI agents. It features:

- **Real-time chat interface** with streaming responses
- **Multiple agent templates** (Code Reviewer, Architecture Expert, Python Developer, etc.)
- **Dynamic configuration** (model selection, temperature, max tokens)
- **Conversation history** with persistence
- **Live metrics** (tokens, cost, message count)
- **Export functionality** (Markdown, JSON, plain text)

## 🚀 Quick Start

### Installation

```bash
# From project root
cd streamlit_apps/agent_interface

# Install dependencies
pip install -r requirements.txt

# Or use poetry
poetry install
```

### Running the App

```bash
# From the agent_interface directory
streamlit run app.py

# Or from project root
streamlit run streamlit_apps/agent_interface/app.py
```

The app will open in your browser at `http://localhost:8501`.

## 📋 Features

### Agent Templates

Six predefined agent templates are available:

1. **General Assistant** - General-purpose helpful assistant
2. **Code Reviewer** - Expert code reviewer for bugs and best practices
3. **Architecture Expert** - Software architecture and design guidance
4. **Python Developer** - Python coding assistance
5. **Documentation Writer** - Technical documentation specialist
6. **Test Generator** - Comprehensive unit test generation

Each template includes:
- Customized system prompt
- Recommended model and temperature
- Example tasks and use cases

### Configuration Options

- **Agent Selection**: Choose from 6 agent templates
- **Model Selection**: Claude (Sonnet, Opus, Haiku) or GPT (4, 3.5)
- **Temperature**: 0.0 (focused) to 1.0 (creative)
- **Max Tokens**: Control response length (100-8000)

### Conversation Management

- **History**: View full conversation history
- **Persistence**: Save conversations to disk
- **Export**: Export to Markdown, JSON, or plain text
- **Metrics**: Track tokens, cost, and message count

## 🏗️ Architecture

```
agent_interface/
├── app.py                          # Main Streamlit app
├── agents/
│   ├── agent_manager.py            # Agent instance management
│   └── agent_templates.py          # Predefined agent templates
├── storage/
│   └── conversation_storage.py     # Conversation persistence
├── pages/                          # Additional pages (future)
│   ├── 01_chat.py                  # Chat interface
│   ├── 02_agent_config.py          # Agent configuration
│   ├── 03_history.py               # Conversation history
│   └── 04_playground.py            # Testing & experimentation
└── components/                     # Reusable components (future)
    ├── chat_interface.py
    ├── agent_selector.py
    ├── model_config.py
    └── metrics_display.py
```

## 💻 Usage Examples

### Basic Chat

1. Select an agent (e.g., "Python Developer")
2. Configure model and temperature
3. Type your message in the chat input
4. View the response with real-time metrics

### Code Review

1. Select "Code Reviewer" agent
2. Paste your code in the chat
3. Receive detailed review with:
   - Bug identification
   - Best practice suggestions
   - Performance recommendations
   - Security considerations

### Generate Tests

1. Select "Test Generator" agent
2. Provide a function to test
3. Get comprehensive unit tests with:
   - Happy path tests
   - Edge case tests
   - Error handling tests
   - Parametrized tests

## 🔧 Customization

### Adding New Agent Templates

Edit `agents/agent_templates.py`:

```python
@staticmethod
def custom_agent() -> AgentTemplate:
    return {
        "name": "Custom Agent",
        "description": "Description",
        "system_prompt": "Your system prompt...",
        "recommended_model": "claude-sonnet-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "example_tasks": ["Task 1", "Task 2"],
    }
```

Then add to `get_all_templates()`:

```python
"Custom Agent": AgentTemplates.custom_agent(),
```

### Integrating Real AI Models

To connect to actual AI models, update `agents/agent_manager.py`:

```python
def generate_response(self, user_message: str) -> str:
    # Import your AI client
    from anthropic import Anthropic

    client = Anthropic()

    # Build messages with history
    messages = self.conversation_history + [
        {"role": "user", "content": user_message}
    ]

    # Call API
    response = client.messages.create(
        model=self.config["model"],
        system=self.system_prompt,
        messages=messages,
        max_tokens=self.config["max_tokens"],
        temperature=self.config["temperature"],
    )

    # Extract and return response
    return response.content[0].text
```

### Styling

Custom CSS is in `app.py`:

```python
st.markdown("""
    <style>
    .custom-class {
        /* Your styles */
    }
    </style>
""", unsafe_allow_html=True)
```

## 📊 Conversation Storage

Conversations are saved to `data/conversations/` as JSON files:

```json
{
  "id": "conv-uuid",
  "agent_name": "Code Reviewer",
  "config": {
    "model": "claude-sonnet-4",
    "temperature": 0.7
  },
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "metrics": {
    "total_tokens": 500,
    "total_cost": 0.005
  },
  "timestamp": "2025-10-09T10:00:00"
}
```

### Storage API

```python
from storage.conversation_storage import ConversationStorage

storage = ConversationStorage()

# Save conversation
storage.save_conversation(
    conversation_id="conv-123",
    agent_name="Code Reviewer",
    config={"model": "claude-sonnet-4"},
    messages=[...],
    metrics={...}
)

# List conversations
conversations = storage.list_conversations(limit=10)

# Load conversation
conv = storage.load_conversation("conv-123")

# Export conversation
markdown = storage.export_conversation("conv-123", format="markdown")
```

## 🎨 Planned Features

### Phase 2 Enhancements

- [ ] **Streaming Responses**: Real-time token-by-token streaming
- [ ] **Multi-Agent Conversations**: Multiple agents in one conversation
- [ ] **Voice Input**: Speech-to-text for input
- [ ] **Code Highlighting**: Syntax highlighting in responses
- [ ] **File Upload**: Upload code files for review
- [ ] **Collaborative Editing**: Edit code with agent assistance
- [ ] **Integration with VS Code**: Extension for in-editor chat

### Advanced Features

- [ ] **Conversation Branching**: Fork conversations at any point
- [ ] **Agent Comparison**: Compare responses from different agents
- [ ] **Custom Agents**: Create and save custom agent configurations
- [ ] **Analytics Dashboard**: Usage analytics and insights
- [ ] **API Integration**: Use as API service
- [ ] **Multi-Language Support**: i18n for international users

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Use different port
streamlit run app.py --server.port 8502
```

**Module Not Found**:
```bash
# Ensure in correct directory
cd streamlit_apps/agent_interface

# Install dependencies
pip install -r requirements.txt
```

**Streamlit Not Installed**:
```bash
pip install streamlit>=1.28.0
```

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Coffee Maker Agent Documentation](../../docs/)

## 🤝 Contributing

To contribute to the Agent Interface:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

See the project's main LICENSE file.

---

**Built with ☕ and Streamlit**
