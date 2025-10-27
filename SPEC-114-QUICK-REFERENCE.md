# SPEC-114: UI & Utility Agent Commands - Quick Reference

**Date**: 2025-10-27
**Status**: ✅ Created in database
**Type**: Monolithic specification
**Hours**: 40 hours total (16 + 14 + 10)

---

## Command Quick Reference

### Assistant Agent (11 commands) - 16 hours

| Category | Commands | Purpose |
|----------|----------|---------|
| **Demo Management** | create-demo, record-demo-session, validate-demo-output | Puppeteer-based demo recording |
| **Bug Reporting** | report-bug, track-bug-status, link-bug-to-priority | Database bug tracking |
| **Delegation** | classify-request, route-to-agent, monitor-delegation | Intelligent routing |
| **Documentation** | generate-docs, update-readme | Auto-documentation |

**Database Tables**: ui_demo_sessions, ui_bug_reports, ui_delegation_log

---

### User Listener Agent (9 commands) - 14 hours

| Category | Commands | Purpose |
|----------|----------|---------|
| **Intent Classification** | classify-intent, extract-entities, determine-agent | NLP-based intent detection |
| **Routing** | route-request, queue-for-agent, handle-fallback | Message routing |
| **Conversation** | track-conversation, update-context, manage-session | State management |

**Database Tables**: ui_conversation_context, ui_intent_classification, ui_routing_log

---

### UX Design Expert Agent (10 commands) - 10 hours

| Category | Commands | Purpose |
|----------|----------|---------|
| **Interface Design** | generate-ui-spec, create-component-spec, validate-accessibility | WCAG-compliant specs |
| **Component Libraries** | manage-component-library, generate-tailwind-config, create-design-tokens, configure-chart-theme | Design system |
| **Design Review** | review-ui-implementation, suggest-improvements, track-design-debt | Quality control |

**Database Tables**: ui_design_specs, ui_component_library, ui_design_tokens, ui_design_debt

---

## Implementation Tasks

| Task | Agent | Commands | Hours | Key Features |
|------|-------|----------|-------|--------------|
| **TASK-114-1** | assistant | 11 | 16h | Puppeteer MCP, bug tracking |
| **TASK-114-2** | user_listener | 9 | 14h | >80% intent accuracy |
| **TASK-114-3** | ux_design_expert | 10 | 10h | Tailwind, WCAG compliance |

---

## Database Schema (10 tables total)

**Assistant** (3 tables):
- `ui_demo_sessions` - Demo metadata + Puppeteer sessions
- `ui_bug_reports` - Bug tracking with severity/priority
- `ui_delegation_log` - Delegation outcomes

**User Listener** (3 tables):
- `ui_conversation_context` - Turn-by-turn conversation state
- `ui_intent_classification` - Classification results
- `ui_routing_log` - Routing decisions

**UX Design Expert** (4 tables):
- `ui_design_specs` - Versioned design specs
- `ui_component_library` - Component definitions
- `ui_design_tokens` - Design system tokens
- `ui_design_debt` - UI/UX technical debt

---

## Key Integration Points

1. **Puppeteer MCP** - Browser automation for demos
2. **Agent Message System** - Inter-agent communication
3. **Roadmap Database** - Priority linking
4. **Orchestrator Bug System** - Unified bug tracking
5. **Tailwind CSS** - Design system integration

---

## Success Criteria Checklist

### Functional
- [ ] All 30 commands executable via ClaudeAgentInvoker
- [ ] 10 database tables created
- [ ] Puppeteer MCP integration working
- [ ] Intent classification >80% accuracy
- [ ] Component library CRUD functional
- [ ] Tailwind configs valid
- [ ] Bug reports linked to roadmap
- [ ] Conversation context persisted

### Non-Functional
- [ ] Commands follow markdown template
- [ ] DomainWrapper used for DB ops
- [ ] Audit trails for all operations
- [ ] CFR-007 compliant
- [ ] Performance: <100ms classification, <500ms routing
- [ ] Complete documentation

---

## Design Decisions Summary

1. **Monolithic spec** - All commands viewable together
2. **Database-first** - No files for components/tokens
3. **LLM classification** - No separate ML model
4. **Puppeteer MCP** - Proven browser automation
5. **Versioned tokens** - Design system evolution
6. **Full context storage** - Persistence + analysis
7. **Unified bug tracking** - Link to orchestrator_bug

---

## Timeline

- **Day 1-2**: Assistant (16h)
- **Day 3-4**: User Listener (14h)
- **Day 5**: UX Design Expert (10h)
- **Day 6**: Testing + documentation

**Total: 6 days (40 hours)**

---

## File Locations

- **Spec in Database**: `data/roadmap.db` → `specs_specification` table
- **Commands**: `.claude/commands/agents/assistant/`, `user_listener/`, `ux_design_expert/`
- **Full Summary**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/SPEC-114-CREATION-SUMMARY.md`

---

## Related Specs

- **SPEC-100**: Master specification
- **SPEC-101**: Foundation infrastructure (required dependency)
- **SPEC-102-106**: Other agent commands
- **SPEC-107**: Migration & testing strategy

---

**Next Action**: Wait for code_developer to implement TASK-114-1, TASK-114-2, TASK-114-3
