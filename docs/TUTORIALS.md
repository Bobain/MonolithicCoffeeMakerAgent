# Coffee Maker Agent - Practical Tutorials

**Last Updated**: 2025-10-10
**Target Audience**: End users, developers, assistants
**Prerequisites**: [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md) completed

---

## 📚 Table of Contents

1. [Tutorial 1: Your First Feature Implementation](#tutorial-1-your-first-feature-implementation)
2. [Tutorial 2: Daily Developer Workflow](#tutorial-2-daily-developer-workflow)
3. [Tutorial 3: Daemon Monitoring & Control](#tutorial-3-daemon-monitoring--control)
4. [Tutorial 4: Bidirectional Communication with Daemon](#tutorial-4-bidirectional-communication-with-daemon)
5. [Tutorial 5: Troubleshooting Common Issues](#tutorial-5-troubleshooting-common-issues)
6. [Tutorial 6: Writing Effective User Stories](#tutorial-6-writing-effective-user-stories)
7. [Tutorial 7: Code Review Workflow](#tutorial-7-code-review-workflow)

---

## Tutorial 1: Your First Feature Implementation

**Time**: 30 minutes
**Goal**: Add a new feature to the roadmap and have the daemon implement it autonomously

### Scenario

You want to add a simple feature: a "Hello World" function that the daemon will implement for you.

### Step 1: Start Project Manager Chat

```bash
cd /path/to/MonolithicCoffeeMakerAgent
poetry shell
poetry run project-manager chat
```

**Expected Output**:
```
🤖 Welcome to Coffee Maker - AI Project Manager

📊 Daemon Status: 🔴 Daemon: Stopped

Type /help for commands or just chat naturally
```

###  Step 2: Add a User Story

In the chat, type:

```
Add a new priority: Create a hello.py file with a hello_world() function
that prints "Hello from Coffee Maker!"
```

**PM Response**:
```
✅ I'll create a new priority for this feature.

Would you like me to add:
- Unit test for the function?
- Documentation?

Estimated: ~15 minutes

Should I add this to the ROADMAP?
```

You respond:
```
Yes, add unit test. Make it the top priority.
```

**PM Response**:
```
✅ Created PRIORITY X: Hello World Function

Added to ROADMAP as TOP PRIORITY with:
- Create hello.py with hello_world() function
- Add unit test (test_hello.py)
- Function prints "Hello from Coffee Maker!"

Ready for daemon to implement!
```

### Step 3: Start the Daemon

Still in the chat, type:
```
/start
```

**Expected Output**:
```
Starting code_developer daemon...

✅ Daemon Started Successfully!

The code_developer daemon is now running in the background.

He'll start working on priorities from the roadmap and will
respond to your messages when he has time.

⏰ Response Time: May take 12+ hours (needs focus time)
```

### Step 4: Monitor Progress

Check daemon status periodically:

```
/status
```

**Expected Output** (while working):
```
🟢 Daemon Status: RUNNING

- PID: 12345
- Status: WORKING
- Current Task: PRIORITY X: Hello World Function
- Uptime: 5 minutes
- CPU: 15.2%
- Memory: 45.3 MB
```

### Step 5: Check Notifications

After a few minutes:

```
/notifications
```

**Expected Output**:
```
📋 Daemon Has Questions:

  #42: Implementation Complete
  2025-10-10 14:30:00

  I've implemented PRIORITY X:
  - Created hello.py with hello_world() function
  - Added test_hello.py with 2 tests
  - All tests passing

  Created PR: feature/priority-x-hello-world
  Ready for review!
```

### Step 6: Review and Merge

Check the pull request on GitHub, review the code, and merge if satisfied.

### Step 7: Verify in ROADMAP

```
/view
```

You should see:
```
### PRIORITY X: Hello World Function ✅ Complete
```

**Congratulations!** You've completed your first feature implementation! 🎉

---

## Tutorial 2: Daily Developer Workflow

**Time**: 10 minutes
**Goal**: Learn the routine workflow for checking progress and responding to the daemon

### Morning Routine (5 minutes)

**Step 1: Start Project Manager**
```bash
poetry run project-manager chat
```

**Step 2: Check Daemon Status**
```
/status
```

This tells you:
- Is daemon running?
- What is daemon working on?
- How long has it been running?

**Step 3: Check for Questions**
```
/notifications
```

Review any questions from the daemon (e.g., "Should I use pytest or unittest?")

**Step 4: Respond to Questions**
```
/respond 42 "Use pytest for consistency"
```

**Step 5: View Roadmap Progress**
```
/view
```

Look for:
- ✅ Complete: Features finished yesterday
- 🔄 In Progress: Current work
- 📝 Planned: Next priorities

### Midday Check-In (2 minutes)

Just check status and notifications:
```
/status
/notifications
```

### Evening Wrap-Up (3 minutes)

**Step 1: Review Pull Requests**

Check GitHub for new PRs from the daemon:
```bash
gh pr list
```

**Step 2: Test Completed Features**

Pull the branch and test:
```bash
gh pr checkout 42
pytest
# Manual testing if needed
```

**Step 3: Approve and Merge**
```bash
gh pr review 42 --approve
gh pr merge 42
```

**Step 4: Stop Daemon (optional)**
```
/stop
```

Or leave running for 24/7 autonomous development!

---

## Tutorial 3: Daemon Monitoring & Control

**Time**: 15 minutes
**Goal**: Master daemon control commands and understand daemon lifecycle

### Scenario: Managing Daemon During Development Session

### Part 1: Starting the Daemon

**Option A: From Chat (Recommended)**
```
/start
```

**Option B: From Command Line**
```bash
poetry run code-developer --auto-approve
```

### Part 2: Checking Daemon Status

**Basic Status**:
```
/status
```

Output breakdown:
```
🟢 Daemon Status: RUNNING
- PID: 12345              ← Process ID
- Status: WORKING         ← idle | working
- Current Task: US-009    ← What it's implementing
- Uptime: 2 hours         ← How long running
- CPU: 15.2%              ← CPU usage
- Memory: 45.3 MB         ← RAM usage
```

**Status Indicators**:
- 🟢 **Active**: Working on a task
- 🟡 **Idle**: Running but waiting for work
- 🔴 **Stopped**: Not running

### Part 3: Daemon Communication Patterns

**Send a Command**:
```
Ask the daemon to implement PRIORITY 5
```

The chat will detect "ask daemon" and send via notifications.

**Natural Language Examples**:
```
✅ "Ask daemon to implement authentication"
✅ "Tell code_developer to add tests for API"
✅ "Daemon, please work on PRIORITY 3"
```

### Part 4: Stopping the Daemon

**Graceful Stop (Recommended)**:
```
/stop
```

This sends SIGTERM, waits up to 10 seconds, then force-kills if needed.

**From Command Line**:
```bash
kill <PID>  # Use PID from /status
```

### Part 5: Restarting the Daemon

```
/restart
```

Equivalent to `/stop` then `/start`.

### Part 6: Troubleshooting Daemon Issues

**Daemon Won't Start**:
```
/start

# If fails:
# 1. Check API key
echo $ANTHROPIC_API_KEY

# 2. Check if already running
ps aux | grep code-developer

# 3. Check logs
tail -f dev_daemon.log
```

**Daemon Not Responding**:
```
/status  # Check if actually running

# If zombie process:
/restart
```

**Daemon Working Too Slow**:
```
# Check CPU/memory
/status

# If high resource usage, restart:
/restart
```

---

## Tutorial 4: Bidirectional Communication with Daemon

**Time**: 20 minutes
**Goal**: Learn how to communicate asynchronously with the daemon (NEW in US-009 ✨)

### Scenario: Daemon Needs Your Input

The daemon is implementing authentication and needs to ask which approach to use.

### Part 1: Daemon Asks a Question

You'll see in chat (automatically, no command needed):

```
📋 Daemon Has Questions:

  #42: Authentication Approach?
  2025-10-10 14:30:00

  I'm implementing authentication. Which approach?

  A) Email/Password (simple, 2 hours)
  B) OAuth + Email (secure, 1 day)

  Recommendation: B (more secure)

Use /notifications to view and respond
```

### Part 2: Viewing Details

```
/notifications
```

Shows full list of pending questions with IDs.

### Part 3: Responding

```
/respond 42 "Use option B with Google and GitHub OAuth"
```

**Daemon Receives**:
```
Response to Question #42:
"Use option B with Google and GitHub OAuth"

Status: Continuing implementation with OAuth
```

### Part 4: Sending Commands to Daemon

**Natural Language (Detected Automatically)**:
```
Ask daemon to add unit tests for authentication
```

**Chat Response**:
```
✅ Command Sent to Daemon (Notification #43)

Your message has been delivered to code_developer.

⏰ Response Time: He may take 12+ hours to respond.
   Like a human developer, he needs focus time and rest periods.

💡 Tip: Use /notifications to check for his response later.
```

### Part 5: Understanding Async Communication

**Key Insight**: The daemon is like a **human colleague**, not a synchronous API.

**Typical Timeline**:
```
10:00 AM: You ask daemon a question
10:05 AM: Daemon receives (via notifications database)
11:30 AM: Daemon responds (when he has time)
2:00 PM:  You check /notifications and see response
```

**This is Normal!** Just like a colleague who:
- Needs focus time for deep work
- May take hours to respond
- Works on one thing at a time
- Takes breaks

**Best Practices**:
1. ✅ Ask questions when you think of them (don't wait)
2. ✅ Check `/notifications` periodically (not constantly)
3. ✅ Provide context in questions ("I'm working on X, should I...")
4. ✅ Be patient - quality takes time

### Part 6: Advanced Communication

**Context-Rich Questions**:
```
Ask daemon: "For US-007 IDE completion, should we use LSP or custom protocol?
Context: We need VS Code + PyCharm support. Performance critical (<100ms)."
```

**Delegation**:
```
Tell daemon to implement all PRIORITY 5 deliverables and notify me when done
```

**Status Checks**:
```
What is daemon currently working on?
```

Chat will detect "daemon" + "status" keywords and show `/status` automatically.

---

## Tutorial 5: Troubleshooting Common Issues

**Time**: 15 minutes
**Goal**: Solve common problems quickly

### Issue 1: "Command not found: project-manager"

**Symptoms**:
```bash
$ project-manager chat
zsh: command not found: project-manager
```

**Solution**:
```bash
# Activate poetry environment
poetry shell

# Verify installation
which project-manager

# If still missing:
poetry install

# Try again
project-manager chat
```

---

### Issue 2: Daemon Won't Start - API Key Missing

**Symptoms**:
```
❌ Failed to Start Daemon

Troubleshooting:
- Check that you have a valid ANTHROPIC_API_KEY in .env
```

**Solution**:
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# If empty, set it:
echo "ANTHROPIC_API_KEY=your-key-here" >> .env

# Or export directly:
export ANTHROPIC_API_KEY='sk-ant-...'

# Try starting again
/start
```

---

### Issue 3: Daemon Running But Not Working

**Symptoms**:
```
/status
🟡 Daemon: Idle - Waiting for tasks
```

But you've added priorities to the ROADMAP.

**Solution**:
```bash
# 1. Check ROADMAP format
cat docs/roadmap/ROADMAP.md | grep "📝 Planned"

# Should see priorities with this status

# 2. Check if daemon is reading correct roadmap
# Look for recent commits from daemon:
git log --author="Claude" --oneline -5

# 3. Restart daemon
/restart
```

---

### Issue 4: Can't Send Commands to Daemon

**Symptoms**:
```
Ask daemon to implement X

# Response:
⚠️  Daemon Not Running

I can't send commands to the daemon because it's not running.
```

**Solution**:
```
/start

# Wait 3 seconds

# Try again:
Ask daemon to implement X
```

---

### Issue 5: Notifications Not Showing

**Symptoms**:
```
/notifications

# Empty response, but you know daemon asked questions
```

**Solution**:
```bash
# Check notifications database exists
ls -la data/notifications.db

# If missing:
mkdir -p data
poetry run project-manager chat  # Re-initializes DB

# Check again:
/notifications
```

---

### Issue 6: Daemon Implemented Wrong Thing

**Symptoms**: Daemon creates PR but it's not what you wanted.

**Solution**:

**Step 1: Don't merge the PR**
```bash
# Close the PR
gh pr close 42
```

**Step 2: Clarify in ROADMAP**
```bash
# Edit ROADMAP.md to be more specific
# Add explicit deliverables
# Add examples
```

**Step 3: Reset priority status**
```markdown
### PRIORITY X: Feature Name
**Status**: 📝 Planned  ← Change from In Progress

**Deliverables** (be very specific):
- Create file.py with exactly these functions: x(), y(), z()
- Add unit tests covering edge cases A, B, C
- Update README.md section "Getting Started"

**Examples**:
```python
def x():
    # Should do this, not that
    pass
```
```

**Step 4: Restart daemon**
```
/restart
```

---

### Issue 7: Performance Issues (Slow Response)

**Symptoms**: Chat or daemon responding slowly.

**Solution**:
```bash
# Check system resources
/status  # Look at CPU and memory

# If high:
/restart

# Check database size
du -sh data/notifications.db

# If > 100MB, clean old notifications:
poetry run python -c "
from coffee_maker.cli.notifications import NotificationDB
db = NotificationDB()
# Archive old notifications
"
```

---

## Tutorial 6: Writing Effective User Stories

**Time**: 15 minutes
**Goal**: Write user stories that lead to successful implementations

### Good vs Bad User Stories

**❌ BAD Example**:
```
User Story: Add authentication

That's it.
```

**Why Bad?**:
- Too vague (what kind of auth?)
- No acceptance criteria
- No business value stated
- Daemon doesn't know what "done" looks like

---

**✅ GOOD Example**:
```markdown
### 🎯 [US-011] User Authentication

**As a**: User of the Coffee Maker web app
**I want**: Secure authentication with email/password and OAuth
**So that**: Only authorized users can access sensitive project data

**Business Value**: ⭐⭐⭐⭐⭐ (Security critical)
**Estimated Effort**: 5-8 story points (1 week)
**Status**: 📝 Planned

**Acceptance Criteria**:
- [ ] Users can register with email/password
- [ ] Passwords hashed with bcrypt (min 12 rounds)
- [ ] Email verification required before access
- [ ] OAuth login with Google and GitHub
- [ ] Session tokens expire after 7 days
- [ ] "Remember me" option extends to 30 days
- [ ] Login attempts rate-limited (5 tries/hour)
- [ ] All auth endpoints have unit tests
- [ ] Password reset via email

**Technical Notes**:
- Use bcrypt for password hashing
- JWT tokens for sessions
- OAuth2 library for Google/GitHub
- Redis for rate limiting

**Definition of Done**:
- [ ] All acceptance criteria met
- [ ] Tests passing (>90% coverage)
- [ ] Security review completed
- [ ] Documentation updated
- [ ] User can successfully register and login
```

**Why Good?**:
- ✅ Clear acceptance criteria (9 specific items)
- ✅ Business value stated
- ✅ Technical notes for implementation guidance
- ✅ Definition of Done checklist
- ✅ Daemon knows exactly what to build

---

### Template for User Stories

```markdown
### 🎯 [US-XXX] [Title]

**As a**: [User role]
**I want**: [What you need]
**So that**: [Business value / why it matters]

**Business Value**: ⭐⭐⭐⭐⭐ (1-5 stars)
**Estimated Effort**: X story points (Y days)
**Status**: 📝 Planned

**Acceptance Criteria**:
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2
- [ ] Specific, testable criterion 3
- [ ] ... (as many as needed)

**Technical Notes** (optional):
- Preferred libraries/frameworks
- Architecture constraints
- Performance requirements
- Security considerations

**Definition of Done**:
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Documentation updated
- [ ] User validated
- [ ] Code reviewed and merged
```

---

### Tips for Writing Acceptance Criteria

**Make Them SMART**:
- **S**pecific: "Users can login" → "Users can login with email and password"
- **M**easurable: "Fast response" → "Login response time <500ms"
- **A**chievable: Don't ask for impossible things
- **R**elevant: Each criterion adds value
- **T**estable: Can be verified objectively

**Examples**:

❌ **Bad**: "Make it look nice"
✅ **Good**: "UI follows Material Design guidelines with consistent spacing (16px grid)"

❌ **Bad**: "Add error handling"
✅ **Good**: "All API endpoints return proper HTTP status codes and JSON error messages"

❌ **Bad**: "Make it fast"
✅ **Good**: "Search results load in <1 second for datasets up to 1M rows"

---

## Tutorial 7: Code Review Workflow

**Time**: 20 minutes
**Goal**: Review daemon-created pull requests effectively

### Scenario: Daemon Created a PR for Authentication Feature

### Step 1: Get Notified

In chat:
```
📋 Daemon Has Questions:

  #55: Implementation Complete - Ready for Review
  2025-10-10 16:30:00

  I've completed US-011 (User Authentication):
  - Email/password registration working
  - OAuth with Google + GitHub integrated
  - All 9 acceptance criteria met
  - 47 unit tests passing (95% coverage)

  PR: https://github.com/.../pull/123
  Branch: feature/us-011-authentication

  Ready for code review!
```

### Step 2: Checkout the Branch

```bash
gh pr checkout 123

# Or manually:
git fetch origin
git checkout feature/us-011-authentication
```

### Step 3: Review the Changes

```bash
# See what files changed
git diff main --name-only

# See the actual changes
git diff main

# Or use gh CLI:
gh pr diff 123
```

### Step 4: Run Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_auth.py -v

# Check coverage
pytest --cov=coffee_maker tests/
```

**Expected Output**:
```
=================== test session starts ====================
...
tests/test_auth.py::test_register_user PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_wrong_password FAILED
...

=================== 46 passed, 1 failed ====================
```

### Step 5: Manual Testing

```bash
# Start the app
python run_app.py

# Test registration flow:
# 1. Go to /register
# 2. Fill form with test@example.com
# 3. Check email verification works
# 4. Login with credentials
# 5. Test OAuth login
```

### Step 6: Review Checklist

Use this checklist for every PR:

```markdown
## Code Review Checklist

### Functionality
- [ ] All acceptance criteria met?
- [ ] Feature works as expected?
- [ ] Edge cases handled?
- [ ] Error messages clear and helpful?

### Code Quality
- [ ] Code follows project conventions?
- [ ] No obvious bugs or security issues?
- [ ] No code duplication?
- [ ] Functions/classes well-named?
- [ ] Comments explain "why", not "what"?

### Tests
- [ ] All tests passing?
- [ ] Coverage >80% for new code?
- [ ] Tests cover edge cases?
- [ ] Tests are readable and maintainable?

### Documentation
- [ ] README updated if needed?
- [ ] API docs updated?
- [ ] ROADMAP marked complete?
- [ ] Comments added for complex logic?

### Security (if applicable)
- [ ] No credentials in code?
- [ ] Input validation present?
- [ ] SQL injection prevented?
- [ ] XSS prevention in place?
```

### Step 7: Request Changes (if needed)

**Option A: Comment on PR**
```bash
gh pr review 123 --comment -b "
Great work! A few issues:

1. test_login_wrong_password is failing
2. Need to add rate limiting (criterion #7)
3. Password reset not implemented yet

Can you fix these?
"
```

**Option B: In Project Manager Chat**
```
/respond 55 "Almost there! Please fix:
1. Failing test for wrong password
2. Add rate limiting
3. Implement password reset

Then I'll approve."
```

### Step 8: Approve and Merge

Once everything looks good:

```bash
# Approve
gh pr review 123 --approve -b "
✅ All acceptance criteria met
✅ Tests passing (95% coverage)
✅ Manual testing successful
✅ Code quality excellent

Great work! Merging now.
"

# Merge
gh pr merge 123 --squash
```

### Step 9: Verify in ROADMAP

```bash
# Check that ROADMAP was updated
cat docs/roadmap/ROADMAP.md | grep "US-011"
```

Should show:
```markdown
### US-011: User Authentication ✅ Complete (2025-10-10)
```

### Step 10: Celebrate! 🎉

```
In chat: "Great job on US-011! Moving to next priority."
```

---

## 🎓 Summary & Next Steps

You've completed all 7 tutorials! You now know how to:

1. ✅ Implement features autonomously with the daemon
2. ✅ Follow daily workflow for maximum productivity
3. ✅ Monitor and control the daemon
4. ✅ Communicate asynchronously with the daemon (NEW ✨)
5. ✅ Troubleshoot common issues
6. ✅ Write effective user stories
7. ✅ Review code professionally

### Recommended Next Steps:

1. **Practice**: Add 2-3 simple features to your roadmap
2. **Explore**: Try different commands in `/help`
3. **Integrate**: Set up Slack notifications ([SLACK_SETUP_GUIDE.md](SLACK_SETUP_GUIDE.md))
4. **Deep Dive**: Read [US-009_TECHNICAL_SPEC.md](US-009_TECHNICAL_SPEC.md) for architecture
5. **Contribute**: Check [COLLABORATION_METHODOLOGY.md](COLLABORATION_METHODOLOGY.md) for workflow

### Questions?

- **Quick questions**: Check [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md)
- **Feature reference**: See [PROJECT_MANAGER_FEATURES.md](PROJECT_MANAGER_FEATURES.md)
- **Architecture**: See technical specs (US-XXX_TECHNICAL_SPEC.md)
- **Community**: Create an issue on GitHub

---

**Happy Building!** 🚀

---

**Last Updated**: 2025-10-10
**Covers**: US-009 features (daemon control, bidirectional communication)
**Maintained By**: project_manager + community
