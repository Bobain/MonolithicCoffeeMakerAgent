# User-Listener Quick Start Guide

The **user-listener** is your primary interface to the MonolithicCoffeeMakerAgent team. It's an intelligent CLI that understands what you want to do and automatically routes you to the right agent.

---

## Getting Started (30 seconds)

### Step 1: Start the User-Listener

```bash
poetry run user-listener
```

You'll see:
```
User Listener · Primary Interface
Powered by Claude Haiku 4.5

I'm your interface to the agent team.
Tell me what you need, and I'll route it to the right specialist.
Type /exit or /quit to leave.

›
```

### Step 2: Type What You Want

Just type in natural language. The user-listener will figure out who should help:

```
› Show me the roadmap
```

The system automatically detects this is about roadmap/planning and routes to **project_manager**.

### Step 3: Read the Response

The right agent responds with expertise:
```
Project Manager: Here's the current roadmap...
[detailed roadmap information]
```

### Step 4: Exit When Done

```
› /exit
```

That's it! You're using the agent team.

---

## Common Tasks

### I want to ask about project status

```
› What's the current project status
› Show me the roadmap
› How many priorities are complete
› What's next on our list
```

**Routes to**: project_manager

**You get**: Strategic planning info, milestones, progress tracking

---

### I want to design something

```
› Design a caching layer
› What's the best architecture for authentication
› How should we structure the database
› Design pattern recommendation
```

**Routes to**: architect

**You get**: Technical specifications, design guidance, best practices

---

### I want to build something

```
› Implement the new feature
› Fix the authentication bug
› Write code for US-045
› Create a pull request
```

**Routes to**: code_developer

**You get**: Implementation guidance, code examples, development support

---

### I want a demo or explanation

```
› Create a demo for me
› Show me how the dashboard works
› Explain how this feature works
› Can you test this functionality
```

**Routes to**: assistant

**You get**: Visual demos, documentation, clear explanations, testing

---

### I want to analyze the code

```
› Where is authentication implemented
› Find where the API is defined
› Search for the database code
› Analyze the security
```

**Routes to**: assistant (with code analysis skills)

**You get**: Deep code analysis, patterns, dependencies, security review

---

### I want UI/UX help

```
› Improve the dashboard UI
› Design a better layout
› Make it look prettier with Tailwind
› What should the chart visualization show
```

**Routes to**: ux-design-expert

**You get**: Design guidance, Tailwind CSS expertise, visual recommendations

---

## How It Works

The user-listener uses a two-stage system to understand your request:

### Stage 1: Pattern Matching (Fast)
The system looks for keywords in your message:

- **"design"** → architect
- **"roadmap"** → project_manager
- **"implement"** → code_developer
- **"demo"** → assistant
- **"where is"** → assistant (with code analysis skills)
- **"ui"** → ux-design-expert

**Confidence**: 90% (very likely correct)

### Stage 2: AI Classification (Fallback)
If your request doesn't match any pattern, Claude Haiku 4.5 reads your message and figures out which agent makes sense.

**Confidence**: 50-80% (less certain, but adaptive)

**Threshold**: If confidence is below 80%, the user-listener handles it directly rather than routing.

---

## Tips & Tricks

### Be Specific
Instead of:
```
› Tell me about the project
```

Try:
```
› What's the current project roadmap
```
This matches the "roadmap" keyword → routes correctly to project_manager

### Use Natural Language
You don't need to be formal. All of these work:

```
› Design a caching layer
› How should we cache things
› What's a good caching strategy
› Build a caching system
```

All route to architect because they contain "design" or similar keywords.

### Ask for What You Need
- Want demos? Ask assistant
- Want implementation? Ask code_developer
- Want architecture? Ask architect
- Want to understand code? Ask assistant (with code analysis skills)
- Want project info? Ask project_manager
- Want UI improvement? Ask ux-design-expert

### Multi-Turn Conversations
The user-listener remembers your conversation history:

```
› Design a caching system
[architect responds with design]

› Now implement it
[code_developer responds with implementation plan]

› Can you show me how to use it
[assistant responds with demo]
```

Each request is understood in context.

---

## Commands

| Command | Effect |
|---------|--------|
| `/exit` | Exit the user-listener |
| `/quit` | Exit the user-listener |
| Ctrl+C | Interrupt and exit gracefully |

---

## What If I Get the Wrong Agent?

Don't worry! If the user-listener routes your request to the wrong agent:

1. **The agent still tries to help** - Even if you get code_developer instead of assistant (with code analysis skills), the developer might still understand your question
2. **Ask more specifically** - Be more explicit about what you want:
   - Instead of: "Where is authentication"
   - Try: "Find where authentication is implemented in the code"
3. **Use the AI fallback** - If your request is ambiguous, the user-listener might handle it directly instead of routing, which can work too

---

## Common Questions

### Q: Can I run multiple user-listeners?

**A**: No, only one instance can run at a time. If you try to run a second one, you'll get an error:
```
Error: Agent 'user_listener' is already running! PID: 12345
```

Stop the first instance first:
```bash
pkill -f "user-listener"
```

### Q: Does it work offline?

**A**: No, the user-listener needs an API key to call Claude Haiku 4.5. The system checks for `ANTHROPIC_API_KEY` in your `.env` file.

### Q: How long does it take to respond?

**A**:
- Pattern matching: < 100ms (very fast)
- AI routing/delegation: 1-2 seconds (reasonable)
- Getting specialized agent response: 5-30 seconds (depends on complexity)

### Q: Does it remember past conversations?

**A**: Yes! The user-listener loads your conversation history from previous sessions. You can reference things you discussed before.

### Q: Can I use it programmatically?

**A**: Currently, the user-listener is a CLI tool for manual interactions. Future versions might support API access or integration with other systems.

---

## Examples Walkthrough

### Example 1: Getting Project Status

```bash
$ poetry run user-listener

User Listener · Primary Interface
Powered by Claude Haiku 4.5

I'm your interface to the agent team.
Tell me what you need, and I'll route it to the right specialist.
Type /exit or /quit to leave.

› What's our project status

[system routes to project_manager]

Project Manager: Here's the current status:
  - 10 priorities completed
  - 3 priorities in progress
  - 5 priorities planned
  - Next milestone: End of October

Overall health: 🟢 On track

› /exit

Goodbye!
```

### Example 2: Designing a Feature

```bash
› Design a user authentication system

[system routes to architect]

Architect: To design a user authentication system, consider:

1. **Architecture**:
   - Use JWT tokens for stateless auth
   - Store user credentials with bcrypt hashing
   - Implement OAuth2 for third-party integrations

2. **Security**:
   - Rate limiting on login attempts
   - Session timeout after 1 hour
   - HTTPS for all auth endpoints

3. **Best Practices**:
   - Never store passwords in plain text
   - Use CORS properly
   - Implement CSRF protection

Would you like me to create a technical spec for this?

› Yes please

Architect: Creating spec at: docs/architecture/specs/SPEC-011-authentication.md

› /exit
```

### Example 3: Multi-Agent Workflow

```bash
› Design and implement a caching layer

[system routes to architect for design]

Architect: I'm designing a caching layer...
[design response]

› Now implement it

[system routes to code_developer for implementation]

Code Developer: I'll implement the caching layer...
[implementation response]

› Create a demo

[system routes to assistant for demo]
