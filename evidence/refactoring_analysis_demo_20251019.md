# Refactoring Analysis Report

**Date**: 2025-10-19
**Analyzed by**: architect (proactive-refactoring-analysis skill)
**Codebase**:
**LOC**: 79,426 lines Python
**Execution Time**: 0.65s

---

## Executive Summary

**Overall Health Score**: 30.1/100 🔴

**Refactoring Opportunities Found**: 185
**Total Estimated Effort**: 925.5 hours
**Potential Time Savings**: 1507.0 hours (in future)
**ROI**: 1.6x

**Top 3 Priorities**:
1. **Split ai_service.py into smaller modules** (CRITICAL ROI) - 16.0 hours, saves 24.0 hours
2. **Split chat_interface.py into smaller modules** (CRITICAL ROI) - 24.0 hours, saves 36.0 hours
3. **Split status_report_generator.py into smaller modules** (CRITICAL ROI) - 16.0 hours, saves 24.0 hours


---

## Refactoring Opportunities (Sorted by Priority)

### 1. 🥉 Split ai_service.py into smaller modules (CRITICAL Priority)

**Issue**: 1269 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 16.0 hours
**Time Saved (Future)**: 24.0 hours
**ROI**: 1.5x
**Priority**: 10/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/ai_service.py`

---

### 2. 🥉 Split chat_interface.py into smaller modules (CRITICAL Priority)

**Issue**: 1562 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 24.0 hours
**Time Saved (Future)**: 36.0 hours
**ROI**: 1.5x
**Priority**: 10/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/chat_interface.py`

---

### 3. 🥉 Split status_report_generator.py into smaller modules (CRITICAL Priority)

**Issue**: 1093 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 16.0 hours
**Time Saved (Future)**: 24.0 hours
**ROI**: 1.5x
**Priority**: 10/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/reports/status_report_generator.py`

---

### 4. 🥈 Extract mixins from god class in metrics.py (HIGH Priority)

**Issue**: 26 methods in single class

**Proposed Refactoring**: Extract mixins for single responsibility

**Effort**: 12.0 hours
**Time Saved (Future)**: 20.0 hours
**ROI**: 1.7x
**Priority**: 9/10

**Benefits**:
- Single Responsibility Principle
- Easier parallel development
- Better testability

**Risks**:
- Requires careful refactoring
- Must maintain compatibility

**Files Affected**:
- `coffee_maker/langfuse_observe/strategies/metrics.py`

---

### 5. 🥈 Extract mixins from god class in spec_handler.py (HIGH Priority)

**Issue**: 24 methods in single class

**Proposed Refactoring**: Extract mixins for single responsibility

**Effort**: 12.0 hours
**Time Saved (Future)**: 20.0 hours
**ROI**: 1.7x
**Priority**: 9/10

**Benefits**:
- Single Responsibility Principle
- Easier parallel development
- Better testability

**Risks**:
- Requires careful refactoring
- Must maintain compatibility

**Files Affected**:
- `coffee_maker/utils/spec_handler.py`

---

### 6. 🥈 Extract mixins from god class in chat_interface.py (HIGH Priority)

**Issue**: 46 methods in single class

**Proposed Refactoring**: Extract mixins for single responsibility

**Effort**: 12.0 hours
**Time Saved (Future)**: 20.0 hours
**ROI**: 1.7x
**Priority**: 9/10

**Benefits**:
- Single Responsibility Principle
- Easier parallel development
- Better testability

**Risks**:
- Requires careful refactoring
- Must maintain compatibility

**Files Affected**:
- `coffee_maker/cli/chat_interface.py`

---

### 7. 🥈 Extract mixins from god class in team_daemon.py (HIGH Priority)

**Issue**: 22 methods in single class

**Proposed Refactoring**: Extract mixins for single responsibility

**Effort**: 12.0 hours
**Time Saved (Future)**: 20.0 hours
**ROI**: 1.7x
**Priority**: 9/10

**Benefits**:
- Single Responsibility Principle
- Easier parallel development
- Better testability

**Risks**:
- Requires careful refactoring
- Must maintain compatibility

**Files Affected**:
- `coffee_maker/autonomous/team_daemon.py`

---

### 8. 🥈 Extract mixins from god class in api.py (HIGH Priority)

**Issue**: 21 methods in single class

**Proposed Refactoring**: Extract mixins for single responsibility

**Effort**: 12.0 hours
**Time Saved (Future)**: 20.0 hours
**ROI**: 1.7x
**Priority**: 9/10

**Benefits**:
- Single Responsibility Principle
- Easier parallel development
- Better testability

**Risks**:
- Requires careful refactoring
- Must maintain compatibility

**Files Affected**:
- `coffee_maker/autonomous/ace/api.py`

---

### 9. 🥈 Extract mixins from god class in status_report_generator.py (HIGH Priority)

**Issue**: 22 methods in single class

**Proposed Refactoring**: Extract mixins for single responsibility

**Effort**: 12.0 hours
**Time Saved (Future)**: 20.0 hours
**ROI**: 1.7x
**Priority**: 9/10

**Benefits**:
- Single Responsibility Principle
- Easier parallel development
- Better testability

**Risks**:
- Requires careful refactoring
- Must maintain compatibility

**Files Affected**:
- `coffee_maker/reports/status_report_generator.py`

---

### 10. 🥉 Split auto_gemini_styleguide.py into smaller modules (HIGH Priority)

**Issue**: 568 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/auto_gemini_styleguide.py`

---

### 11. 🥉 Split auto_picker_llm_refactored.py into smaller modules (HIGH Priority)

**Issue**: 569 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/langfuse_observe/auto_picker_llm_refactored.py`

---

### 12. 🥉 Split db_schema.py into smaller modules (HIGH Priority)

**Issue**: 711 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/langfuse_observe/analytics/db_schema.py`

---

### 13. 🥉 Split metrics_integration.py into smaller modules (HIGH Priority)

**Issue**: 554 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/utils/metrics_integration.py`

---

### 14. 🥉 Split task_estimator.py into smaller modules (HIGH Priority)

**Issue**: 501 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/utils/task_estimator.py`

---

### 15. 🥉 Split dependency_analyzer.py into smaller modules (HIGH Priority)

**Issue**: 574 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/utils/dependency_analyzer.py`

---

### 16. 🥉 Split spec_handler.py into smaller modules (HIGH Priority)

**Issue**: 731 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/utils/spec_handler.py`

---

### 17. 🥉 Split roadmap_editor.py into smaller modules (HIGH Priority)

**Issue**: 945 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/roadmap_editor.py`

---

### 18. 🥉 Split document_updater.py into smaller modules (HIGH Priority)

**Issue**: 731 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/document_updater.py`

---

### 19. 🥉 Split user_listener.py into smaller modules (HIGH Priority)

**Issue**: 568 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/user_listener.py`

---

### 20. 🥉 Split spec_workflow.py into smaller modules (HIGH Priority)

**Issue**: 540 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/spec_workflow.py`

---

### 21. 🥉 Split metadata_extractor.py into smaller modules (HIGH Priority)

**Issue**: 633 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/metadata_extractor.py`

---

### 22. 🥉 Split user_story_detector.py into smaller modules (HIGH Priority)

**Issue**: 542 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/user_story_detector.py`

---

### 23. 🥉 Split preview_generator.py into smaller modules (HIGH Priority)

**Issue**: 603 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/preview_generator.py`

---

### 24. 🥉 Split utility.py into smaller modules (HIGH Priority)

**Issue**: 654 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/commands/utility.py`

---

### 25. 🥉 Split status.py into smaller modules (HIGH Priority)

**Issue**: 726 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/cli/commands/status.py`

---

### 26. 🥉 Split daemon_implementation.py into smaller modules (HIGH Priority)

**Issue**: 559 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/daemon_implementation.py`

---

### 27. 🥉 Split code_reviewer.py into smaller modules (HIGH Priority)

**Issue**: 889 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/code_reviewer.py`

---

### 28. 🥉 Split story_metrics.py into smaller modules (HIGH Priority)

**Issue**: 715 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/story_metrics.py`

---

### 29. 🥉 Split spec_generator.py into smaller modules (HIGH Priority)

**Issue**: 805 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/spec_generator.py`

---

### 30. 🥉 Split team_daemon.py into smaller modules (HIGH Priority)

**Issue**: 599 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/team_daemon.py`

---

### 31. 🥉 Split message_queue.py into smaller modules (HIGH Priority)

**Issue**: 636 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/message_queue.py`

---

### 32. 🥉 Split orchestrator.py into smaller modules (HIGH Priority)

**Issue**: 972 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/orchestrator.py`

---

### 33. 🥉 Split daemon.py into smaller modules (HIGH Priority)

**Issue**: 958 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/daemon.py`

---

### 34. 🥉 Split startup_skill_executor.py into smaller modules (HIGH Priority)

**Issue**: 567 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/startup_skill_executor.py`

---

### 35. 🥉 Split code_developer_agent.py into smaller modules (HIGH Priority)

**Issue**: 648 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/agents/code_developer_agent.py`

---

### 36. 🥉 Split base_agent.py into smaller modules (HIGH Priority)

**Issue**: 629 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/agents/base_agent.py`

---

### 37. 🥉 Split architect_agent.py into smaller modules (HIGH Priority)

**Issue**: 562 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/agents/architect_agent.py`

---

### 38. 🥉 Split architect_skills_mixin.py into smaller modules (HIGH Priority)

**Issue**: 576 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/agents/architect_skills_mixin.py`

---

### 39. 🥉 Split api.py into smaller modules (HIGH Priority)

**Issue**: 942 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/ace/api.py`

---

### 40. 🥉 Split generator.py into smaller modules (HIGH Priority)

**Issue**: 638 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/autonomous/ace/generator.py`

---

### 41. 🥉 Split test_failure_analyzer.py into smaller modules (HIGH Priority)

**Issue**: 597 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/skills/code_analysis/test_failure_analyzer.py`

---

### 42. 🥉 Split proactive_refactoring_analysis.py into smaller modules (HIGH Priority)

**Issue**: 736 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/skills/refactoring_analysis/proactive_refactoring_analysis.py`

---

### 43. 🥉 Split architecture_reuse_checker.py into smaller modules (HIGH Priority)

**Issue**: 565 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/skills/architecture/architecture_reuse_checker.py`

---

### 44. 🥉 Split proactive_refactoring_analyzer.py into smaller modules (HIGH Priority)

**Issue**: 614 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/skills/architecture/proactive_refactoring_analyzer.py`

---

### 45. 🥉 Split git_workflow_automation.py into smaller modules (HIGH Priority)

**Issue**: 725 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/skills/git_workflow/git_workflow_automation.py`

---

### 46. 🥉 Split 4_📊_Analytics.py into smaller modules (HIGH Priority)

**Issue**: 570 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/streamlit_app/pages/4_📊_Analytics.py`

---

### 47. 🥉 Split continuous_work_loop.py into smaller modules (HIGH Priority)

**Issue**: 567 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/orchestrator/continuous_work_loop.py`

---

### 48. 🥉 Split parallel_execution_coordinator.py into smaller modules (HIGH Priority)

**Issue**: 521 LOC in single file

**Proposed Refactoring**: Split into logical modules or use mixin pattern

**Effort**: 8.0 hours
**Time Saved (Future)**: 12.0 hours
**ROI**: 1.5x
**Priority**: 8/10

**Benefits**:
- Easier to navigate and understand
- Better separation of concerns
- Easier testing

**Risks**:
- Breaking existing imports
- Requires thorough testing

**Files Affected**:
- `coffee_maker/orchestrator/parallel_execution_coordinator.py`

---

### 49. 🥈 Break down complex functions in process_manager.py (MEDIUM Priority)

**Issue**: Functions up to 57 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/process_manager.py`

---

### 50. 🥈 Break down complex functions in auto_gemini_styleguide.py (MEDIUM Priority)

**Issue**: Functions up to 118 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/auto_gemini_styleguide.py`

---

### 51. 🥈 Break down complex functions in git_integration.py (MEDIUM Priority)

**Issue**: Functions up to 101 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/code_reviewer/git_integration.py`

---

### 52. 🥈 Break down complex functions in report_generator.py (MEDIUM Priority)

**Issue**: Functions up to 269 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/code_reviewer/report_generator.py`

---

### 53. 🥈 Break down complex functions in security_auditor.py (MEDIUM Priority)

**Issue**: Functions up to 52 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/code_reviewer/perspectives/security_auditor.py`

---

### 54. 🥈 Break down complex functions in architect_critic.py (MEDIUM Priority)

**Issue**: Functions up to 60 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/code_reviewer/perspectives/architect_critic.py`

---

### 55. 🥈 Break down complex functions in performance_analyst.py (MEDIUM Priority)

**Issue**: Functions up to 52 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/code_reviewer/perspectives/performance_analyst.py`

---

### 56. 🥈 Break down complex functions in scheduled_llm.py (MEDIUM Priority)

**Issue**: Functions up to 91 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/scheduled_llm.py`

---

### 57. 🥈 Break down complex functions in cost_calculator.py (MEDIUM Priority)

**Issue**: Functions up to 84 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/cost_calculator.py`

---

### 58. 🥈 Break down complex functions in llm_tools.py (MEDIUM Priority)

**Issue**: Functions up to 126 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/llm_tools.py`

---

### 59. 🥈 Break down complex functions in skill_tracking.py (MEDIUM Priority)

**Issue**: Functions up to 92 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/skill_tracking.py`

---

### 60. 🥈 Break down complex functions in tools.py (MEDIUM Priority)

**Issue**: Functions up to 95 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/tools.py`

---

### 61. 🥈 Break down complex functions in llm.py (MEDIUM Priority)

**Issue**: Functions up to 80 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/llm.py`

---

### 62. 🥈 Break down complex functions in retry.py (MEDIUM Priority)

**Issue**: Functions up to 118 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/retry.py`

---

### 63. 🥈 Break down complex functions in response_parser.py (MEDIUM Priority)

**Issue**: Functions up to 61 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/response_parser.py`

---

### 64. 🥈 Break down complex functions in auto_picker_llm_refactored.py (MEDIUM Priority)

**Issue**: Functions up to 146 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/auto_picker_llm_refactored.py`

---

### 65. 🥈 Break down complex functions in llm_config.py (MEDIUM Priority)

**Issue**: Functions up to 75 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/llm_config.py`

---

### 66. 🥈 Break down complex functions in metrics.py (MEDIUM Priority)

**Issue**: Functions up to 60 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/strategies/metrics.py`

---

### 67. 🥈 Break down complex functions in scheduling.py (MEDIUM Priority)

**Issue**: Functions up to 67 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/strategies/scheduling.py`

---

### 68. 🥈 Break down complex functions in exporter.py (MEDIUM Priority)

**Issue**: Functions up to 89 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/analytics/exporter.py`

---

### 69. 🥈 Break down complex functions in analyzer.py (MEDIUM Priority)

**Issue**: Functions up to 91 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/analytics/analyzer.py`

---

### 70. 🥈 Break down complex functions in analyzer_sqlite.py (MEDIUM Priority)

**Issue**: Functions up to 61 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/analytics/analyzer_sqlite.py`

---

### 71. 🥈 Break down complex functions in exporter_sqlite.py (MEDIUM Priority)

**Issue**: Functions up to 65 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/langfuse_observe/analytics/exporter_sqlite.py`

---

### 72. 🥈 Break down complex functions in setup_isolated_venv.py (MEDIUM Priority)

**Issue**: Functions up to 115 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/setup_isolated_venv.py`

---

### 73. 🥈 Break down complex functions in time.py (MEDIUM Priority)

**Issue**: Functions up to 52 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/time.py`

---

### 74. 🥈 Break down complex functions in metrics_integration.py (MEDIUM Priority)

**Issue**: Functions up to 103 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/metrics_integration.py`

---

### 75. 🥈 Break down complex functions in task_estimator.py (MEDIUM Priority)

**Issue**: Functions up to 143 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/task_estimator.py`

---

### 76. 🥈 Break down complex functions in dependency_checker.py (MEDIUM Priority)

**Issue**: Functions up to 82 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/dependency_checker.py`

---

### 77. 🥈 Break down complex functions in dependency_analyzer.py (MEDIUM Priority)

**Issue**: Functions up to 214 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/dependency_analyzer.py`

---

### 78. 🥈 Break down complex functions in dependency_impact_assessor.py (MEDIUM Priority)

**Issue**: Functions up to 66 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/dependency_impact_assessor.py`

---

### 79. 🥈 Break down complex functions in dependency_security_scanner.py (MEDIUM Priority)

**Issue**: Functions up to 67 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/dependency_security_scanner.py`

---

### 80. 🥈 Break down complex functions in dependency_version_analyzer.py (MEDIUM Priority)

**Issue**: Functions up to 75 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/dependency_version_analyzer.py`

---

### 81. 🥈 Break down complex functions in text_to_speech.py (MEDIUM Priority)

**Issue**: Functions up to 67 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/text_to_speech.py`

---

### 82. 🥈 Break down complex functions in spec_cache.py (MEDIUM Priority)

**Issue**: Functions up to 58 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/spec_cache.py`

---

### 83. 🥈 Break down complex functions in dependency_license_checker.py (MEDIUM Priority)

**Issue**: Functions up to 82 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/dependency_license_checker.py`

---

### 84. 🥈 Break down complex functions in spec_handler.py (MEDIUM Priority)

**Issue**: Functions up to 150 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/spec_handler.py`

---

### 85. 🥈 Break down complex functions in github.py (MEDIUM Priority)

**Issue**: Functions up to 117 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/github.py`

---

### 86. 🥈 Break down complex functions in dependency_conflict_analyzer.py (MEDIUM Priority)

**Issue**: Functions up to 74 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/dependency_conflict_analyzer.py`

---

### 87. 🥈 Break down complex functions in query_engine.py (MEDIUM Priority)

**Issue**: Functions up to 57 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/code_index/query_engine.py`

---

### 88. 🥈 Break down complex functions in indexer.py (MEDIUM Priority)

**Issue**: Functions up to 59 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/utils/code_index/indexer.py`

---

### 89. 🥈 Break down complex functions in spec_diff.py (MEDIUM Priority)

**Issue**: Functions up to 93 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/spec_diff.py`

---

### 90. 🥈 Break down complex functions in roadmap_editor.py (MEDIUM Priority)

**Issue**: Functions up to 95 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/roadmap_editor.py`

---

### 91. 🥈 Break down complex functions in ai_service.py (MEDIUM Priority)

**Issue**: Functions up to 180 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/ai_service.py`

---

### 92. 🥈 Break down complex functions in roadmap_cli.py (MEDIUM Priority)

**Issue**: Functions up to 120 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/roadmap_cli.py`

---

### 93. 🥈 Break down complex functions in console_ui.py (MEDIUM Priority)

**Issue**: Functions up to 55 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/console_ui.py`

---

### 94. 🥈 Break down complex functions in spec_review.py (MEDIUM Priority)

**Issue**: Functions up to 103 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/spec_review.py`

---

### 95. 🥈 Break down complex functions in assistant_manager.py (MEDIUM Priority)

**Issue**: Functions up to 55 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/assistant_manager.py`

---

### 96. 🥈 Break down complex functions in daily_report_generator.py (MEDIUM Priority)

**Issue**: Functions up to 96 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/daily_report_generator.py`

---

### 97. 🥈 Break down complex functions in document_updater.py (MEDIUM Priority)

**Issue**: Functions up to 104 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/document_updater.py`

---

### 98. 🥈 Break down complex functions in user_listener.py (MEDIUM Priority)

**Issue**: Functions up to 121 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/user_listener.py`

---

### 99. 🥈 Break down complex functions in chat_interface.py (MEDIUM Priority)

**Issue**: Functions up to 127 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/chat_interface.py`

---

### 100. 🥈 Break down complex functions in assistant_bridge.py (MEDIUM Priority)

**Issue**: Functions up to 57 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/assistant_bridge.py`

---

### 101. 🥈 Break down complex functions in spec_workflow.py (MEDIUM Priority)

**Issue**: Functions up to 108 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/spec_workflow.py`

---

### 102. 🥈 Break down complex functions in developer_status_display.py (MEDIUM Priority)

**Issue**: Functions up to 112 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/developer_status_display.py`

---

### 103. 🥈 Break down complex functions in metadata_extractor.py (MEDIUM Priority)

**Issue**: Functions up to 66 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/metadata_extractor.py`

---

### 104. 🥈 Break down complex functions in agent_router.py (MEDIUM Priority)

**Issue**: Functions up to 74 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/agent_router.py`

---

### 105. 🥈 Break down complex functions in user_story_detector.py (MEDIUM Priority)

**Issue**: Functions up to 117 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/user_story_detector.py`

---

### 106. 🥈 Break down complex functions in bug_tracker.py (MEDIUM Priority)

**Issue**: Functions up to 87 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/bug_tracker.py`

---

### 107. 🥈 Break down complex functions in notifications.py (MEDIUM Priority)

**Issue**: Functions up to 101 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/notifications.py`

---

### 108. 🥈 Break down complex functions in assistant_tools.py (MEDIUM Priority)

**Issue**: Functions up to 158 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/assistant_tools.py`

---

### 109. 🥈 Break down complex functions in request_classifier.py (MEDIUM Priority)

**Issue**: Functions up to 118 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/request_classifier.py`

---

### 110. 🥈 Break down complex functions in architect_cli.py (MEDIUM Priority)

**Issue**: Functions up to 142 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/architect_cli.py`

---

### 111. 🥈 Break down complex functions in spec_metrics.py (MEDIUM Priority)

**Issue**: Functions up to 107 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/spec_metrics.py`

---

### 112. 🥈 Break down complex functions in preview_generator.py (MEDIUM Priority)

**Issue**: Functions up to 73 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/preview_generator.py`

---

### 113. 🥈 Break down complex functions in analyze_roadmap.py (MEDIUM Priority)

**Issue**: Functions up to 68 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/commands/analyze_roadmap.py`

---

### 114. 🥈 Break down complex functions in roadmap.py (MEDIUM Priority)

**Issue**: Functions up to 56 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/commands/roadmap.py`

---

### 115. 🥈 Break down complex functions in add_priority.py (MEDIUM Priority)

**Issue**: Functions up to 59 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/commands/add_priority.py`

---

### 116. 🥈 Break down complex functions in utility.py (MEDIUM Priority)

**Issue**: Functions up to 126 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/commands/utility.py`

---

### 117. 🥈 Break down complex functions in team.py (MEDIUM Priority)

**Issue**: Functions up to 101 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/commands/team.py`

---

### 118. 🥈 Break down complex functions in notifications.py (MEDIUM Priority)

**Issue**: Functions up to 80 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/commands/notifications.py`

---

### 119. 🥈 Break down complex functions in status.py (MEDIUM Priority)

**Issue**: Functions up to 165 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/cli/commands/status.py`

---

### 120. 🥈 Break down complex functions in skill_invoker.py (MEDIUM Priority)

**Issue**: Functions up to 57 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/skill_invoker.py`

---

### 121. 🥈 Break down complex functions in puppeteer_client.py (MEDIUM Priority)

**Issue**: Functions up to 96 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/puppeteer_client.py`

---

### 122. 🥈 Break down complex functions in cached_roadmap_parser.py (MEDIUM Priority)

**Issue**: Functions up to 65 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/cached_roadmap_parser.py`

---

### 123. 🥈 Break down complex functions in claude_api_interface.py (MEDIUM Priority)

**Issue**: Functions up to 68 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/claude_api_interface.py`

---

### 124. 🥈 Break down complex functions in spec_watcher.py (MEDIUM Priority)

**Issue**: Functions up to 51 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/spec_watcher.py`

---

### 125. 🥈 Break down complex functions in daemon_implementation.py (MEDIUM Priority)

**Issue**: Functions up to 252 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/daemon_implementation.py`

---

### 126. 🥈 Break down complex functions in claude_cli_interface.py (MEDIUM Priority)

**Issue**: Functions up to 118 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/claude_cli_interface.py`

---

### 127. 🥈 Break down complex functions in spec_template_manager.py (MEDIUM Priority)

**Issue**: Functions up to 83 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/spec_template_manager.py`

---

### 128. 🥈 Break down complex functions in code_reviewer.py (MEDIUM Priority)

**Issue**: Functions up to 176 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/code_reviewer.py`

---

### 129. 🥈 Break down complex functions in roadmap_parser.py (MEDIUM Priority)

**Issue**: Functions up to 86 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/roadmap_parser.py`

---

### 130. 🥈 Break down complex functions in task_metrics.py (MEDIUM Priority)

**Issue**: Functions up to 77 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/task_metrics.py`

---

### 131. 🥈 Break down complex functions in story_metrics.py (MEDIUM Priority)

**Issue**: Functions up to 100 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/story_metrics.py`

---

### 132. 🥈 Break down complex functions in architect_report_generator.py (MEDIUM Priority)

**Issue**: Functions up to 74 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/architect_report_generator.py`

---

### 133. 🥈 Break down complex functions in daemon_spec_manager.py (MEDIUM Priority)

**Issue**: Functions up to 91 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/daemon_spec_manager.py`

---

### 134. 🥈 Break down complex functions in spec_generator.py (MEDIUM Priority)

**Issue**: Functions up to 144 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/spec_generator.py`

---

### 135. 🥈 Break down complex functions in message_queue.py (MEDIUM Priority)

**Issue**: Functions up to 90 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/message_queue.py`

---

### 136. 🥈 Break down complex functions in startup_skill_mixin.py (MEDIUM Priority)

**Issue**: Functions up to 61 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/startup_skill_mixin.py`

---

### 137. 🥈 Break down complex functions in orchestrator.py (MEDIUM Priority)

**Issue**: Functions up to 73 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/orchestrator.py`

---

### 138. 🥈 Break down complex functions in standup_generator.py (MEDIUM Priority)

**Issue**: Functions up to 53 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/standup_generator.py`

---

### 139. 🥈 Break down complex functions in daemon_status.py (MEDIUM Priority)

**Issue**: Functions up to 90 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/daemon_status.py`

---

### 140. 🥈 Break down complex functions in activity_db.py (MEDIUM Priority)

**Issue**: Functions up to 80 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/activity_db.py`

---

### 141. 🥈 Break down complex functions in daemon_cli.py (MEDIUM Priority)

**Issue**: Functions up to 208 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/daemon_cli.py`

---

### 142. 🥈 Break down complex functions in skill_loader.py (MEDIUM Priority)

**Issue**: Functions up to 65 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/skill_loader.py`

---

### 143. 🥈 Break down complex functions in daemon_git_ops.py (MEDIUM Priority)

**Issue**: Functions up to 54 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/daemon_git_ops.py`

---

### 144. 🥈 Break down complex functions in daemon.py (MEDIUM Priority)

**Issue**: Functions up to 224 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/daemon.py`

---

### 145. 🥈 Break down complex functions in startup_skill_executor.py (MEDIUM Priority)

**Issue**: Functions up to 64 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/startup_skill_executor.py`

---

### 146. 🥈 Break down complex functions in code_developer_agent.py (MEDIUM Priority)

**Issue**: Functions up to 99 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/agents/code_developer_agent.py`

---

### 147. 🥈 Break down complex functions in base_agent.py (MEDIUM Priority)

**Issue**: Functions up to 71 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/agents/base_agent.py`

---

### 148. 🥈 Break down complex functions in architect_agent.py (MEDIUM Priority)

**Issue**: Functions up to 126 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/agents/architect_agent.py`

---

### 149. 🥈 Break down complex functions in architect_skills_mixin.py (MEDIUM Priority)

**Issue**: Functions up to 90 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/agents/architect_skills_mixin.py`

---

### 150. 🥈 Break down complex functions in code_developer_commit_review_mixin.py (MEDIUM Priority)

**Issue**: Functions up to 77 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/agents/code_developer_commit_review_mixin.py`

---

### 151. 🥈 Break down complex functions in trace_manager.py (MEDIUM Priority)

**Issue**: Functions up to 75 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/ace/trace_manager.py`

---

### 152. 🥈 Break down complex functions in playbook_loader.py (MEDIUM Priority)

**Issue**: Functions up to 75 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/ace/playbook_loader.py`

---

### 153. 🥈 Break down complex functions in api.py (MEDIUM Priority)

**Issue**: Functions up to 113 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/ace/api.py`

---

### 154. 🥈 Break down complex functions in generator.py (MEDIUM Priority)

**Issue**: Functions up to 96 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/ace/generator.py`

---

### 155. 🥈 Break down complex functions in insights.py (MEDIUM Priority)

**Issue**: Functions up to 124 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/autonomous/ace/insights.py`

---

### 156. 🥈 Break down complex functions in analysis_loader.py (MEDIUM Priority)

**Issue**: Functions up to 57 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/analysis_loader.py`

---

### 157. 🥈 Break down complex functions in skill_loader.py (MEDIUM Priority)

**Issue**: Functions up to 60 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/skill_loader.py`

---

### 158. 🥈 Break down complex functions in code_forensics.py (MEDIUM Priority)

**Issue**: Functions up to 77 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/code_analysis/code_forensics.py`

---

### 159. 🥈 Break down complex functions in functional_search.py (MEDIUM Priority)

**Issue**: Functions up to 68 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/code_analysis/functional_search.py`

---

### 160. 🥈 Break down complex functions in security_audit.py (MEDIUM Priority)

**Issue**: Functions up to 70 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/code_analysis/security_audit.py`

---

### 161. 🥈 Break down complex functions in code_explainer.py (MEDIUM Priority)

**Issue**: Functions up to 93 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/code_analysis/code_explainer.py`

---

### 162. 🥈 Break down complex functions in test_failure_analyzer.py (MEDIUM Priority)

**Issue**: Functions up to 99 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/code_analysis/test_failure_analyzer.py`

---

### 163. 🥈 Break down complex functions in dependency_tracer.py (MEDIUM Priority)

**Issue**: Functions up to 84 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/code_analysis/dependency_tracer.py`

---

### 164. 🥈 Break down complex functions in context_budget_optimizer.py (MEDIUM Priority)

**Issue**: Functions up to 84 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/optimization/context_budget_optimizer.py`

---

### 165. 🥈 Break down complex functions in proactive_refactoring_analysis.py (MEDIUM Priority)

**Issue**: Functions up to 110 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/refactoring_analysis/proactive_refactoring_analysis.py`

---

### 166. 🥈 Break down complex functions in architecture_reuse_checker.py (MEDIUM Priority)

**Issue**: Functions up to 78 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/architecture/architecture_reuse_checker.py`

---

### 167. 🥈 Break down complex functions in proactive_refactoring_analyzer.py (MEDIUM Priority)

**Issue**: Functions up to 107 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/architecture/proactive_refactoring_analyzer.py`

---

### 168. 🥈 Break down complex functions in functionality_tester.py (MEDIUM Priority)

**Issue**: Functions up to 56 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/dod_verification/functionality_tester.py`

---

### 169. 🥈 Break down complex functions in report_generator.py (MEDIUM Priority)

**Issue**: Functions up to 149 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/dod_verification/report_generator.py`

---

### 170. 🥈 Break down complex functions in pr_creator.py (MEDIUM Priority)

**Issue**: Functions up to 133 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/git_workflow/pr_creator.py`

---

### 171. 🥈 Break down complex functions in git_workflow_automation.py (MEDIUM Priority)

**Issue**: Functions up to 119 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/git_workflow/git_workflow_automation.py`

---

### 172. 🥈 Break down complex functions in commit_generator.py (MEDIUM Priority)

**Issue**: Functions up to 62 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/skills/git_workflow/commit_generator.py`

---

### 173. 🥈 Break down complex functions in provider_factory.py (MEDIUM Priority)

**Issue**: Functions up to 62 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/ai_providers/provider_factory.py`

---

### 174. 🥈 Break down complex functions in fallback_strategy.py (MEDIUM Priority)

**Issue**: Functions up to 108 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/ai_providers/fallback_strategy.py`

---

### 175. 🥈 Break down complex functions in openai_provider.py (MEDIUM Priority)

**Issue**: Functions up to 68 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/ai_providers/providers/openai_provider.py`

---

### 176. 🥈 Break down complex functions in claude_provider.py (MEDIUM Priority)

**Issue**: Functions up to 58 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/ai_providers/providers/claude_provider.py`

---

### 177. 🥈 Break down complex functions in gemini_provider.py (MEDIUM Priority)

**Issue**: Functions up to 69 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/ai_providers/providers/gemini_provider.py`

---

### 178. 🥈 Break down complex functions in agents.py (MEDIUM Priority)

**Issue**: Functions up to 127 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/code_formatter/agents.py`

---

### 179. 🥈 Break down complex functions in continuous_work_loop.py (MEDIUM Priority)

**Issue**: Functions up to 72 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/orchestrator/continuous_work_loop.py`

---

### 180. 🥈 Break down complex functions in parallel_execution_coordinator.py (MEDIUM Priority)

**Issue**: Functions up to 76 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/orchestrator/parallel_execution_coordinator.py`

---

### 181. 🥈 Break down complex functions in slack_notifier.py (MEDIUM Priority)

**Issue**: Functions up to 77 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/reports/slack_notifier.py`

---

### 182. 🥈 Break down complex functions in status_tracking_updater.py (MEDIUM Priority)

**Issue**: Functions up to 87 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/reports/status_tracking_updater.py`

---

### 183. 🥈 Break down complex functions in status_report_generator.py (MEDIUM Priority)

**Issue**: Functions up to 160 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/reports/status_report_generator.py`

---

### 184. 🥈 Break down complex functions in update_scheduler.py (MEDIUM Priority)

**Issue**: Functions up to 54 LOC

**Proposed Refactoring**: Extract helper functions, simplify logic

**Effort**: 3.0 hours
**Time Saved (Future)**: 5.0 hours
**ROI**: 1.7x
**Priority**: 6/10

**Benefits**:
- Better readability
- Easier testing
- Reusable helpers

**Risks**:
- May increase call stack depth

**Files Affected**:
- `coffee_maker/reports/update_scheduler.py`

---

### 185. 🥈 Address 155 technical debt items (MEDIUM Priority)

**Issue**: 155 TODO/FIXME/HACK comments in codebase

**Proposed Refactoring**: Create ROADMAP priorities for top items

**Effort**: 77.5 hours
**Time Saved (Future)**: 155.0 hours
**ROI**: 2.0x
**Priority**: 5/10

**Benefits**:
- Clean up known issues
- Prevent future bugs
- Improve code quality

**Risks**:
- Some TODOs may be outdated

**Files Affected**:
- `coffee_maker/utils/metrics_integration.py`
- `coffee_maker/utils/dependency_analyzer.py`
- `coffee_maker/utils/spec_handler.py`
- `coffee_maker/cli/roadmap_editor.py`
- `coffee_maker/cli/spec_review.py`

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Total Files | 263 |
| Total Loc | 79426 |
| Avg Loc Per File | 302.0 |
| Max Loc File | coffee_maker/cli/chat_interface.py |
| Total Functions | 1910 |
| Total Classes | 387 |
| Avg Complexity | 19.8 |
| Max Complexity File | coffee_maker/cli/chat_interface.py |
| Total Todos | 91 |
| Total Fixmes | 22 |
| Total Hacks | 42 |
| Files Over 500 Loc | 42 |
| Files Over 1000 Loc | 3 |

---

## Next Steps

1. **project_manager**: Review this report
2. **project_manager**: Add top priorities to ROADMAP
3. **architect**: Create technical specs for approved refactorings
4. **code_developer**: Implement refactorings in priority order
5. **architect**: Run this skill again in 1 week (track progress)

---

**Generated by**: proactive-refactoring-analysis skill
**Version**: 1.0.0


## Trend Analysis (Week-over-Week)

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Health Score | 30.1 | 30.1 | +0.0 ➡️ |
| Total LOC | 79,426 | 79,426 | +0 |
| Opportunities | 185 | 185 | +0 ➡️ |
| Avg Complexity | 19.8 | 19.8 | +0.0 |
