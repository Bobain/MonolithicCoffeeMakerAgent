# Simplified Command Architecture

## 🎯 From 100 Commands → 36 Commands (-64% reduction)

## Command Summary by Agent

### 1. project_manager (5 commands)
```yaml
roadmap:      # View/update ROADMAP priorities (list, details, status)
status:       # Developer status and notifications
dependencies: # Check and manage dependencies
github:       # PR/issue monitoring and sync
stats:        # Project metrics and statistics
```

### 2. architect (5 commands)
```yaml
spec:          # Create/update/approve technical specifications
tasks:         # Decompose specs into tasks and manage them
documentation: # ADRs, guidelines, style guides
review:        # Architecture validation and compliance
dependencies:  # Technical dependency management
```

### 3. code_developer (6 commands)
```yaml
implement: # Claim priority → work → complete (full lifecycle)
test:      # Run tests, fix failures, generate coverage
git:       # Commits and pull requests
review:    # Request and track code reviews
quality:   # Pre-commit hooks, metrics, linting
config:    # Update configurations
```

### 4. code_reviewer (4 commands)
```yaml
review:  # Generate comprehensive review reports with scoring
analyze: # Style/security/complexity/coverage/type analysis
monitor: # Detect new commits and track issues
notify:  # Alert architects of critical findings
```

### 5. orchestrator (5 commands)
```yaml
agents:      # Spawn/kill/restart/monitor agent lifecycle
orchestrate: # Coordinate work and detect deadlocks
worktree:    # Manage git worktrees for parallel work
messages:    # Route inter-agent communication
monitor:     # Resource usage and activity summaries
```

### 6. assistant (4 commands)
```yaml
demo:     # Create/record/validate demos with Puppeteer
bug:      # Report and track bugs
delegate: # Classify requests and route to agents
docs:     # Generate documentation and READMEs
```

### 7. user_listener (3 commands)
```yaml
understand:   # Classify intent and extract entities
route:        # Route requests to appropriate agents
conversation: # Manage conversation context and session
```

### 8. ux_design_expert (4 commands)
```yaml
design:     # Create UI and component specifications
components: # Manage component library, Tailwind, design tokens
review:     # Review UI implementations and accessibility
debt:       # Track and manage design debt
```

## Key Benefits of Consolidation

### 1. **Easier to Learn**
- 36 commands vs 100 commands
- Consistent patterns across agents
- Parameter-driven sub-actions

### 2. **Better Workflow**
- Lifecycle commands (e.g., `implement` handles claim→work→complete)
- Related operations grouped together
- Fewer context switches

### 3. **More Maintainable**
- Less code duplication
- Shared parameter validation
- Easier to test

### 4. **Better UX**
```python
# Clear and intuitive:
project_manager.roadmap(action="list", status="blocked")
architect.spec(action="create", title="New Feature")
code_developer.implement(priority_id="PRIORITY-28", phase="complete")

# Instead of remembering:
# check_priority_status, get_priority_details, list_all_priorities,
# update_priority_metadata, etc.
```

## Migration Strategy

### Phase 1: Update SPECs
- Revise SPEC-102 through SPEC-114
- Consolidate command definitions
- Update database schemas

### Phase 2: Implement Consolidated Commands
- Each command accepts `action` parameter
- Backward compatibility via command aliases
- Gradual deprecation of old commands

### Phase 3: Update Documentation
- Simplified command reference
- Workflow examples
- Migration guide for existing code

## Example: Consolidated Command Implementation

```python
class ProjectManagerCommands:
    def roadmap(self, action="list", **params):
        """Unified ROADMAP operations."""
        actions = {
            "list": self._list_priorities,
            "details": self._get_priority_details,
            "update": self._update_priority,
            "status": self._check_priority_status
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return actions[action](**params)

    def _list_priorities(self, status=None, assignee=None):
        """List priorities with optional filters."""
        # Implementation

    def _get_priority_details(self, priority_id):
        """Get detailed information about a priority."""
        # Implementation
```

## Command Comparison

| Before (100 commands) | After (36 commands) | Reduction |
|-----------------------|---------------------|-----------|
| Hard to discover | Easy to learn | -64% cognitive load |
| Many small functions | Fewer rich functions | -60% API surface |
| Scattered functionality | Logical groupings | Better organization |
| Lots of duplication | DRY principle | Less maintenance |

## Next Steps

1. **Get Approval** - Review with team
2. **Update SPECs** - Revise specifications in database
3. **Implement** - Create consolidated commands
4. **Document** - Update all documentation
5. **Migrate** - Gradual rollout with aliases
