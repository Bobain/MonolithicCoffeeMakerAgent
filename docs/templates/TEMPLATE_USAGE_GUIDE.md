# Technical Spec Template Usage Guide

**Purpose**: Guide project managers and architects in creating comprehensive technical specifications with accurate task-level time estimates.

**Version**: 1.0
**Last Updated**: 2025-10-16

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Template Selection](#template-selection)
3. [Template Variables](#template-variables)
4. [Task Sizing Guidelines](#task-sizing-guidelines)
5. [Time Estimation Process](#time-estimation-process)
6. [Examples of Good vs Bad Estimates](#examples-of-good-vs-bad-estimates)
7. [Common Pitfalls](#common-pitfalls)
8. [Best Practices](#best-practices)
9. [Checklist](#checklist)

---

## Quick Start

### 5-Step Process

1. **Identify Feature Type**: CRUD, Integration, UI, or Infrastructure
2. **Select Template**: Use example that matches your feature type
3. **Fill Variables**: Replace all {{VARIABLE}} placeholders
4. **Break into Phases**: Divide work into logical phases (3-5 phases ideal)
5. **Estimate Tasks**: Use sizing guidelines to estimate each task

### Time Investment

- **Simple feature** (CRUD): 15-20 minutes to create spec
- **Medium feature** (Integration): 30-45 minutes to create spec
- **Complex feature** (UI + Backend): 45-60 minutes to create spec
- **Infrastructure**: 20-30 minutes to create spec

**ROI**: Spending 30 minutes on a spec for a 3-day feature improves estimate accuracy by 30-50%.

---

## Template Selection

### Feature Type Decision Tree

```
Start: What are you building?
    ↓
Does it primarily CRUD data?
    YES → Use CRUD_FEATURE_EXAMPLE.md
    NO → Continue
    ↓
Does it integrate with external service?
    YES → Use INTEGRATION_FEATURE_EXAMPLE.md
    NO → Continue
    ↓
Is it primarily UI/frontend?
    YES → Use UI_FEATURE_EXAMPLE.md
    NO → Continue
    ↓
Is it infrastructure/tooling?
    YES → Use INFRASTRUCTURE_FEATURE_EXAMPLE.md
    NO → Use TECHNICAL_SPEC_TEMPLATE.md (custom)
```

### Feature Type Characteristics

#### CRUD Features
**Examples**: User management, blog posts, product catalog
**Characteristics**:
- Database schema required
- Basic CRUD operations (Create, Read, Update, Delete)
- Standard validation rules
- Straightforward UI forms
- Predictable time estimates

**Typical Duration**: 2-4 days

#### Integration Features
**Examples**: Slack integration, payment gateway, email service
**Characteristics**:
- External API dependency
- Authentication/authorization setup
- Error handling for third-party failures
- Webhook/callback handling
- Retry/circuit breaker logic

**Typical Duration**: 3-5 days

#### UI Features
**Examples**: Dashboard, data visualization, interactive widget
**Characteristics**:
- Heavy frontend work
- Responsive design requirements
- User interaction flows
- State management
- Visual design considerations

**Typical Duration**: 3-6 days

#### Infrastructure Features
**Examples**: CI/CD pipeline, monitoring, deployment automation
**Characteristics**:
- Configuration-heavy
- Cross-cutting concern
- Affects multiple systems
- One-time setup with ongoing maintenance
- Documentation-critical

**Typical Duration**: 2-4 days

---

## Template Variables

### Core Variables (Required)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{FEATURE_NAME}}` | Short, descriptive name | "User Authentication System" |
| `{{FEATURE_TYPE}}` | One of: CRUD, Integration, UI, Infrastructure | "Integration" |
| `{{COMPLEXITY}}` | Low, Medium, or High | "Medium" |
| `{{TOTAL_TIME_HOURS}}` | Sum of all task estimates | "32" |
| `{{TOTAL_TIME_DAYS}}` | Hours / 8 (round up) | "4" |
| `{{AUTHOR}}` | Your name or agent name | "project_manager" |
| `{{DATE}}` | Current date | "2025-10-16" |

### Summary Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{FEATURE_SUMMARY}}` | 2-3 sentence overview | "Enable users to log in with email/password or OAuth..." |
| `{{BUSINESS_VALUE}}` | Why this matters to business | "Reduces support tickets by 40%" |
| `{{USER_IMPACT}}` | How users benefit | "Seamless login in under 2 seconds" |
| `{{TECHNICAL_IMPACT}}` | Technical benefits | "Improves security posture with JWT" |

### Requirement Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{REQUIREMENT_X_TITLE}}` | Short requirement name | "Email/Password Login" |
| `{{REQUIREMENT_X_DESCRIPTION}}` | Detailed description | "Users can authenticate using email and password..." |
| `{{ACCEPTANCE_CRITERION_X}}` | Testable criterion | "User receives JWT token on successful login" |

### Phase Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PHASE_X_NAME}}` | Phase name | "Database Schema & Models" |
| `{{PHASE_X_GOAL}}` | What this phase achieves | "Create data model for user accounts" |
| `{{PHASE_X_DURATION}}` | Total hours for phase | "8" |
| `{{TASK_X_Y_TITLE}}` | Task name (X=phase, Y=task) | "Create User model with fields" |
| `{{TASK_X_Y_HOURS}}` | Task estimate | "2" |
| `{{TASK_X_Y_DESCRIPTION}}` | What to do | "Define User model with email, password_hash..." |
| `{{TASK_X_Y_DELIVERABLE}}` | Tangible output | "coffee_maker/models/user.py" |

### Time Estimate Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{IMPLEMENTATION_TIME}}` | Coding time | "1.5" |
| `{{TESTING_TIME}}` | Test writing time | "0.5" |
| `{{DOCUMENTATION_TIME}}` | Doc writing time | "0.3" |
| `{{UNIT_TEST_COVERAGE}}` | Coverage target | "90" |
| `{{INTEGRATION_TEST_COVERAGE}}` | Integration coverage | "80" |

---

## Task Sizing Guidelines

### Task Size Rules

1. **Minimum Size**: 0.5 hours (30 minutes)
   - Anything smaller is too granular
   - Example: "Add docstring to function"

2. **Maximum Size**: 4 hours
   - Larger tasks must be broken down
   - Example: "Implement entire API" → Break into endpoints

3. **Sweet Spot**: 1-3 hours per task
   - Trackable progress
   - Clear deliverables
   - Easy to estimate

### Task Breakdown Formula

```
Total Task Time = Implementation + Testing + Documentation

Where:
- Implementation: Core coding work
- Testing: Unit tests (25-30% of implementation)
- Documentation: Inline docs + user docs (10-15% of implementation)
```

### Task Type Estimates

#### 1. Database Tasks

| Task Type | Typical Time | Breakdown |
|-----------|--------------|-----------|
| Schema design | 1-2h | Design: 1h, Review: 0.5h, Documentation: 0.5h |
| Migration script | 2-3h | Write: 1.5h, Test: 1h, Documentation: 0.5h |
| Model implementation | 1-2h | Code: 1h, Unit tests: 0.5h, Docs: 0.5h |
| Complex queries | 2-3h | Code: 1.5h, Tests: 1h, Optimization: 0.5h |

**Example**: "Create User model with email, password_hash, created_at fields"
- Implementation: 1h (model class, validators)
- Testing: 0.5h (unit tests for model methods)
- Documentation: 0.3h (docstrings)
- **Total**: 1.8h → Round to **2h**

#### 2. API Tasks

| Task Type | Typical Time | Breakdown |
|-----------|--------------|-----------|
| Simple endpoint (CRUD) | 2-3h | Code: 1.5h, Unit tests: 1h, Docs: 0.5h |
| Complex endpoint | 3-4h | Code: 2h, Unit tests: 1.5h, Docs: 0.5h |
| Auth/authorization | 2-3h | Code: 1.5h, Tests: 1h, Security review: 0.5h |
| Business logic | 3-4h | Code: 2h, Tests: 1.5h, Edge cases: 0.5h |

**Example**: "Implement POST /api/users endpoint for user creation"
- Implementation: 1.5h (route, validation, database write)
- Unit tests: 1h (success, validation errors, duplicate email)
- Integration tests: 0.5h (end-to-end flow)
- Documentation: 0.5h (API docs)
- **Total**: 3.5h → Round to **3.5h**

#### 3. UI Tasks

| Task Type | Typical Time | Breakdown |
|-----------|--------------|-----------|
| Simple component | 1-2h | Code: 1h, Styling: 0.5h, Tests: 0.5h |
| Complex component | 2-3h | Code: 1.5h, Styling: 1h, Tests: 0.5h |
| Component integration | 2-3h | Code: 1.5h, State management: 1h, Tests: 0.5h |
| Responsive design | 1h | CSS: 0.5h, Testing: 0.5h |

**Example**: "Create LoginForm component with email/password fields"
- Implementation: 1h (component, validation)
- Styling: 0.5h (Tailwind CSS)
- Testing: 0.5h (component tests)
- **Total**: 2h

#### 4. Infrastructure Tasks

| Task Type | Typical Time | Breakdown |
|-----------|--------------|-----------|
| Environment setup | 2-3h | Config: 1h, Testing: 1h, Docs: 1h |
| CI/CD pipeline | 2-4h | Config: 2h, Testing: 1h, Docs: 1h |
| Deployment automation | 3-4h | Script: 2h, Testing: 1h, Docs: 1h |
| Monitoring setup | 2-3h | Config: 1.5h, Testing: 0.5h, Docs: 1h |

**Example**: "Set up GitHub Actions for automated testing"
- Implementation: 1.5h (.github/workflows/test.yml)
- Testing: 1h (trigger workflow, verify results)
- Documentation: 0.5h (README update)
- **Total**: 3h

#### 5. Testing Tasks

**Formula**:
- **Unit tests**: 25-30% of implementation time
- **Integration tests**: 15-20% of implementation time
- **E2E tests**: 10-15% of total feature time

**Example**: Feature implementation = 12h
- Unit tests: 12h × 0.30 = 3.6h → **3.5h**
- Integration tests: 12h × 0.15 = 1.8h → **2h**
- E2E tests: (12h + 3.5h + 2h) × 0.10 = 1.75h → **2h**

#### 6. Documentation Tasks

| Task Type | Typical Time | Notes |
|-----------|--------------|-------|
| User guide (per feature) | 1-2h | Quick start, examples, troubleshooting |
| API docs (per endpoint) | 0.5-1h | Request/response, examples, errors |
| Architecture docs | 2-3h | Diagrams, decisions, rationale |
| Deployment guide | 1-2h | Setup, config, troubleshooting |
| Code documentation | 10-15% of implementation | Inline docstrings, comments |

**Example**: "Update TUTORIALS.md with User Authentication guide"
- Writing: 1h (quick start, step-by-step)
- Screenshots: 0.5h (capture, annotate)
- Review: 0.5h (polish, links)
- **Total**: 2h

---

## Time Estimation Process

### Step-by-Step Process

#### Step 1: Understand Requirements (5-10 minutes)
- Read user story thoroughly
- Identify all functional requirements
- List non-functional requirements (performance, security)
- Ask clarifying questions if needed

#### Step 2: Define Phases (5-10 minutes)
- Break feature into logical phases (3-5 phases ideal)
- Each phase should have a clear goal
- Order phases by dependency
- Example phases:
  - Phase 1: Data model & schema
  - Phase 2: API endpoints
  - Phase 3: UI components
  - Phase 4: Testing & documentation

#### Step 3: List Tasks (10-20 minutes)
- For each phase, list specific tasks
- Each task should have a clear deliverable
- Use task sizing guidelines for estimates
- Include testing and documentation tasks explicitly

**Example Phase**:
```
Phase 2: API Implementation (10h)

Tasks:
1. POST /api/users endpoint (3.5h)
   - Code: 1.5h
   - Unit tests: 1h
   - Integration tests: 0.5h
   - API docs: 0.5h

2. GET /api/users/:id endpoint (2.5h)
   - Code: 1h
   - Unit tests: 0.5h
   - Integration tests: 0.5h
   - API docs: 0.5h

3. PATCH /api/users/:id endpoint (3h)
   - Code: 1.5h
   - Unit tests: 1h
   - Integration tests: 0.5h

4. DELETE /api/users/:id endpoint (2h)
   - Code: 1h
   - Unit tests: 0.5h
   - Integration tests: 0.5h
```

#### Step 4: Calculate Totals (2-3 minutes)
- Sum all task estimates per phase
- Calculate total across all phases
- Convert hours to days (hours / 8, round up)
- Add 10-20% buffer for unknowns

**Example Calculation**:
```
Phase 1: 8h
Phase 2: 10h
Phase 3: 12h
Phase 4: 6h
-----------
Subtotal: 36h

Buffer (15%): +5.4h
-----------
Total: 41.4h → 42h → 5.25 days → Round to 5-6 days
```

#### Step 5: Validate Estimates (5 minutes)
- Compare to historical data (if available)
- Check if task sizes are within 0.5h-4h range
- Ensure testing is 25-30% of implementation
- Ensure documentation is 10-15% of implementation
- Review with team if estimate seems off

---

## Examples of Good vs Bad Estimates

### Example 1: API Endpoint

**❌ Bad Estimate**:
```
Task: Implement user registration API
Time: 1 day
```

**Problems**:
- No breakdown
- No testing time
- No documentation time
- "1 day" is vague (6h? 8h? 10h?)

**✅ Good Estimate**:
```
Task: POST /api/auth/register endpoint
Time: 4h

Breakdown:
- Implementation: 2h
  - Route handler with validation (1h)
  - Password hashing & user creation (0.5h)
  - Error handling (0.5h)
- Unit tests: 1h
  - Success case (0.3h)
  - Validation errors (0.3h)
  - Duplicate email (0.2h)
  - Password hashing verification (0.2h)
- Integration tests: 0.5h
  - End-to-end registration flow (0.5h)
- Documentation: 0.5h
  - API docs with examples (0.5h)

Deliverable: coffee_maker/api/auth.py, tests/unit/api/test_auth.py
```

### Example 2: Database Schema

**❌ Bad Estimate**:
```
Task: Add database tables
Time: 3h
```

**Problems**:
- Which tables?
- No migration mentioned
- No testing
- Too vague

**✅ Good Estimate**:
```
Phase 1: Database Schema & Models (8h)

Task 1.1: Design User schema (1.5h)
- Implementation: 1h
  - Define fields (email, password_hash, created_at, updated_at)
  - Add indexes (email unique, created_at)
  - Document relationships
- Documentation: 0.5h
  - Schema diagram
  - Field descriptions

Task 1.2: Create migration script (2.5h)
- Implementation: 1.5h
  - Write Alembic migration
  - Add rollback logic
- Testing: 1h
  - Test migration up
  - Test migration down
  - Verify indexes created

Task 1.3: Implement User model (2h)
- Implementation: 1h
  - SQLAlchemy model class
  - Validation methods
  - Helper methods (set_password, check_password)
- Unit tests: 0.5h
  - Model creation
  - Validation
  - Password hashing
- Documentation: 0.5h
  - Docstrings for all methods

Task 1.4: Integration tests for User model (2h)
- Implementation: 1.5h
  - CRUD operations
  - Constraint testing (unique email)
  - Edge cases
- Documentation: 0.5h
  - Test documentation
```

### Example 3: UI Component

**❌ Bad Estimate**:
```
Task: Build login page
Time: 4h
```

**Problems**:
- No component breakdown
- No styling time
- No testing
- No responsive design

**✅ Good Estimate**:
```
Phase 3: Login UI (10h)

Task 3.1: LoginForm component (2.5h)
- Implementation: 1.5h
  - Form fields (email, password)
  - Client-side validation
  - Submit handler
- Styling: 0.5h
  - Tailwind CSS layout
  - Error message styling
- Testing: 0.5h
  - Component render tests
  - Validation tests

Task 3.2: Login page layout (2h)
- Implementation: 1h
  - Page component
  - Header/footer integration
  - Logo and branding
- Styling: 0.5h
  - Responsive design
  - Mobile layout
- Testing: 0.5h
  - Responsive tests

Task 3.3: Authentication state management (2.5h)
- Implementation: 1.5h
  - Redux/Context setup
  - Login action
  - Token storage
- Testing: 1h
  - State update tests
  - Token persistence tests

Task 3.4: Error handling & UX (2h)
- Implementation: 1h
  - Error messages
  - Loading states
  - Success redirects
- Styling: 0.5h
  - Error styling
  - Loading spinners
- Testing: 0.5h
  - Error scenario tests

Task 3.5: E2E login flow test (1h)
- Implementation: 1h
  - Puppeteer test
  - Success flow
  - Error scenarios
```

---

## Common Pitfalls

### Pitfall 1: Forgetting Testing Time

**Problem**: Estimate 8h for implementation, forget 2-3h for tests
**Solution**: Always add testing as separate tasks (25-30% of implementation)

**Example**:
```
❌ Task: Implement API endpoint (3h)

✅ Task: Implement API endpoint (3h)
   + Unit tests (1h)
   + Integration tests (0.5h)
   = 4.5h total
```

### Pitfall 2: Forgetting Documentation Time

**Problem**: No time allocated for docs, leads to poor documentation
**Solution**: Add documentation tasks explicitly (10-15% of implementation)

**Example**:
```
❌ Phase 2: API Implementation (12h)

✅ Phase 2: API Implementation (12h)
   + API documentation (1.5h)
   + Code docstrings (0.5h)
   = 14h total
```

### Pitfall 3: Tasks Too Large

**Problem**: "Implement authentication system (16h)"
**Solution**: Break into smaller tasks (0.5h-4h each)

**Example**:
```
❌ Task: Implement authentication (16h)

✅ Phase 2: Authentication (16h)
   Task 2.1: User model & schema (2h)
   Task 2.2: Password hashing (1.5h)
   Task 2.3: JWT token generation (2h)
   Task 2.4: Login endpoint (3.5h)
   Task 2.5: Logout endpoint (1.5h)
   Task 2.6: Token refresh endpoint (2.5h)
   Task 2.7: Integration tests (2h)
   Task 2.8: API documentation (1h)
```

### Pitfall 4: No Buffer for Unknowns

**Problem**: Exact estimates with no margin for error
**Solution**: Add 10-20% buffer for unknowns, complexities

**Example**:
```
❌ Total: 32h (4 days exact)

✅ Total: 32h implementation
   + 4.8h buffer (15%)
   = 36.8h → 37h → 4.6 days → Round to 5 days
```

### Pitfall 5: Ignoring Dependencies

**Problem**: Estimate tasks independently, ignore waiting time
**Solution**: Identify dependencies, add blocked time if needed

**Example**:
```
❌ Phase 2: API (12h) - can start immediately

✅ Phase 2: API (12h)
   Dependencies:
   - Phase 1: Database schema must be complete first
   - External: OAuth provider setup (user approval needed - 1 day)

   Critical Path: Phase 1 (8h) → Wait (8h) → Phase 2 (12h)
   Total time: 28h (3.5 days)
```

### Pitfall 6: Underestimating UI Work

**Problem**: "Build dashboard (4h)" - way too low
**Solution**: Break UI into components, styling, state management

**Example**:
```
❌ Task: Build analytics dashboard (4h)

✅ Phase 3: Analytics Dashboard (20h)
   Task 3.1: Chart components (4h)
   Task 3.2: Data fetching & state (3h)
   Task 3.3: Layout & responsive design (3h)
   Task 3.4: Filter controls (2.5h)
   Task 3.5: Export functionality (2h)
   Task 3.6: Loading & error states (1.5h)
   Task 3.7: Component tests (2h)
   Task 3.8: E2E tests (1.5h)
   Task 3.9: User documentation (0.5h)
```

---

## Best Practices

### 1. Start with Historical Data

If you have metrics from US-015, use them:
- Look at similar features completed recently
- Check actual vs estimated time ratios
- Adjust estimates based on historical accuracy

### 2. Be Specific with Deliverables

Each task should have a tangible output:
- File names (coffee_maker/models/user.py)
- Test files (tests/unit/test_user.py)
- Documentation updates (TUTORIALS.md section added)

### 3. Include Edge Cases

Don't just estimate happy path:
- Error handling
- Validation
- Edge cases
- Rollback scenarios

### 4. Consider Team Familiarity

Adjust estimates based on experience:
- New technology: +30-50% time
- Familiar technology: -10-20% time
- First time doing X: +50% time

### 5. Review and Iterate

After completing a feature:
- Compare actual vs estimated time
- Identify what was underestimated
- Update estimation guidelines
- Feed data into US-015 metrics system

### 6. Get Second Opinions

For complex features:
- Review spec with another team member
- Ask "Am I missing anything?"
- Sanity check total time estimate

### 7. Document Assumptions

If your estimate depends on something:
- Document the assumption
- Note impact if assumption is wrong
- Example: "Assumes OAuth provider already configured (+4h if not)"

---

## Checklist

### Before Finalizing Spec

- [ ] All {{VARIABLES}} replaced with actual values
- [ ] Feature type selected (CRUD, Integration, UI, Infrastructure)
- [ ] Complexity level assigned (Low, Medium, High)
- [ ] Broken into 3-5 phases
- [ ] Each phase has clear goal
- [ ] All tasks are 0.5h-4h in size
- [ ] Testing time included (25-30% of implementation)
- [ ] Documentation time included (10-15% of implementation)
- [ ] Dependencies identified and documented
- [ ] Risks identified with mitigations
- [ ] Success criteria defined
- [ ] Total time calculated and converted to days
- [ ] 10-20% buffer added for unknowns
- [ ] Compared to historical data (if available)
- [ ] Reviewed by another team member (if possible)

### After Creating Spec

- [ ] Spec saved to docs/roadmap/PRIORITY_X_TECHNICAL_SPEC.md
- [ ] Referenced in ROADMAP.md
- [ ] Estimate communicated to user
- [ ] User approved the estimate
- [ ] Ready to begin implementation

---

## Quick Reference: Estimation Formulas

### Total Task Time
```
Task Time = Implementation + Testing + Documentation

Where:
- Testing = Implementation × 0.30 (30%)
- Documentation = Implementation × 0.15 (15%)
- Total = Implementation × 1.45
```

### Phase Time
```
Phase Time = Σ(all task times in phase)
```

### Total Feature Time
```
Feature Time = Σ(all phase times) × 1.15 (15% buffer)
Convert to days = Feature Time / 8 (round up)
```

### Confidence Intervals
```
Best Case = Feature Time × 0.80
Expected = Feature Time × 1.00
Worst Case = Feature Time × 1.30
```

---

## Examples by Complexity

### Low Complexity (2-3 days)
- Simple CRUD operations
- Basic UI components
- Standard integrations (well-documented APIs)

### Medium Complexity (3-5 days)
- Custom business logic
- Complex UI interactions
- Integrations with error handling
- Performance optimization

### High Complexity (5-10 days)
- Novel features (no existing patterns)
- Multiple system integrations
- Advanced UI with real-time updates
- Security-critical features

---

**End of Template Usage Guide**

For detailed examples, see:
- docs/templates/examples/CRUD_FEATURE_EXAMPLE.md
- docs/templates/examples/INTEGRATION_FEATURE_EXAMPLE.md
- docs/templates/examples/UI_FEATURE_EXAMPLE.md
- docs/templates/examples/INFRASTRUCTURE_FEATURE_EXAMPLE.md
