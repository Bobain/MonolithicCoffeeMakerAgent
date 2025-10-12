# Prompt Management System - Technical Documentation

**Status**: Phase 1 Complete, Phase 2 (Langfuse) Planned
**Created**: 2025-10-12
**Related**: PRIORITY 8 (Multi-AI Provider Support), PRIORITY 4.1 (Puppeteer MCP)

---

## Overview

Coffee Maker's prompt management system provides centralized, observable, and multi-provider prompt management. The system has two phases:

1. **Phase 1 (Completed)**: Local centralization in `.claude/commands/`
2. **Phase 2 (Planned)**: Langfuse integration as source of truth

---

## Architecture

### Phase 1: Local Prompt Management (✅ Complete)

```
┌──────────────────────────────────────────────────────┐
│             .claude/commands/                         │
│  ┌────────────────────────────────────────────┐     │
│  │  create-technical-spec.md                  │     │
│  │  implement-documentation.md                │     │
│  │  implement-feature.md                      │     │
│  │  test-web-app.md                           │     │
│  │  capture-visual-docs.md                    │     │
│  │  fix-github-issue.md                       │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────────┬───────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   PromptLoader          │
              │  (prompt_loader.py)     │
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │ daemon_ │      │ daemon_ │      │ daemon_ │
    │  spec_  │      │  impl_  │      │ status  │
    │ manager │      │ mentation│      │         │
    └─────────┘      └─────────┘      └─────────┘
```

### Phase 2: Langfuse Integration (📝 Planned)

```
┌──────────────────────────────────────────────────────────┐
│                    Langfuse                               │
│  ┌────────────────────────────────────────────┐          │
│  │  Production Prompts (Source of Truth)      │          │
│  │  - Version control                         │          │
│  │  - A/B testing                             │          │
│  │  - Observability                           │          │
│  │  - Metrics                                 │          │
│  └────────────────────────────────────────────┘          │
└──────────────────────────┬───────────────────────────────┘
                           │ Sync
              ┌────────────▼────────────┐
              │  LangfusePromptSync     │
              │  - Pull latest prompts  │
              │  - Cache locally        │
              │  - Track usage          │
              └────────────┬────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│         .claude/commands/ (Local Cache)               │
│  - Synced from Langfuse production labels            │
│  - Fallback for offline usage                        │
│  - Fast local access                                 │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │   PromptLoader          │
          │  + Langfuse tracking    │
          └────────────┬────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
      ┌────▼────┐            ┌────▼────┐
      │  Agents  │            │ Langfuse│
      │ Execution│──observe──▶│  Cloud  │
      └──────────┘            └─────────┘
```

---

## Phase 1: Implementation Details (✅ Complete)

### 1. Prompt Files Location

**Directory**: `.claude/commands/`

All prompts are stored as Markdown files with `$VARIABLE_NAME` placeholders:

```
.claude/commands/
├── create-technical-spec.md        # Technical spec generation
├── implement-documentation.md      # Documentation tasks
├── implement-feature.md            # Feature implementation
├── test-web-app.md                # Puppeteer web testing
├── capture-visual-docs.md         # Visual documentation
└── fix-github-issue.md            # GitHub issue fixing
```

### 2. Prompt Template Format

**Example**: `create-technical-spec.md`

```markdown
Create a detailed technical specification for implementing $PRIORITY_NAME.

Read the user story from docs/ROADMAP.md and create a comprehensive technical spec.

**Your Task:**
1. Read docs/ROADMAP.md to understand $PRIORITY_NAME
2. Create docs/$SPEC_FILENAME with detailed technical specification
3. Include:
   - Prerequisites & Dependencies
   - Architecture Overview
   ...

**User Story Context:**
$PRIORITY_CONTEXT

Create the spec now in docs/$SPEC_FILENAME.
```

**Variables** (substituted at runtime):
- `$PRIORITY_NAME`: e.g., "US-021"
- `$SPEC_FILENAME`: e.g., "US_021_TECHNICAL_SPEC.md"
- `$PRIORITY_CONTEXT`: Content from ROADMAP

### 3. PromptLoader API

**File**: `coffee_maker/autonomous/prompt_loader.py`

```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

# Load a prompt with variables
prompt = load_prompt(
    PromptNames.CREATE_TECHNICAL_SPEC,
    {
        "PRIORITY_NAME": "US-021",
        "SPEC_FILENAME": "US_021_TECHNICAL_SPEC.md",
        "PRIORITY_CONTEXT": "Split daemon.py into smaller files..."
    }
)
```

**Key Features**:
- Variable substitution (`$VAR_NAME` → value)
- List available prompts
- Check prompt existence
- Error handling for missing prompts

### 4. Integration Points

**daemon_spec_manager.py**:
```python
# Before: Hardcoded prompt
return f"""Create a detailed technical specification..."""

# After: Centralized prompt
return load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {...})
```

**daemon_implementation.py**:
```python
# Documentation tasks
return load_prompt(PromptNames.IMPLEMENT_DOCUMENTATION, {...})

# Feature tasks
return load_prompt(PromptNames.IMPLEMENT_FEATURE, {...})
```

---

## Phase 2: Langfuse Integration (📝 Planned)

### User Story

> "As a user, I need all prompts stored in Langfuse as the source of truth.
> The prompts in .claude/commands are OK as long as they are copies of
> production-labeled prompts from Langfuse. I need this for efficient
> observability in Langfuse."

### Architecture Components

#### 1. Langfuse Prompt Management

**Langfuse Features to Use**:
- **Prompt Versioning**: Track prompt changes over time
- **Production Labels**: Mark stable prompts for production use
- **A/B Testing**: Test prompt variations
- **Metrics**: Track success rates, latency, costs
- **Observability**: View all prompt executions

**Prompt Structure in Langfuse**:
```python
{
  "name": "create-technical-spec",
  "version": 3,
  "labels": ["production"],
  "template": "Create a detailed technical specification for {{PRIORITY_NAME}}...",
  "variables": ["PRIORITY_NAME", "SPEC_FILENAME", "PRIORITY_CONTEXT"],
  "metadata": {
    "provider": "anthropic",
    "model": "claude-sonnet-4",
    "usage": "daemon_spec_creation"
  }
}
```

#### 2. LangfusePromptSync (New Component)

**File**: `coffee_maker/autonomous/langfuse_prompt_sync.py`

```python
class LangfusePromptSync:
    """Sync prompts from Langfuse to local cache.

    Features:
    - Pull latest production-labeled prompts from Langfuse
    - Cache locally in .claude/commands/
    - Track prompt versions
    - Handle offline scenarios

    Example:
        >>> sync = LangfusePromptSync()
        >>> sync.pull_prompts()  # Sync from Langfuse
        >>> sync.get_prompt("create-technical-spec")  # Use cached
    """

    def pull_prompts(self) -> bool:
        """Pull latest production prompts from Langfuse."""

    def get_prompt(self, name: str, variables: dict) -> str:
        """Get prompt (from Langfuse or cache)."""

    def track_usage(self, prompt_name: str, execution_id: str):
        """Track prompt usage in Langfuse."""
```

#### 3. Enhanced PromptLoader

**Updated**: `coffee_maker/autonomous/prompt_loader.py`

```python
class PromptLoader:
    def __init__(
        self,
        prompts_dir: Optional[Path] = None,
        use_langfuse: bool = True,  # NEW
        langfuse_client: Optional[LangfuseClient] = None  # NEW
    ):
        self.use_langfuse = use_langfuse
        self.langfuse = langfuse_client

    def load(self, prompt_name: str, variables: dict) -> str:
        """Load prompt from Langfuse (or local cache fallback)."""

        if self.use_langfuse and self.langfuse:
            # Try Langfuse first
            try:
                prompt = self.langfuse.get_prompt(
                    name=prompt_name,
                    label="production"  # Only use production prompts
                )

                # Track prompt fetch in Langfuse
                self.langfuse.trace(
                    name="prompt_fetch",
                    metadata={"prompt": prompt_name}
                )

                return prompt.compile(variables)

            except Exception as e:
                logger.warning(f"Langfuse fetch failed: {e}, using local cache")

        # Fallback to local cache
        return self._load_from_file(prompt_name, variables)
```

#### 4. Observability Integration

**Track All Prompt Executions**:

```python
# In daemon_spec_manager.py
def _build_spec_creation_prompt(self, priority: dict, spec_filename: str) -> str:
    # Load prompt with Langfuse tracking
    prompt = load_prompt(
        PromptNames.CREATE_TECHNICAL_SPEC,
        {
            "PRIORITY_NAME": priority_name,
            "SPEC_FILENAME": spec_filename,
            "PRIORITY_CONTEXT": priority_context,
        }
    )

    # Langfuse will automatically track:
    # - Prompt version used
    # - Variables substituted
    # - Timestamp
    # - Agent (code_developer)

    return prompt

# When executing with Claude
def _ensure_technical_spec(self, priority: dict) -> bool:
    prompt = self._build_spec_creation_prompt(priority, spec_filename)

    # Execute with Langfuse observation
    result = self.claude.execute_prompt(
        prompt,
        timeout=600,
        langfuse_trace_id=self.langfuse.current_trace_id  # Link to prompt
    )

    # Langfuse automatically captures:
    # - Prompt text
    # - Model response
    # - Token usage
    # - Latency
    # - Success/failure
```

### Implementation Plan for Phase 2

#### Step 1: Setup Langfuse Prompts (1-2 hours)

**Tasks**:
1. Create Langfuse account/project (if not exists)
2. Upload all 6 prompts to Langfuse
3. Label as "production"
4. Test manual fetch via Langfuse UI

**Deliverables**:
- All prompts in Langfuse with "production" label
- Document Langfuse project ID, API keys

#### Step 2: Implement LangfusePromptSync (3-4 hours)

**Tasks**:
1. Create `langfuse_prompt_sync.py`
2. Implement `pull_prompts()` method
3. Implement `get_prompt()` with fallback
4. Add CLI command: `coffee_maker prompts sync`
5. Unit tests

**Deliverables**:
- LangfusePromptSync class working
- CLI command to manually sync
- Tests pass

#### Step 3: Enhance PromptLoader (2-3 hours)

**Tasks**:
1. Add Langfuse client to PromptLoader
2. Implement Langfuse-first loading
3. Add fallback to local cache
4. Add observability tracking
5. Update existing code to use enhanced loader

**Deliverables**:
- PromptLoader supports Langfuse
- Seamless fallback to local cache
- All tests pass

#### Step 4: Observability Integration (2-3 hours)

**Tasks**:
1. Link prompt fetches to Langfuse traces
2. Track prompt executions with metadata
3. Add dashboards in Langfuse for prompt metrics
4. Document observability setup

**Deliverables**:
- All prompt executions visible in Langfuse
- Metrics tracked (success rate, latency, cost)
- Dashboard configured

#### Step 5: Testing & Validation (2-3 hours)

**Test Scenarios**:
1. ✅ Fetch prompts from Langfuse
2. ✅ Use cached prompts when offline
3. ✅ Track prompt usage in Langfuse
4. ✅ Version updates reflected
5. ✅ A/B testing works (future)

**Deliverables**:
- All tests pass
- Documentation complete
- User guide written

---

## Benefits

### Phase 1 Benefits (✅ Achieved)

1. **Multi-AI Provider Support**
   - Prompts work with Claude, Gemini, OpenAI
   - Easy migration between providers
   - Consistent prompt format

2. **Maintainability**
   - Single source of truth (local)
   - Easy to update prompts
   - Version control in git

3. **Developer Experience**
   - Clear separation of prompts from code
   - IDE autocomplete for prompt names
   - Variable validation

### Phase 2 Benefits (📝 Planned)

1. **Observability**
   - See all prompt executions in Langfuse
   - Track success rates, costs, latency
   - Identify problematic prompts

2. **Experimentation**
   - A/B test prompt variations
   - Measure impact of changes
   - Roll back if needed

3. **Collaboration**
   - Non-developers can edit prompts in Langfuse UI
   - Review prompt changes before deployment
   - Audit trail of all modifications

4. **Production Safety**
   - Only use production-labeled prompts
   - Gradual rollout of new versions
   - Automatic rollback on errors

---

## Migration Guide

### For Developers

**Current State**:
```python
# Prompts are hardcoded
prompt = f"""Create a spec for {priority_name}..."""
```

**After Phase 1**:
```python
# Prompts loaded from .claude/commands/
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": priority_name
})
```

**After Phase 2**:
```python
# Same API, but now sources from Langfuse
# (with local cache fallback)
prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": priority_name
})

# Execution is automatically tracked in Langfuse
```

### For Operations

**Prompt Update Process**:

1. **Phase 1 (Current)**:
   ```bash
   # Edit prompt file
   vi .claude/commands/implement-feature.md

   # Commit to git
   git add .claude/commands/
   git commit -m "Update feature implementation prompt"
   ```

2. **Phase 2 (Planned)**:
   ```bash
   # Update in Langfuse UI or API
   langfuse prompts update implement-feature \
     --version 4 \
     --label production

   # Sync to local cache
   coffee_maker prompts sync

   # Changes take effect immediately
   ```

---

## Security Considerations

### API Keys

**Langfuse API Key Storage**:
```bash
# Store in environment (recommended)
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."

# Or in .env file
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

### Prompt Visibility

- Prompts in Langfuse visible to team
- Local cache in `.claude/commands/` version controlled
- No secrets in prompts (use runtime variables)

---

## Monitoring & Metrics

### Langfuse Dashboard

**Key Metrics** (Phase 2):
1. **Prompt Usage**
   - Most used prompts
   - Usage by agent
   - Usage over time

2. **Performance**
   - Average latency per prompt
   - Token usage per prompt
   - Cost per prompt

3. **Quality**
   - Success rate per prompt
   - Error rate per prompt
   - User feedback (if collected)

4. **Versions**
   - Active prompt versions
   - Version rollout status
   - Version comparison

---

## References

- **Phase 1 Implementation**: commit 8c65280
- **Langfuse Docs**: https://langfuse.com/docs/prompts
- **PromptLoader**: `coffee_maker/autonomous/prompt_loader.py`
- **User Story**: "Prompts in Langfuse as source of truth"

---

## Next Steps

### Immediate (Phase 1 Complete)
- ✅ Prompts centralized in .claude/commands/
- ✅ PromptLoader implemented
- ✅ Code updated to use centralized prompts
- ✅ Puppeteer MCP configured

### Short-term (Phase 2)
- [ ] Upload prompts to Langfuse
- [ ] Implement LangfusePromptSync
- [ ] Enhance PromptLoader with Langfuse
- [ ] Add observability tracking
- [ ] Test end-to-end

### Long-term
- [ ] A/B testing framework
- [ ] Automated prompt optimization
- [ ] Multi-language prompt support
- [ ] Prompt marketplace/sharing

---

**Status**: Phase 1 ✅ Complete | Phase 2 📝 Ready to Implement
**Last Updated**: 2025-10-12
