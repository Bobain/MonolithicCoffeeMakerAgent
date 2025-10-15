# User Listener - Your Primary Interface

**user_listener** is the ONLY agent with a user interface. All interactions with the Coffee Maker Agent system go through user_listener.

---

## What is user_listener?

user_listener is an intelligent dispatcher that:
1. **Listens** to your requests
2. **Interprets** your intent
3. **Delegates** to appropriate team members
4. **Synthesizes** responses back to you

Think of user_listener as your personal assistant who knows exactly which expert to consult for any task.

---

## How to Use

### Starting the Interface

```bash
# Interactive chat mode
poetry run user-listener

# Specific commands
poetry run user-listener <command>
```

### Available Commands

**ACE Framework**:
- `curate [agent]` - Trigger ACE curation
- `playbook [agent]` - View agent playbook
- `ace-status [agent]` - Show ACE framework status

**Project Management**:
- `status` - Project status
- `roadmap` - View ROADMAP
- `metrics` - Development metrics
- `summary` - Recent completions

**Code & Analysis**:
- `search <query>` - Search codebase
- `analyze <file>` - Analyze specific file

**General**:
- `agents` - List all team members with colors
- `help` - Show help

---

## How Delegation Works

When you make a request, user_listener:

1. **Interprets** your intent
2. **Identifies** which team member(s) to involve
3. **Delegates** to appropriate agents
4. **Shows** which agent is working (with colors!)
5. **Synthesizes** the final response

### Example

```
You: "What's the status of the ACE framework?"

[blue]user_listener:[/blue] Asking project_manager for ACE status...
[green]project_manager:[/green] Checking ROADMAP and implementation tracker...
[green]project_manager:[/green] ACE Framework Status:
  - Phases 1-4: Complete (80%)
  - Phase 5: Planned
  - 172 tests passing

[blue]user_listener:[/blue] Summary: ACE framework is 80% complete and ready for production!
```

---

## Agent Colors

Each agent has a color for easy identification:
- **user_listener**: blue (that's me!)
- **code_developer**: cyan
- **project_manager**: green
- **code-searcher**: purple
- **ux-design-expert**: magenta
- **assistant**: yellow
- **generator**: orange
- **reflector**: teal
- **curator**: pink

---

## Team Members

user_listener can delegate to:

| Agent | Responsibility |
|-------|---------------|
| **code_developer** | Write/modify code, create PRs |
| **project_manager** | Strategic planning, ROADMAP, monitoring (backend only) |
| **code-searcher** | Deep code analysis, forensics |
| **ux-design-expert** | Design decisions, UI/UX |
| **assistant** | General help, documentation expert |
| **generator** | ACE execution observation |
| **reflector** | ACE insight extraction |
| **curator** | ACE playbook management |

---

## Why Only One UI?

Having user_listener as the ONLY UI provides:
- **Clarity**: One entry point for all interactions
- **Intelligence**: Automatic routing to right expert
- **Attribution**: You see which agent did what
- **Coordination**: Multi-agent tasks handled seamlessly
- **Consistency**: Same interface for all operations

---

## Common Use Cases

### Checking Project Status

```bash
poetry run user-listener status
```

user_listener delegates to project_manager (backend) and returns formatted status.

### Implementing a Feature

```bash
poetry run user-listener "Implement authentication feature"
```

user_listener delegates to code_developer for implementation, shows progress, and reports results.

### Searching the Codebase

```bash
poetry run user-listener search "authentication"
```

user_listener delegates to code-searcher for deep analysis, synthesizes findings.

### Triggering ACE Curation

```bash
poetry run user-listener curate code_developer
```

user_listener delegates to curator to update playbook, shows curation summary.

### Viewing Playbook

```bash
poetry run user-listener playbook code_developer
```

user_listener delegates to curator to load playbook, displays formatted content.

---

## FAQs

**Q: Can I talk directly to other agents?**
A: No - all agents except user_listener are backend only. user_listener handles all communication.

**Q: What if I need project_manager specifically?**
A: Just ask user_listener! It will delegate to project_manager and show you the response.

**Q: How do I know which agent is responding?**
A: Agent names are color-coded in the output. Look for the colored agent name before each message.

**Q: Can user_listener handle multiple agents at once?**
A: Yes! user_listener can coordinate multiple agents for complex requests.

**Q: What happened to project-manager chat?**
A: project_manager is now backend-only. Use user_listener for all UI interactions.

**Q: Why the change?**
A: Clear separation of concerns: user_listener (UI) vs project_manager (backend strategic operations).

---

## Advanced Features

### Multi-Agent Coordination

user_listener can coordinate multiple agents for complex tasks:

```
You: "Fix the bug in CLI and update the documentation"

[blue]user_listener:[/blue] I'll coordinate this for you:
  1. code_developer - Fix bug in CLI (code changes)
  2. project_manager - Update docs (backend doc management)

[cyan]code_developer:[/cyan] Fixing bug in roadmap_cli.py...
[cyan]code_developer:[/cyan] Bug fixed! Tests passing.

[green]project_manager:[/green] Updating documentation...
[green]project_manager:[/green] docs/ROADMAP_CLI_USAGE.md updated.

[blue]user_listener:[/blue] Complete! Bug fixed and docs updated.
```

### Intelligent Intent Detection

user_listener understands natural language:

```
"What's broken?" → Delegates to project_manager for error analysis
"Make it faster" → Delegates to code_developer for optimization
"Show me the code" → Delegates to code-searcher for analysis
"What should this look like?" → Delegates to ux-design-expert for design
```

### Context Preservation

user_listener maintains context across the conversation:

```
You: "What's the status of US-015?"
[blue]user_listener:[/blue] US-015 (Metrics Tracking) is 80% complete...

You: "When will it be done?"
[blue]user_listener:[/blue] [remembers US-015 context] Estimated completion: 1-2 days...

You: "Show me the code"
[blue]user_listener:[/blue] [delegates to code-searcher for US-015 code]
```

---

## Troubleshooting

### user_listener not responding

**Check**:
```bash
# Verify user_listener is installed
poetry run user-listener --version

# Check logs
tail -f logs/user_listener.log
```

### Command not recognized

**Solution**: Use `poetry run user-listener help` to see available commands.

### Agent delegation failing

**Check**:
- Are all agents properly configured in `.claude/agents/`?
- Check agent logs in `logs/` directory
- Report issues to project_manager

---

## Best Practices

1. **Start with user_listener**: Always use user_listener as your entry point
2. **Be specific**: Clear requests get better results
3. **Use colors**: Watch for agent colors to see who's working
4. **Ask for clarification**: user_listener will ask if intent is unclear
5. **Trust the delegation**: user_listener knows which expert to consult

---

## Examples Gallery

### Example 1: Project Status Check

```bash
$ poetry run user-listener status

[blue]user_listener:[/blue] Checking project status...
[green]project_manager:[/green] Project Status Summary:
  - Active: US-015 (Metrics Tracking) - 80% complete
  - Completed this week: US-023, US-014, US-021
  - Tests: 172 passing
  - Velocity: 2.5 priorities/week

[blue]user_listener:[/blue] Project is healthy! 80% through current priority.
```

### Example 2: ACE Playbook Curation

```bash
$ poetry run user-listener curate code_developer

[blue]user_listener:[/blue] Starting ACE curation for code_developer...
[teal]reflector:[/teal] Analyzing 15 traces from last 24 hours...
[teal]reflector:[/teal] Extracted 8 insights (3 success patterns, 2 failure modes, 3 optimizations)
[pink]curator:[/pink] Loading playbook (237 bullets, effectiveness 0.82)...
[pink]curator:[/pink] De-duplicating insights...
[pink]curator:[/pink] Merged 3 insights, added 5 new bullets
[pink]curator:[/pink] Playbook updated: 242 bullets, effectiveness 0.84

[blue]user_listener:[/blue] Curation complete! Playbook improved (+5 bullets, +0.02 effectiveness)
```

### Example 3: Code Search

```bash
$ poetry run user-listener search "authentication"

[blue]user_listener:[/blue] Searching codebase for authentication...
[purple]code-searcher:[/purple] Found 23 files with authentication references
[purple]code-searcher:[/purple] Key files:
  - coffee_maker/auth/login.py (login implementation)
  - coffee_maker/auth/session.py (session management)
  - coffee_maker/middleware/auth_middleware.py (middleware)
[purple]code-searcher:[/purple] Authentication uses bcrypt for hashing, JWT for tokens

[blue]user_listener:[/blue] Authentication is implemented across 3 modules. See summary above.
```

---

## Migration Notes

**If you were using project-manager UI commands**:

| Old Command | New Command |
|-------------|-------------|
| `project-manager curate` | `user-listener curate` |
| `project-manager playbook` | `user-listener playbook` |
| `project-manager chat` | `user-listener` (interactive) |
| `project-manager status` | `user-listener status` |

**Backend operations** (monitoring, strategic planning) remain with project_manager, but accessed through user_listener UI.

---

## Quick Reference Card

```
USER INTERFACE (user_listener)
├─ Interactive: poetry run user-listener
├─ Commands: poetry run user-listener <cmd>
└─ Delegates to team members automatically

TEAM MEMBERS (backend only)
├─ code_developer: Implementation
├─ project_manager: Strategy & monitoring
├─ code-searcher: Deep analysis
├─ ux-design-expert: Design
├─ assistant: General help
├─ generator: ACE observation
├─ reflector: ACE insights
└─ curator: ACE playbooks

COMMON COMMANDS
├─ status: Project status
├─ roadmap: View ROADMAP
├─ metrics: Dev metrics
├─ curate: Trigger ACE curation
├─ playbook: View playbook
├─ search: Search codebase
└─ help: Show help
```

---

**Remember**: user_listener is your ONE interface to the entire team. Just ask what you need, and it will coordinate everything!

**Version**: 1.0
**Last Updated**: 2025-10-15
**Status**: Active - user_listener is the ONLY UI agent
