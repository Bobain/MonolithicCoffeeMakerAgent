# REFACTOR-001 - Phase 1: Extract Commands

**Estimated Time**: 5 hours
**Status**: Planned

---

**Step 1.1**: Create `commands/base.py` with `BaseCommand` class (1 hour)
- Define interface
- Add common utilities (error handling, formatting)
- Write unit tests

**Step 1.2**: Extract one command as proof of concept - `ViewCommand` (1 hour)
- Copy code from `roadmap_cli.py`
- Adapt to `BaseCommand` interface
- Test in isolation
- Update `roadmap_cli.py` to use new command

**Step 1.3**: Extract remaining commands (3 hours)
- StatusCommand
- DeveloperStatusCommand
- NotificationsCommand
- RespondCommand
- SpecCommand
- MetricsCommand
- SummaryCommand
- CalendarCommand

---

## Next Phase

**After completing this phase, proceed to**:
- **[Phase 2: Refactor Chat Interface](phase2-refactor-chat-interface.md)**
