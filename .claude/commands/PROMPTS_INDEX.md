# Prompts Index - Agent & Task Mapping

This document provides a complete index of all prompts in `.claude/commands/` and shows which agents use them.

**Last Updated**: 2025-10-12

---

## Agent System Prompts

These prompts define the core behavior and identity of each agent.

### 1. project_manager / assistant

**File**: `agent-project-manager.md`

**Used By**:
- `project_manager` CLI (coffee_maker/cli/ai_service.py)
- `assistant` agent (same AIService class)

**Purpose**: Defines the behavior of the project manager and assistant agents, including:
- Project management strategy
- Communication style
- Roadmap management capabilities
- Response formatting

**Variables**:
- `$TOTAL_PRIORITIES` - Total number of priorities
- `$COMPLETED_PRIORITIES` - Number of completed priorities
- `$IN_PROGRESS_PRIORITIES` - Number of in-progress priorities
- `$PLANNED_PRIORITIES` - Number of planned priorities
- `$PRIORITY_LIST` - Formatted list of current priorities (top 10)

**Updated Via**: `coffee_maker/cli/ai_service.py:381-419` (_build_system_prompt method)

---

### 2. code_developer

**Note**: The `code_developer` agent does NOT have a single system prompt. Instead, it uses **task-specific prompts** (see below) depending on what it needs to do.

**Architecture**:
```python
# code_developer chooses prompts based on task type
if is_documentation_task:
    prompt = load_prompt(PromptNames.IMPLEMENT_DOCUMENTATION, {...})
elif is_feature_task:
    prompt = load_prompt(PromptNames.IMPLEMENT_FEATURE, {...})
elif needs_technical_spec:
    prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {...})
```

**Rationale**: This design allows `code_developer` to be flexible and use the most appropriate prompt for each specific task, rather than having a single rigid system prompt.

---

## Task-Specific Prompts

These prompts are used by the `code_developer` agent for specific implementation tasks.

### 1. create-technical-spec.md

**Used By**: `code_developer` (daemon_spec_manager.py)

**Purpose**: Generate detailed technical specifications for complex priorities

**When Used**: Before implementing any priority with >1 day estimated duration

**Variables**:
- `$PRIORITY_NAME` - Priority identifier (e.g., "US-021")
- `$SPEC_FILENAME` - Output filename (e.g., "US_021_TECHNICAL_SPEC.md")
- `$PRIORITY_CONTEXT` - Full priority content from ROADMAP

**Code Reference**: `coffee_maker/autonomous/daemon_spec_manager.py:150-165`

**Example**:
```python
prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": "US-021",
    "SPEC_FILENAME": "US_021_TECHNICAL_SPEC.md",
    "PRIORITY_CONTEXT": "Split daemon.py into smaller modules..."
})
```

---

### 2. implement-feature.md

**Used By**: `code_developer` (daemon_implementation.py)

**Purpose**: Implement a feature or code-related priority

**When Used**: When priority is NOT documentation-related

**Variables**:
- `$PRIORITY_NAME` - Priority identifier
- `$PRIORITY_TITLE` - Priority title
- `$PRIORITY_CONTENT` - Priority description (truncated to 1000 chars)

**Code Reference**: `coffee_maker/autonomous/daemon_implementation.py:395-419`

**Example**:
```python
prompt = load_prompt(PromptNames.IMPLEMENT_FEATURE, {
    "PRIORITY_NAME": "US-023",
    "PRIORITY_TITLE": "Module Hierarchy Refactoring",
    "PRIORITY_CONTENT": "Reorganize codebase into clear modules..."
})
```

---

### 3. implement-documentation.md

**Used By**: `code_developer` (daemon_implementation.py)

**Purpose**: Create or update documentation

**When Used**: When priority contains keywords: documentation, docs, guide, ux, user experience, quickstart

**Variables**:
- `$PRIORITY_NAME` - Priority identifier
- `$PRIORITY_TITLE` - Priority title
- `$PRIORITY_CONTENT` - Priority description (truncated to 1500 chars)

**Code Reference**: `coffee_maker/autonomous/daemon_implementation.py:369-393`

**Example**:
```python
prompt = load_prompt(PromptNames.IMPLEMENT_DOCUMENTATION, {
    "PRIORITY_NAME": "US-010",
    "PRIORITY_TITLE": "Living Documentation",
    "PRIORITY_CONTENT": "Create comprehensive documentation index..."
})
```

---

### 4. fix-github-issue.md

**Used By**: `code_developer` (planned/future use)

**Purpose**: Resolve GitHub issues automatically

**When Used**: When daemon processes GitHub issue references

**Variables**:
- To be determined based on implementation

**Status**: Prompt created, integration pending

---

### 5. test-web-app.md (Puppeteer)

**Used By**: `code_developer` with Puppeteer MCP

**Purpose**: Test web applications using browser automation

**When Used**: For web testing, validation, and QA tasks

**Variables**:
- To be determined based on implementation

**Status**: Prompt created, Puppeteer MCP integrated, usage patterns TBD

**Related**: PRIORITY 4.1 - Puppeteer MCP Integration

---

### 6. capture-visual-docs.md (Puppeteer)

**Used By**: `code_developer` with Puppeteer MCP

**Purpose**: Capture screenshots and visual documentation

**When Used**: For creating visual guides, UI documentation, etc.

**Variables**:
- To be determined based on implementation

**Status**: Prompt created, Puppeteer MCP integrated, usage patterns TBD

**Related**: PRIORITY 4.1 - Puppeteer MCP Integration

---

### 7. verify-dod-puppeteer.md (Puppeteer) ⭐ NEW

**Used By**: All agents (code_developer, project_manager, assistant)

**Purpose**: Comprehensive Definition of Done verification using Puppeteer browser automation

**When Used**:
- After implementation to verify all acceptance criteria are met
- Before marking priorities as complete
- When user requests DoD verification
- Autonomously by code_developer for web-based features

**Variables**:
- `$PRIORITY_NAME` - Priority identifier (e.g., "US-031")
- `$PRIORITY_TITLE` - Priority title
- `$ACCEPTANCE_CRITERIA` - Formatted list of acceptance criteria
- `$APP_URL` - URL of the application to test

**Code Reference**:
- Used via `PuppeteerClient` in `coffee_maker/autonomous/puppeteer_client.py`
- Integrated in `daemon_implementation.py:478-523` (_verify_dod_with_puppeteer method)

**Example**:
```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

prompt = load_prompt(PromptNames.VERIFY_DOD_PUPPETEER, {
    "PRIORITY_NAME": "US-031",
    "PRIORITY_TITLE": "Custom AI Environment",
    "ACCEPTANCE_CRITERIA": "- [ ] Web UI loads\n- [ ] All features visible",
    "APP_URL": "http://localhost:8501"
})
```

**Features**:
- Systematic verification of all acceptance criteria
- Screenshots as evidence for each criterion
- Console error checking
- Performance observations
- Clear pass/fail recommendations
- Ready-for-merge status

**Status**: ✅ Integrated - All agents can now verify DoD with Puppeteer

**Related**: US-032 - Puppeteer DoD Integration

---

## Tool Capabilities

All agents have access to powerful tools for enhanced autonomy:

### Puppeteer MCP (Browser Automation)

**Available Since**: PRIORITY 4.1 (2025-10-12)

**What It Does**:
- Navigate to web pages
- Take screenshots
- Test interactive elements (click, fill, select, hover)
- Execute JavaScript in browser console
- Verify web application functionality

**Tools Available**:
- `puppeteer_navigate` - Navigate to URLs
- `puppeteer_screenshot` - Capture screenshots
- `puppeteer_click` - Click elements
- `puppeteer_fill` - Fill input fields
- `puppeteer_select` - Select dropdown options
- `puppeteer_hover` - Hover over elements
- `puppeteer_evaluate` - Execute JavaScript

**Used By**: All agents (project_manager, assistant, code_developer)

**Primary Use Cases**:
1. **DoD Verification**: Autonomously verify that web features meet acceptance criteria
2. **Visual Documentation**: Capture screenshots for documentation
3. **Web Testing**: Test Streamlit apps, dashboards, web UIs
4. **Deployment Verification**: Confirm apps are live and working

**Configuration**: `.claude/mcp/puppeteer.json` or `~/Library/Application Support/Claude/config.json`

---

### GitHub CLI (`gh`)

**Available Since**: 2025-10-12 (US-032)

**What It Does**:
- Manage GitHub issues and pull requests
- Check CI/CD status
- Link roadmap priorities to GitHub
- Automate PR creation

**Common Commands**:
- `gh issue list` - List issues
- `gh issue view <number>` - View issue details
- `gh pr create` - Create pull request
- `gh pr list` - List PRs
- `gh pr checks` - Check CI status
- `gh repo view` - View repository info

**Used By**: All agents (project_manager, assistant, code_developer)

**Primary Use Cases**:
1. **Issue Management**: View and track GitHub issues
2. **PR Automation**: Create PRs after implementation
3. **Status Monitoring**: Check build/test status
4. **Workflow Integration**: Connect ROADMAP to GitHub

**Integration**: Prompts updated to include `gh` usage examples

---

## Multi-AI Provider Support

All prompts in `.claude/commands/` are designed to work with **multiple AI providers**:

✅ **Claude** (current default)
✅ **Gemini** (ready to use)
✅ **OpenAI** (ready to use)

### How to Switch Providers

**Example - Using Gemini**:
```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames
from coffee_maker.ai_providers.providers.gemini_provider import GeminiProvider

# Load prompt (same API for all providers)
prompt = load_prompt(PromptNames.IMPLEMENT_FEATURE, {
    "PRIORITY_NAME": "US-031",
    "PRIORITY_TITLE": "Custom AI Environment",
    "PRIORITY_CONTENT": "..."
})

# Execute with Gemini instead of Claude
provider = GeminiProvider()
result = provider.execute(prompt)
```

**No changes to prompts needed!** The same prompt templates work across all providers.

---

## Langfuse Integration (Phase 2 - Planned)

**Goal**: Langfuse becomes the source of truth for prompts

**Architecture**:
```
Langfuse (production prompts)
    ↓ sync
.claude/commands/ (local cache)
    ↓ load
PromptLoader → Agents
    ↓ track
Langfuse (observability)
```

**Benefits**:
1. Version control for prompts in Langfuse
2. A/B testing of prompt variations
3. Track success rates, costs, latency per prompt
4. Team collaboration on prompt engineering
5. Production labels for stable prompts
6. Automatic rollback on failures

**Timeline**: 10-14 hours estimated

**Related Documentation**: `docs/PROMPT_MANAGEMENT_SYSTEM.md`

---

## Usage Guidelines

### For Developers

**Adding a New Prompt**:
1. Create `.claude/commands/my-new-prompt.md`
2. Use `$VARIABLE_NAME` for placeholders
3. Add to `PromptNames` class in `prompt_loader.py`
4. Update this index document
5. Use `load_prompt(PromptNames.MY_NEW_PROMPT, {...})` in code

**Modifying Existing Prompts**:
1. Edit the `.md` file directly
2. Test with current agents
3. Update documentation if variables change
4. Eventually: Sync to Langfuse (Phase 2)

### For Users

**Viewing Prompts**:
```bash
# List all prompts
ls .claude/commands/

# View a specific prompt
cat .claude/commands/agent-project-manager.md
```

**Understanding Agent Behavior**:
- Want to know how `project_manager` thinks? → Read `agent-project-manager.md`
- Want to know how `code_developer` implements features? → Read `implement-feature.md`
- Want to know how specs are created? → Read `create-technical-spec.md`

---

## File Structure

```
.claude/commands/
├── PROMPTS_INDEX.md              # This file
├── agent-project-manager.md      # project_manager/assistant system prompt (updated with Puppeteer + gh)
├── create-technical-spec.md      # Spec generation (code_developer)
├── implement-feature.md          # Feature implementation (updated with Puppeteer + gh)
├── implement-documentation.md    # Documentation tasks (updated with Puppeteer + gh)
├── verify-dod-puppeteer.md       # DoD verification with Puppeteer ⭐ NEW
├── fix-github-issue.md           # GitHub issue resolution (future)
├── test-web-app.md              # Web testing with Puppeteer (future)
└── capture-visual-docs.md       # Visual docs with Puppeteer (future)
```

---

## Related Documentation

- **Prompt Management System**: `docs/PROMPT_MANAGEMENT_SYSTEM.md`
- **PromptLoader API**: `coffee_maker/autonomous/prompt_loader.py`
- **CLAUDE.md**: `.claude/CLAUDE.md` (project instructions)
- **ROADMAP**: `docs/ROADMAP.md`

---

## Version History

- **2025-10-12 (v2)**: US-032 - Puppeteer DoD Integration + GitHub CLI
  - ⭐ Added `verify-dod-puppeteer.md` prompt for autonomous DoD verification
  - Updated all agent prompts with Puppeteer MCP capabilities
  - Added GitHub CLI (`gh`) integration to all agent prompts
  - Created `PuppeteerClient` utility class for agents
  - Integrated DoD verification into `code_developer` workflow
  - Documented tool capabilities (Puppeteer + gh)
  - All agents can now autonomously verify DoD with browser automation

- **2025-10-12 (v1)**: Initial index created
  - Extracted project_manager system prompt
  - Documented all existing prompts
  - Created comprehensive agent mapping

---

**For Questions**: See `.claude/CLAUDE.md` or `docs/PROMPT_MANAGEMENT_SYSTEM.md`
