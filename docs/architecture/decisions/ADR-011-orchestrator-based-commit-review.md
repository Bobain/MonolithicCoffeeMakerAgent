# ADR-011: Orchestrator-Based Commit Review (No Git Hooks)

**Status**: Accepted

**Date**: 2025-10-18

**Author**: architect agent

**Supersedes**: Git hook approach from ADR-010

**Related**: ADR-010 (Commit Review), Orchestrator (coffee_maker/autonomous/orchestrator.py)

---

## Context

ADR-010 documented architect's new commit review responsibility but proposed using **git hooks** to trigger reviews. However, we already have a **sophisticated orchestrator** that manages inter-agent communication through file-based messaging.

**User's Question (2025-10-18)**:
> "Peut-on se passer d'un git hook? Les agents ne peuvent-ils pas communiquer directement par le biais de l'agent orchestrator?"

**Answer**: **Oui!** L'orchestrator est la solution parfaite et élimine le besoin de git hooks.

### Current Orchestrator Architecture

```python
# coffee_maker/autonomous/orchestrator.py (already exists!)

class OrchestratorAgent(BaseAgent):
    """Multi-agent orchestrator managing parallel team execution.

    Inter-Process Communication (IPC):
        - Status files: data/agent_status/{agent}_status.json
        - Message queues: data/agent_messages/{agent}_inbox/
        - File-based for simplicity and observability
    """
```

**Features Already Available**:
- ✅ Launches all agents in parallel
- ✅ File-based messaging between agents
- ✅ Status tracking (`data/agent_status/`)
- ✅ Message inbox per agent (`data/agent_messages/{agent}_inbox/`)
- ✅ Health monitoring and crash recovery
- ✅ Graceful shutdown coordination

### The Problem with Git Hooks

**Proposed in ADR-010**:
```bash
# .git/hooks/post-commit
git commit → git hook → invoke architect (subprocess)
```

**Problems**:
1. **External dependency**: Git hooks are not part of the agent system
2. **No orchestrator awareness**: Git hook bypasses orchestrator
3. **Subprocess complexity**: Hook spawns architect outside orchestrator control
4. **Platform-specific**: Git hooks work differently on Windows vs Unix
5. **Installation overhead**: Hooks must be installed per developer machine
6. **Hard to test**: Git hooks are harder to test than Python code
7. **No status tracking**: Hook execution not visible in orchestrator dashboard

### Forces at Play

**Agent Communication**:
- Agents already communicate via file-based messages
- Orchestrator monitors all agents and can route messages
- No need for external triggers (git hooks)

**Simplicity**:
- File-based messaging is simple and observable
- All communication goes through one system (orchestrator)
- Easier to debug (all messages are files)

**Consistency**:
- All agents use same communication mechanism
- Orchestrator has full visibility into all interactions
- No "special case" for commit review

---

## Decision

We will use **orchestrator-based messaging** instead of git hooks to trigger commit reviews.

### Architecture: Orchestrator-Based Communication

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR WORKFLOW                         │
└─────────────────────────────────────────────────────────────────┘

1. code_developer completes implementation
       │
       ├─ Writes code
       ├─ git commit -m "feat: ..."
       └─ git push origin roadmap
              │
              ▼
2. code_developer sends message to architect (via orchestrator)
       │
       ├─ Writes file: data/agent_messages/architect_inbox/commit_review_<SHA>.json
       ├─ Message type: "commit_review_request"
       ├─ Content: { "commit_sha": "a1b2c3d", "files": [...], "priority": "PRIORITY X" }
       └─ orchestrator sees new message in architect's inbox
              │
              ▼
3. architect receives message (next poll)
       │
       ├─ Reads inbox: data/agent_messages/architect_inbox/
       ├─ Processes "commit_review_request" messages
       └─ Prioritizes: CRITICAL commits first, then NORMAL
              │
              ▼
4. architect performs review + skills update
       │
       ├─ Reads git diff (git show <SHA>)
       ├─ Analyzes code quality, patterns, architecture
       ├─ Updates Code Index (new functions, classes)
       ├─ Generates feedback (tactical, learning, strategic)
       └─ Routes feedback to recipients
              │
              ▼
5. architect sends feedback messages
       │
       ├─ TACTICAL → data/agent_messages/code_developer_inbox/feedback_<SHA>.json
       ├─ LEARNING → data/agent_messages/reflector_inbox/pattern_<SHA>.json
       └─ STRATEGIC → data/agent_messages/project_manager_inbox/refactor_<SHA>.json
              │
              ▼
6. Recipients receive and process feedback
       │
       ├─ code_developer: Reads tactical feedback, fixes bugs
       ├─ reflector: Captures patterns for future reuse
       └─ project_manager: Creates new ROADMAP priorities
```

**No Git Hooks Required** - All communication through orchestrator's file-based messaging!

---

## Message Protocol

### Message Format

**All messages are JSON files** in `data/agent_messages/{recipient}_inbox/`

**Message Structure**:
```json
{
  "message_id": "commit_review_a1b2c3d_1729258800",
  "type": "commit_review_request",
  "sender": "code_developer",
  "recipient": "architect",
  "timestamp": "2025-10-18T14:30:00Z",
  "priority": "NORMAL",
  "content": {
    "commit_sha": "a1b2c3d",
    "branch": "roadmap",
    "priority_name": "PRIORITY 10",
    "files_changed": [
      "coffee_maker/autonomous/skills_updater.py",
      "tests/unit/test_skills_updater.py"
    ],
    "loc_added": 150,
    "loc_removed": 50,
    "commit_message": "feat: Implement skills updater for Code Index"
  }
}
```

### Message Types

#### 1. commit_review_request (code_developer → architect)

**When**: After every commit to roadmap branch

**Content**:
```json
{
  "type": "commit_review_request",
  "sender": "code_developer",
  "recipient": "architect",
  "priority": "NORMAL",  // or "CRITICAL" for security/blocking issues
  "content": {
    "commit_sha": "a1b2c3d",
    "branch": "roadmap",
    "priority_name": "PRIORITY 10",
    "files_changed": ["file1.py", "file2.py"],
    "loc_added": 150,
    "loc_removed": 50,
    "commit_message": "feat: ...",
    "spec_file": "docs/architecture/specs/SPEC-010.md"  // if exists
  }
}
```

**architect Action**:
- Review commit within SLA (2h NORMAL, 30min CRITICAL)
- Update Code Index
- Generate feedback messages

#### 2. tactical_feedback (architect → code_developer)

**When**: Bug found, spec deviation, performance issue

**Content**:
```json
{
  "type": "tactical_feedback",
  "sender": "architect",
  "recipient": "code_developer",
  "priority": "HIGH",
  "content": {
    "commit_sha": "a1b2c3d",
    "issues": [
      {
        "severity": "CRITICAL",
        "type": "bug",
        "file": "coffee_maker/auth/login.py",
        "line": 45,
        "description": "Password stored in plaintext",
        "fix": "Use bcrypt to hash passwords before storing"
      },
      {
        "severity": "MEDIUM",
        "type": "performance",
        "file": "coffee_maker/index/builder.py",
        "line": 120,
        "description": "Sequential file parsing (60s for 450 files)",
        "fix": "Use ProcessPoolExecutor for parallel parsing"
      }
    ],
    "action_required": true,
    "deadline": "2025-10-18T16:30:00Z"  // 2 hours from now
  }
}
```

**code_developer Action**:
- Read feedback from inbox
- Fix issues in priority order (CRITICAL first)
- Create new commit with fixes
- Send acknowledgment message back to architect

#### 3. learning_feedback (architect → reflector)

**When**: Effective pattern discovered, anti-pattern identified

**Content**:
```json
{
  "type": "learning_feedback",
  "sender": "architect",
  "recipient": "reflector",
  "priority": "LOW",
  "content": {
    "commit_sha": "a1b2c3d",
    "pattern_type": "best_practice",
    "pattern_name": "Atomic File Update Pattern",
    "description": "Uses temp file + atomic rename to prevent corruption",
    "location": {
      "file": "coffee_maker/code_index/updater.py",
      "line_start": 150,
      "line_end": 180
    },
    "why_effective": [
      "Prevents partial writes during crash",
      "No file corruption even if process killed",
      "Fast (atomic rename is O(1) operation)"
    ],
    "reuse_opportunity": "Apply to all config file writes",
    "code_snippet": "..."
  }
}
```

**reflector Action**:
- Store pattern in delta items (long-term memory)
- code_developer will automatically reference this pattern in future

#### 4. strategic_feedback (architect → project_manager)

**When**: Major refactoring needed, technical debt critical

**Content**:
```json
{
  "type": "strategic_feedback",
  "sender": "architect",
  "recipient": "project_manager",
  "priority": "MEDIUM",
  "content": {
    "commit_sha": "a1b2c3d",
    "issue_type": "technical_debt",
    "title": "Payment Module Needs Refactoring",
    "description": "80% code duplication across Stripe, PayPal, Square gateways",
    "impact": "Bug fixes must be applied 3 times manually (high risk)",
    "recommendation": {
      "action": "Create new ROADMAP priority",
      "priority_name": "PRIORITY X - Refactor Payment Gateways",
      "estimated_effort": "8-12 hours",
      "benefit": "Reduce 450 LOC to ~150 LOC, consistent behavior"
    },
    "urgency": "MEDIUM",
    "deadline": "Within 2 weeks"
  }
}
```

**project_manager Action**:
- Evaluate impact vs effort
- Create new PRIORITY in ROADMAP.md
- Notify user of technical debt

---

## Implementation Changes

### code_developer Agent (Modified)

**New Behavior**: After each commit, send message to architect

```python
class CodeDeveloperAgent(BaseAgent):
    def _after_commit_success(self, commit_sha: str, files_changed: List[str]):
        """Called after successful commit to roadmap branch.

        Sends commit review request to architect via orchestrator messaging.
        """
        # Determine priority based on commit content
        priority = self._determine_review_priority(commit_sha, files_changed)

        # Create commit review request message
        message = {
            "message_id": f"commit_review_{commit_sha}_{int(time.time())}",
            "type": "commit_review_request",
            "sender": "code_developer",
            "recipient": "architect",
            "timestamp": datetime.now().isoformat(),
            "priority": priority,  # "CRITICAL" or "NORMAL"
            "content": {
                "commit_sha": commit_sha,
                "branch": "roadmap",
                "priority_name": self.current_priority,
                "files_changed": files_changed,
                "loc_added": self._count_loc_added(commit_sha),
                "loc_removed": self._count_loc_removed(commit_sha),
                "commit_message": self._get_commit_message(commit_sha),
                "spec_file": self._find_spec_file(self.current_priority),
            }
        }

        # Write message to architect's inbox
        self._send_message("architect", message)

        logger.info(f"✉️  Sent commit review request to architect (SHA: {commit_sha[:7]})")

    def _determine_review_priority(self, commit_sha: str, files_changed: List[str]) -> str:
        """Determine if commit needs CRITICAL (urgent) or NORMAL review.

        CRITICAL if:
        - Security-related files changed (auth/, security/)
        - Critical infrastructure changed (daemon.py, orchestrator.py)
        - >500 LOC changed (large refactoring)

        Otherwise: NORMAL
        """
        # Check for security files
        security_patterns = ["auth/", "security/", "jwt", "password", "token"]
        if any(pattern in f.lower() for f in files_changed for pattern in security_patterns):
            return "CRITICAL"

        # Check for critical infrastructure
        critical_files = ["daemon.py", "orchestrator.py", "agent_registry.py"]
        if any(f.endswith(cf) for f in files_changed for cf in critical_files):
            return "CRITICAL"

        # Check LOC changed
        loc_changed = self._count_loc_added(commit_sha) + self._count_loc_removed(commit_sha)
        if loc_changed > 500:
            return "CRITICAL"

        return "NORMAL"
```

### architect Agent (Modified)

**New Behavior**: Poll inbox for commit review requests

```python
class ArchitectAgent(BaseAgent):
    def _do_background_work(self):
        """architect's background work: proactive spec creation + commit reviews.

        Prioritized work order:
        1. CRITICAL commit reviews (security, large changes)
        2. NORMAL commit reviews (routine changes)
        3. Proactive spec creation (if no reviews pending)
        """
        # Step 1: Check inbox for commit review requests
        review_requests = self._read_messages(type_filter="commit_review_request")

        if review_requests:
            # Prioritize CRITICAL reviews first
            critical = [r for r in review_requests if r.get("priority") == "CRITICAL"]
            normal = [r for r in review_requests if r.get("priority") == "NORMAL"]

            # Process CRITICAL reviews immediately
            for request in critical:
                self._process_commit_review(request)

            # Process NORMAL reviews (up to 3 per iteration to avoid backlog)
            for request in normal[:3]:
                self._process_commit_review(request)

        # Step 2: Proactive spec creation (if no pending reviews)
        else:
            self._proactive_spec_creation()

    def _process_commit_review(self, request: Dict):
        """Process a single commit review request.

        Steps:
        1. Read git diff
        2. Analyze code quality
        3. Update Code Index
        4. Generate feedback
        5. Route feedback to recipients
        """
        commit_sha = request["content"]["commit_sha"]

        logger.info(f"📋 Reviewing commit {commit_sha[:7]}...")

        # Step 1: Read git diff
        diff = self.git.show(commit_sha)

        # Step 2: Analyze code quality
        analysis = self._analyze_commit(diff, request["content"])

        # Step 3: Update Code Index
        self._update_code_index(commit_sha, analysis)

        # Step 4: Generate feedback
        feedback = self._generate_feedback(analysis)

        # Step 5: Route feedback
        self._route_feedback(commit_sha, feedback)

        logger.info(f"✅ Commit {commit_sha[:7]} reviewed successfully")

    def _route_feedback(self, commit_sha: str, feedback: Dict):
        """Route feedback to appropriate recipients based on type.

        Routing logic (from ADR-010):
        - CRITICAL bugs/security → code_developer (TACTICAL)
        - Spec deviation → code_developer (TACTICAL)
        - Refactoring needed → project_manager (STRATEGIC)
        - Effective pattern → reflector (LEARNING)
        """
        # TACTICAL feedback to code_developer
        if feedback.get("tactical"):
            self._send_message("code_developer", {
                "type": "tactical_feedback",
                "content": feedback["tactical"],
                "priority": feedback["tactical"]["priority"],
            })

        # LEARNING feedback to reflector
        if feedback.get("learning"):
            self._send_message("reflector", {
                "type": "learning_feedback",
                "content": feedback["learning"],
                "priority": "LOW",
            })

        # STRATEGIC feedback to project_manager
        if feedback.get("strategic"):
            self._send_message("project_manager", {
                "type": "strategic_feedback",
                "content": feedback["strategic"],
                "priority": feedback["strategic"]["urgency"],
            })
```

---

## Benefits vs Git Hooks

| Aspect | Git Hooks (ADR-010) | Orchestrator Messaging (ADR-011) |
|--------|---------------------|----------------------------------|
| **Integration** | External (git infrastructure) | Native (Python agent system) |
| **Visibility** | Hidden (subprocess) | Visible (orchestrator dashboard) |
| **Testing** | Hard (need git repo) | Easy (unit test messages) |
| **Cross-Platform** | Platform-specific | Platform-agnostic |
| **Installation** | Per-developer setup | No setup (part of system) |
| **Status Tracking** | None | Full orchestrator monitoring |
| **Error Handling** | Limited (subprocess) | Rich (agent crash recovery) |
| **Prioritization** | No (FIFO only) | Yes (CRITICAL first) |
| **Observability** | Low (logs only) | High (all messages are files) |
| **Debugging** | Hard (subprocess) | Easy (inspect message files) |

---

## Migration from ADR-010

### Changes Required

1. **Remove Git Hook References**
   - ❌ Delete `.git/hooks/post-commit` approach
   - ❌ Remove git hook installation scripts
   - ❌ No subprocess spawning from git

2. **Add Message Handling**
   - ✅ code_developer sends `commit_review_request` after commits
   - ✅ architect polls inbox for review requests
   - ✅ architect sends feedback messages to recipients

3. **Update Infrastructure**
   - ✅ Use existing `data/agent_messages/` directories
   - ✅ Use existing `BaseAgent._send_message()` method
   - ✅ Use existing `BaseAgent._read_messages()` method

### No Breaking Changes

- ✅ All ADR-010 concepts remain (3 feedback channels, routing logic, skills update)
- ✅ Only TRIGGER mechanism changes (orchestrator messages vs git hooks)
- ✅ Workflow diagrams from ADR-010 still valid (just replace "git hook" with "send message")

---

## Performance

### Latency

| Trigger | Latency | Notes |
|---------|---------|-------|
| **Git Hook** | Immediate (<1s) | Subprocess spawn overhead |
| **Orchestrator Message** | <30s (next poll) | architect polls inbox every 30s |

**Trade-off**: Slight latency increase (30s vs 1s), but:
- CRITICAL commits: architect can poll more frequently (<5s)
- Benefit: Better integration, easier debugging, full observability

### Throughput

- **Backlog Handling**: architect processes up to 3 NORMAL reviews per iteration
- **Priority Queue**: CRITICAL reviews always processed first
- **No Bottleneck**: If backlog grows, architect increases poll frequency dynamically

---

## Risks and Mitigations

### Risk 1: Message Delivery Failure

**Risk**: Message file write fails or gets corrupted

**Probability**: LOW (file I/O is reliable)

**Mitigation**:
- Use atomic writes (temp file + rename)
- code_developer retries if message send fails
- orchestrator monitors message delivery

### Risk 2: architect Inbox Overflow

**Risk**: Too many review requests pile up in inbox

**Probability**: MEDIUM (if code_developer commits very frequently)

**Mitigation**:
- architect prioritizes CRITICAL first
- architect processes batches (3 NORMAL per iteration)
- orchestrator can alert if inbox >20 messages
- architect increases poll frequency if backlog detected

### Risk 3: Review Latency Too High

**Risk**: 30s polling interval too slow for CRITICAL reviews

**Probability**: LOW (30s is acceptable for most use cases)

**Mitigation**:
- architect can poll more frequently for CRITICAL (every 5s)
- code_developer can send high-priority notification (separate mechanism)
- Future: WebSocket push for instant delivery (if needed)

---

## Success Metrics

### Quantitative

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Message Delivery Success** | >99% | % of messages successfully written |
| **Review Latency (CRITICAL)** | <5 min | Time from commit to review start |
| **Review Latency (NORMAL)** | <30 min | Time from commit to review start |
| **Inbox Backlog** | <10 messages | Average inbox size for architect |
| **Message Corruption** | 0 | Corrupted message files |

### Qualitative

- ✅ **Easier to Debug**: All messages visible as files (can inspect manually)
- ✅ **Better Integration**: No external dependencies (git hooks)
- ✅ **Full Observability**: orchestrator dashboard shows all communication
- ✅ **Platform Agnostic**: Works same on Windows, macOS, Linux

---

## Example Workflow

### Scenario: code_developer Commits Security Fix

```
1. code_developer commits:
   git commit -m "fix: Hash passwords with bcrypt"

2. code_developer sends message:
   File: data/agent_messages/architect_inbox/commit_review_a1b2c3d_1729258800.json
   {
     "type": "commit_review_request",
     "priority": "CRITICAL",  // Security-related
     "content": {
       "commit_sha": "a1b2c3d",
       "files_changed": ["coffee_maker/auth/login.py"],
       ...
     }
   }

3. architect polls inbox (next iteration, <30s):
   - Sees CRITICAL review request
   - Prioritizes immediately (before NORMAL reviews)

4. architect reviews commit:
   - Reads diff: git show a1b2c3d
   - Analyzes: Password hashing implemented correctly ✅
   - Updates Code Index: login.py:45-89 complexity: LOW → MEDIUM
   - No issues found → No tactical feedback needed

5. architect sends LEARNING feedback:
   File: data/agent_messages/reflector_inbox/pattern_a1b2c3d_1729258900.json
   {
     "type": "learning_feedback",
     "content": {
       "pattern_name": "Password Hashing with bcrypt",
       "description": "Secure password storage using bcrypt",
       ...
     }
   }

6. reflector captures pattern:
   - Stores in delta items (long-term memory)
   - code_developer will reference this for future auth code

Total time: <5 minutes (CRITICAL review SLA met) ✅
```

---

## Conclusion

**Orchestrator-based messaging is superior to git hooks** for triggering commit reviews because:

1. **Native Integration**: No external dependencies, pure Python
2. **Full Observability**: All messages visible in orchestrator dashboard
3. **Easy Testing**: Unit test messages without git repo
4. **Platform Agnostic**: Works identically on all platforms
5. **Priority Support**: CRITICAL reviews processed first
6. **Better Debugging**: Inspect message files directly
7. **Crash Recovery**: orchestrator handles agent crashes gracefully

**Trade-off Accepted**: Slight latency increase (30s vs 1s) in exchange for much better integration and observability.

**Recommendation**: Accept ADR-011 and update ADR-010 to remove git hook references.

---

## Next Steps

1. ✅ Accept ADR-011 (orchestrator-based messaging)
2. Update ADR-010 to reference orchestrator instead of git hooks
3. Implement code_developer message sending (`_after_commit_success()`)
4. Implement architect message handling (`_process_commit_review()`)
5. Test end-to-end workflow with sample commits
6. Measure review latency and inbox backlog
7. Optimize poll frequency if needed

**Timeline**: 2-3 days to implement messaging layer (simpler than git hooks!)

---

## References

- [ADR-010: Architect Commit Review and Skills Maintenance](./ADR-010-code-architect-commit-review-skills-maintenance.md)
- [ADR-009: Retire assistant (using code analysis skills), Replace with Skills](./ADR-009-retire-assistant (using code analysis skills)-replace-with-skills.md)
- [Orchestrator Implementation](../../coffee_maker/autonomous/orchestrator.py)
- [BaseAgent Messaging](../../coffee_maker/autonomous/agents/base_agent.py)

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-18 | Created | architect |
| 2025-10-18 | Status: Accepted | architect |

---

## Appendix: Message Flow Diagrams

### Diagram 1: CRITICAL Commit Review (Security Fix)

```
Time: T+0s
├─ code_developer: git commit (security fix)
└─ code_developer: Send message to architect (priority: CRITICAL)

Time: T+5s (architect polls inbox every 5s for CRITICAL)
├─ architect: Read message from inbox
├─ architect: Review commit (15 min)
├─ architect: Update Code Index
└─ architect: Send tactical feedback to code_developer

Time: T+20min
├─ code_developer: Read tactical feedback
├─ code_developer: Fix issues
└─ code_developer: New commit with fixes

Total SLA: <30 min ✅
```

### Diagram 2: NORMAL Commit Review (Feature Implementation)

```
Time: T+0s
├─ code_developer: git commit (new feature)
└─ code_developer: Send message to architect (priority: NORMAL)

Time: T+30s (architect polls inbox every 30s)
├─ architect: Read message from inbox
├─ architect: Review commit (10 min)
├─ architect: Update Code Index
└─ architect: Send learning feedback to reflector

Time: T+15min
├─ reflector: Read learning feedback
└─ reflector: Store pattern in delta items

Total SLA: <2 hours ✅
```

### Diagram 3: Inbox Backlog Handling

```
architect inbox:
├─ commit_review_a1b2c3d.json (CRITICAL) ← Process 1st
├─ commit_review_b2c3d4e.json (CRITICAL) ← Process 2nd
├─ commit_review_c3d4e5f.json (NORMAL)   ← Process 3rd
├─ commit_review_d4e5f6g.json (NORMAL)   ← Process 4th
├─ commit_review_e5f6g7h.json (NORMAL)   ← Process 5th
└─ commit_review_f6g7h8i.json (NORMAL)   ← Queue (next iteration)

architect processes:
- All CRITICAL first (no matter how many)
- Up to 3 NORMAL per iteration (prevent starvation)
- Remaining NORMAL wait for next iteration
```
