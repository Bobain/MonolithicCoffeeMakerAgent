"""Main Streamlit Application for Agent Interaction.

This is the entry point for the Coffee Maker Agent interaction interface.
It provides a modern chat interface for interacting with various AI agents.

Features:
- Real-time chat with streaming responses
- Multiple agent templates
- Dynamic configuration
- Conversation history
- Metrics and analytics

Usage:
    streamlit run streamlit_apps/agent_interface/app.py
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Coffee Maker Agent - Chat Interface",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    import uuid

    st.session_state.conversation_id = str(uuid.uuid4())

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0

# Main header
st.markdown('<div class="main-header">☕ Coffee Maker Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Interactive Chat Interface for AI Agents</div>',
    unsafe_allow_html=True,
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Agent selection
    agent_type = st.selectbox(
        "Select Agent",
        [
            "General Assistant",
            "Code Reviewer",
            "Architecture Expert",
            "Python Developer",
            "Documentation Writer",
            "Test Generator",
        ],
        help="Choose the agent type for this conversation",
    )

    # Model selection
    model = st.selectbox(
        "Model",
        [
            "claude-sonnet-4",
            "claude-opus-4",
            "claude-haiku-4",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        help="Select the AI model to use",
    )

    # Temperature
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, help="Controls randomness in responses")

    # Max tokens
    max_tokens = st.number_input("Max Tokens", 100, 8000, 2000, 100, help="Maximum tokens in response")

    st.divider()

    # Metrics
    st.subheader("📊 Session Metrics")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Tokens", st.session_state.total_tokens)
    with col2:
        st.metric("Cost", f"${st.session_state.total_cost:.4f}")

    st.divider()

    # Actions
    st.subheader("🔧 Actions")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.session_state.total_cost = 0.0
        st.rerun()

    if st.button("💾 Export Chat", use_container_width=True):
        st.info("Export feature coming soon!")

    if st.button("📜 Load History", use_container_width=True):
        st.info("History feature coming soon!")

# Main chat area
chat_container = st.container()

with chat_container:
    # Display existing messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.markdown(
                f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-message assistant-message"><strong>Assistant:</strong><br>{content}</div>',
                unsafe_allow_html=True,
            )

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with chat_container:
        st.markdown(
            f'<div class="chat-message user-message"><strong>You:</strong><br>{user_input}</div>',
            unsafe_allow_html=True,
        )

    # Generate assistant response (placeholder for now)
    with chat_container:
        with st.spinner("🤔 Thinking..."):
            # TODO: Integrate with actual agent
            # For now, provide a placeholder response
            assistant_response = f"""Thank you for your message! This is a placeholder response.

**Selected Configuration:**
- Agent: {agent_type}
- Model: {model}
- Temperature: {temperature}
- Max Tokens: {max_tokens}

**Your message:**
{user_input}

---

*Note: This is the UI framework. Agent integration coming next!*

To fully activate this interface:
1. Integration with Coffee Maker agents
2. Streaming response support
3. Conversation persistence
4. Advanced metrics tracking
"""

            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            # Update metrics (placeholder values)
            st.session_state.total_tokens += 150
            st.session_state.total_cost += 0.0015

    # Rerun to show new messages
    st.rerun()

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>☕ Coffee Maker Agent v1.0 | Built with Streamlit</p>
        <p>Features: Chat, Streaming, Metrics, History (in development)</p>
    </div>
    """,
    unsafe_allow_html=True,
)
