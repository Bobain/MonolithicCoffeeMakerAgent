# System Architecture

**Version**: 1.0
**Last Updated**: 2025-10-16
**Status**: Living Document

This document provides visual architecture diagrams for the MonolithicCoffeeMakerAgent system.

---

## Table of Contents

1. [High-Level System Architecture](#high-level-system-architecture)
2. [Module Dependency Graph](#module-dependency-graph)
3. [Agent Interaction Flow](#agent-interaction-flow)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Class Hierarchy](#class-hierarchy)

---

## High-Level System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Interface]
        Streamlit[Streamlit Apps]
        UserListener[user_listener Agent]
    end

    subgraph "Orchestration Layer"
        PM[project_manager Agent]
        CD[code_developer Agent]
        Assistant[assistant Agent]
        Architect[architect Agent]
    end

    subgraph "Execution Layer"
        Daemon[DevDaemon]
        AIService[AI Service]
        GitOps[Git Operations]
    end

    subgraph "Data Layer"
        Roadmap[(ROADMAP.md)]
        NotificationDB[(Notifications)]
        StatusDB[(Developer Status)]
        Langfuse[(Langfuse Observability)]
    end

    subgraph "External Services"
        Claude[Claude API]
        OpenAI[OpenAI API]
        Gemini[Gemini API]
        GitHub[GitHub API]
    end

    CLI --> PM
    Streamlit --> PM
    UserListener --> PM
    UserListener --> Assistant
    UserListener --> CD
    UserListener --> Architect

    PM --> Daemon
    CD --> Daemon
    Architect --> AIService

    Daemon --> GitOps
    Daemon --> Roadmap
    Daemon --> StatusDB
    Daemon --> NotificationDB

    AIService --> Claude
    AIService --> OpenAI
    AIService --> Gemini

    GitOps --> GitHub

    Daemon --> Langfuse
    AIService --> Langfuse
```

**Description**:
- **User Interface Layer**: Entry points for user interaction
- **Orchestration Layer**: Autonomous agents coordinating work
- **Execution Layer**: Core business logic and automation
- **Data Layer**: Persistent storage and observability
- **External Services**: Third-party APIs and services

---

## Module Dependency Graph

```mermaid
graph LR
    subgraph "Core Modules"
        Config[config/]
        Utils[utils/]
        Exceptions[exceptions.py]
    end

    subgraph "Autonomous System"
        Daemon[autonomous/daemon.py]
        Parser[autonomous/roadmap_parser.py]
        GitManager[autonomous/git_manager.py]
        PromptLoader[autonomous/prompt_loader.py]
    end

    subgraph "AI Providers"
        AIService[ai_service/]
        Claude[ai_service/claude_provider.py]
        OpenAI[ai_service/openai_provider.py]
        Gemini[ai_service/gemini_provider.py]
    end

    subgraph "CLI Tools"
        PMCLI[cli/project_manager_cli.py]
        Notifications[cli/notifications.py]
        AssistantManager[cli/assistant_manager.py]
    end

    subgraph "Observability"
        Langfuse[langfuse_observe/]
        RateTracker[langfuse_observe/global_rate_tracker.py]
        Retry[langfuse_observe/retry.py]
    end

    Daemon --> Config
    Daemon --> Utils
    Daemon --> Parser
    Daemon --> GitManager
    Daemon --> PromptLoader
    Daemon --> AIService
    Daemon --> Notifications

    AIService --> Claude
    AIService --> OpenAI
    AIService --> Gemini
    AIService --> Config
    AIService --> Langfuse
    AIService --> RateTracker
    AIService --> Retry

    PMCLI --> Notifications
    PMCLI --> Parser
    PMCLI --> Config

    Config --> Exceptions
    Utils --> Exceptions

    Claude --> Langfuse
    OpenAI --> Langfuse
    Gemini --> Langfuse
```

**Key Dependencies**:
- All modules depend on `config/` and `utils/`
- AI providers are isolated and interchangeable
- Langfuse observability spans all AI operations
- CLI tools are independent of daemon logic

---

## Agent Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant UserListener
    participant Assistant
    participant PM as project_manager
    participant CD as code_developer
    participant Architect
    participant Daemon
    participant GitHub

    User->>UserListener: "Implement feature X"
    UserListener->>UserListener: Parse intent

    alt Strategic Decision
        UserListener->>PM: Delegate strategic planning
        PM->>PM: Analyze ROADMAP
        PM->>UserListener: Strategic plan
    else Technical Spec
        UserListener->>Architect: Request technical design
        Architect->>Architect: Create specification
        Architect->>UserListener: Technical spec
    else Implementation
        UserListener->>CD: Delegate implementation
        CD->>Daemon: Trigger implementation
        Daemon->>Daemon: Read ROADMAP
        Daemon->>Daemon: Implement code
        Daemon->>Daemon: Run tests
        Daemon->>Daemon: Verify DoD
        Daemon->>GitHub: Create PR
        CD->>UserListener: Implementation complete
    else Quick Question
        UserListener->>Assistant: Delegate query
        Assistant->>Assistant: Search docs
        Assistant->>UserListener: Answer
    end

    UserListener->>User: Synthesized response
```

**Interaction Patterns**:
1. **user_listener is the ONLY UI agent** - All user interactions go through it
2. **Delegation based on task type** - Strategic, technical, implementation, or informational
3. **Autonomous execution** - code_developer works independently after delegation
4. **Synthesis** - user_listener combines responses from multiple agents

---

## Data Flow Diagrams

### Autonomous Implementation Flow

```mermaid
graph TD
    Start[code_developer starts] --> ReadROADMAP[Read ROADMAP.md]
    ReadROADMAP --> FindPriority[Find next 'Planned' priority]

    FindPriority --> CheckComplexity{Complex priority?}
    CheckComplexity -->|Yes| CreateSpec[Create technical spec]
    CheckComplexity -->|No| UpdateStatus1[Mark 'In Progress']
    CreateSpec --> UpdateStatus1

    UpdateStatus1 --> LoadPrompt[Load implementation prompt]
    LoadPrompt --> CallAI[Execute AI provider]
    CallAI --> ProcessResponse[Process AI response]

    ProcessResponse --> WriteCode[Write code files]
    WriteCode --> RunTests[Run pytest]

    RunTests --> TestPass{Tests pass?}
    TestPass -->|No| FixTests[Fix test failures]
    FixTests --> RunTests
    TestPass -->|Yes| VerifyDoD[Verify DoD]

    VerifyDoD --> DoDPass{DoD pass?}
    DoDPass -->|No| CreateNotification[Notify user]
    DoDPass -->|Yes| GitCommit[Git commit]

    GitCommit --> GitPush[Git push]
    GitPush --> CreatePR[Create GitHub PR]
    CreatePR --> UpdateStatus2[Mark 'Complete']
    UpdateStatus2 --> UpdateROADMAP[Update ROADMAP.md]
    UpdateROADMAP --> End[Loop to next priority]

    CreateNotification --> End
```

### AI Provider Selection Flow

```mermaid
graph TD
    Request[AI Request] --> CheckProvider{Provider specified?}
    CheckProvider -->|Yes| UseSpecified[Use specified provider]
    CheckProvider -->|No| AutoSelect[Auto-select provider]

    AutoSelect --> CheckClaude{Claude available?}
    CheckClaude -->|Yes| UseClaude[Use Claude]
    CheckClaude -->|No| CheckOpenAI{OpenAI available?}

    CheckOpenAI -->|Yes| UseOpenAI[Use OpenAI]
    CheckOpenAI -->|No| CheckGemini{Gemini available?}

    CheckGemini -->|Yes| UseGemini[Use Gemini]
    CheckGemini -->|No| Error[Raise ProviderError]

    UseSpecified --> ExecuteRequest[Execute request]
    UseClaude --> ExecuteRequest
    UseOpenAI --> ExecuteRequest
    UseGemini --> ExecuteRequest

    ExecuteRequest --> CheckRate{Rate limit OK?}
    CheckRate -->|No| Wait[Wait with backoff]
    Wait --> CheckRate
    CheckRate -->|Yes| CallAPI[Call API]

    CallAPI --> Success{Success?}
    Success -->|Yes| TrackMetrics[Track in Langfuse]
    Success -->|No| Retry{Retry?}

    Retry -->|Yes| ExecuteRequest
    Retry -->|No| Fallback{Fallback available?}

    Fallback -->|Yes| AutoSelect
    Fallback -->|No| Error

    TrackMetrics --> Response[Return response]
```

---

## Class Hierarchy

### Daemon System

```mermaid
classDiagram
    class DevDaemon {
        +RoadmapParser parser
        +GitManager git
        +ClaudeCLIInterface claude_cli
        +NotificationDB notifications
        +run()
        +stop()
        -_check_prerequisites()
    }

    class GitOpsMixin {
        -_sync_roadmap_branch()
        -_merge_to_roadmap()
        -_create_feature_branch()
    }

    class SpecManagerMixin {
        -_create_technical_spec()
        -_check_spec_needed()
        -_write_spec_file()
    }

    class ImplementationMixin {
        -_implement_priority()
        -_verify_dod()
        -_create_pull_request()
    }

    class StatusMixin {
        -_write_status()
        -_update_subtask()
        -_get_current_status()
    }

    DevDaemon --|> GitOpsMixin
    DevDaemon --|> SpecManagerMixin
    DevDaemon --|> ImplementationMixin
    DevDaemon --|> StatusMixin
```

### AI Provider System

```mermaid
classDiagram
    class AIProvider {
        <<interface>>
        +generate(prompt: str) str
        +stream(prompt: str) Iterator
        +get_model_info() dict
    }

    class ClaudeProvider {
        -client: Anthropic
        -model: str
        +generate(prompt: str) str
        +stream(prompt: str) Iterator
    }

    class OpenAIProvider {
        -client: OpenAI
        -model: str
        +generate(prompt: str) str
        +stream(prompt: str) Iterator
    }

    class GeminiProvider {
        -client: GenerativeModel
        -model: str
        +generate(prompt: str) str
        +stream(prompt: str) Iterator
    }

    class AIService {
        -providers: dict
        -fallback_chain: list
        +execute(prompt: str) str
        +classify_request(input: str) dict
        -_select_provider() AIProvider
    }

    AIProvider <|.. ClaudeProvider
    AIProvider <|.. OpenAIProvider
    AIProvider <|.. GeminiProvider
    AIService --> AIProvider
```

### Configuration System

```mermaid
classDiagram
    class ConfigManager {
        <<static>>
        -_cache: dict
        +get_anthropic_api_key(required: bool) str
        +get_openai_api_key(required: bool) str
        +get_gemini_api_key(required: bool) str
        +get_langfuse_keys() tuple
        -_get_from_env(key: str) str
        -_get_from_file(path: str) str
    }

    class CoffeeMakerError {
        <<exception>>
        +message: str
        +context: dict
    }

    class ConfigError {
        <<exception>>
    }

    class APIKeyMissingError {
        <<exception>>
        +key_name: str
        +env_file: str
    }

    CoffeeMakerError <|-- ConfigError
    ConfigError <|-- APIKeyMissingError

    ConfigManager ..> APIKeyMissingError : raises
```

---

## Integration Points

### Langfuse Observability

```mermaid
graph LR
    subgraph "Application Layer"
        Daemon[Daemon]
        AIService[AI Service]
        Providers[AI Providers]
    end

    subgraph "Observability Layer"
        Decorators[@observe decorators]
        Traces[Trace capture]
        Metrics[Metrics collection]
    end

    subgraph "External Service"
        Langfuse[(Langfuse Cloud)]
    end

    Daemon --> Decorators
    AIService --> Decorators
    Providers --> Decorators

    Decorators --> Traces
    Decorators --> Metrics

    Traces --> Langfuse
    Metrics --> Langfuse
```

**Key Features**:
- All AI calls automatically traced
- Cost tracking per provider
- Performance metrics (latency, tokens)
- Error rate monitoring
- Model comparison analytics

### GitHub Integration

```mermaid
graph LR
    subgraph "Daemon"
        GitOps[GitOpsMixin]
        PRCreation[PR Creation]
    end

    subgraph "Git Manager"
        Commit[Git Commit]
        Push[Git Push]
        Branch[Branch Management]
    end

    subgraph "GitHub API (gh CLI)"
        PR[Create PR]
        Status[Check Status]
        Review[Request Review]
    end

    GitOps --> Commit
    GitOps --> Push
    GitOps --> Branch
    PRCreation --> PR
    PR --> Status
    PR --> Review
```

---

## Design Patterns

### 1. Mixin Pattern (Daemon)

**Purpose**: Break down monolithic `DevDaemon` class into focused concerns

**Benefits**:
- Single Responsibility Principle
- Easier testing of individual mixins
- Better code organization
- Reusable components

**Example**:
```python
class DevDaemon(GitOpsMixin, SpecManagerMixin,
                ImplementationMixin, StatusMixin):
    """Main daemon composed from focused mixins."""
    pass
```

### 2. Strategy Pattern (AI Providers)

**Purpose**: Allow runtime selection of AI providers

**Benefits**:
- Provider agnostic code
- Easy to add new providers
- Fallback chain support
- Provider-specific optimization

**Example**:
```python
providers = {
    "claude": ClaudeProvider(),
    "openai": OpenAIProvider(),
    "gemini": GeminiProvider()
}
service.execute(prompt, provider="claude")  # Runtime selection
```

### 3. Singleton Pattern (ConfigManager)

**Purpose**: Centralize configuration with caching

**Benefits**:
- Single source of truth
- Cached API keys (performance)
- Consistent error handling
- Easy to mock in tests

**Example**:
```python
# All files use the same cached instance
api_key = ConfigManager.get_anthropic_api_key()
```

### 4. Observer Pattern (Langfuse)

**Purpose**: Track execution without coupling code to observability

**Benefits**:
- Non-invasive instrumentation
- Automatic trace capture
- Decorators for clean code
- Easy to disable for testing

**Example**:
```python
@observe(name="implement_priority")
def _implement_priority(self, priority):
    # Automatically traced without explicit calls
    pass
```

---

## Performance Considerations

### Test Suite Optimization

**Problem**: Original test suite took 169 seconds (2m 49s)

**Solution**:
- Marked slow tests with `@pytest.mark.slow`
- Created pytest.ini with marker configuration
- Run fast tests by default: `pytest -m "not slow"`

**Result**:
- Fast tests: 21.5 seconds (87% improvement!)
- Slow tests: Run separately for integration testing
- 757 tests pass in <30 seconds

### Rate Limiting Strategy

**Problem**: API rate limits can cause failures

**Solution**:
- Proactive rate tracking (not reactive)
- Safety margins (N-2 requests)
- Exponential backoff retry
- Per-model tracking

**Benefits**:
- Prevent rate limit errors before they happen
- Optimal API utilization
- Automatic recovery from transient failures

---

## Security Considerations

### API Key Management

**Requirements**:
1. Never commit API keys to git
2. Use environment variables or `.env` files
3. Fail fast on missing keys
4. Clear error messages for debugging

**Implementation**:
```python
# ConfigManager.get_anthropic_api_key(required=True)
# Raises APIKeyMissingError with helpful message:
#   "ANTHROPIC_API_KEY not found. Set in .env or environment."
```

### Code Isolation

**Daemon Safety**:
- Runs in isolated git branches
- Creates PRs for review (never direct push to main)
- User approval required for critical operations
- All changes tracked in Langfuse

---

## Appendix: Key Files

### Configuration
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/config/manager.py` - ConfigManager
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.env` - Environment variables
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/pyproject.toml` - Dependencies

### Daemon System
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon.py` - Main daemon
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/roadmap_parser.py` - ROADMAP parsing
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/git_manager.py` - Git operations

### AI Service
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/ai_service/ai_service.py` - Main AI service
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/ai_service/claude_provider.py` - Claude integration
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/ai_service/openai_provider.py` - OpenAI integration
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/ai_service/gemini_provider.py` - Gemini integration

### Testing
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/pytest.ini` - Test configuration
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/tests/unit/` - Unit tests (<30s)
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/tests/integration/` - Integration tests (slower)

---

**Document Maintainers**: code_developer
**Last Review**: 2025-10-16
**Next Review**: After major architecture changes

🤖 *Generated with [Claude Code](https://claude.com/claude-code) via code_developer*
