# REFACTOR-003 - Phase 2: Apply to Critical Path - daemon.py

**Estimated Time**: 3 hours
**Status**: Planned

---

**Step 2.1**: Add defensive file operations (1 hour)
```python
# Before
content = self.roadmap_path.read_text()

# After
from coffee_maker.utils.defensive_io import DefensiveFileMixin

class DevDaemon(DefensiveFileMixin, ...):
    def _read_roadmap(self):
        content = self.read_file_safely(
            self.roadmap_path,
            default="# Empty Roadmap\n\nNo priorities defined."
        )
        if content is None:
            logger.error("Failed to read roadmap, using default")
            content = "# Empty Roadmap\n"
        return content
```

**Step 2.2**: Add retry logic to API calls (1 hour)
```python
# Before
result = self.claude.execute_prompt(prompt)

# After
from coffee_maker.utils.retry import retry_with_backoff

@retry_with_backoff(max_attempts=3, initial_delay=2.0)
def _call_claude_with_retry(self, prompt: str):
    return self.claude.execute_prompt(prompt)
```

**Step 2.3**: Add input validation (1 hour)
```python
# Before
priority_name = next_priority['name']

# After
from coffee_maker.utils.validation import Validator

priority_name = Validator.validate_not_empty(
    next_priority.get('name'),
    'priority name'
)
```

---

## Next Phase

**After completing this phase, proceed to**:
- **[Phase 3: Apply to Core Modules](phase3-apply-to-core-modules.md)**
