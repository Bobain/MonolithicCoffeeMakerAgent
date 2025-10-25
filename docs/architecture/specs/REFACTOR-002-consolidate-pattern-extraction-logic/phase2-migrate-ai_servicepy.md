# REFACTOR-002 - Phase 2: Migrate ai_service.py

**Estimated Time**: 2 hours
**Status**: Planned

---

**Step 2.1**: Replace extraction methods (1 hour)
```python
# Before
def _extract_completion_date(self, content: str) -> Optional[datetime]:
    patterns = [...]
    for pattern in patterns:
        ...

# After
from coffee_maker.utils.pattern_extractor import get_extractor

def _extract_completion_date(self, content: str) -> Optional[datetime]:
    return get_extractor().extract('completion_date', content)
```

**Step 2.2**: Update method calls (0.5 hours)
- Update all `_extract_*` calls
- Verify tests pass

**Step 2.3**: Delete old extraction methods (0.5 hours)
- Remove duplicated code
- Update documentation

---

## Next Phase

**After completing this phase, proceed to**:
- **[Phase 3: Migrate status_report_generator.py](phase3-migrate-status_report_generatorpy.md)**
