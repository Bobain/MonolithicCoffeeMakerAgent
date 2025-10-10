# Coffee Maker Agent - Documentation

**Welcome!** This directory contains all project documentation, guides, and specifications.

---

## 🚀 Quick Start - New Users

**First time here?** Start with these three documents:

1. **[QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md)** (5 minutes)
   - Get up and running quickly
   - Learn basic commands
   - Start using the system

2. **[TUTORIALS.md](TUTORIALS.md)** (20-30 minutes)
   - 7 practical tutorials
   - Step-by-step examples
   - Common workflows

3. **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** (reference)
   - Complete documentation map
   - Navigation by user type
   - Topic-based index

**Then explore based on your role:**
- 🎓 **End User** → [USER_JOURNEY_PROJECT_MANAGER.md](USER_JOURNEY_PROJECT_MANAGER.md)
- 👨‍💻 **Developer** → [COLLABORATION_METHODOLOGY.md](COLLABORATION_METHODOLOGY.md)
- 🔧 **Contributor** → [E2E_TESTING_GUIDE.md](E2E_TESTING_GUIDE.md)

---

## 📋 Core Documents

### Project Roadmap
- **[ROADMAP.md](ROADMAP.md)** ⭐ **SINGLE SOURCE OF TRUTH**
  - All project priorities and features
  - Current status and progress
  - What's being worked on next
  - Used by daemon, project-manager, and humans

### Team Collaboration
- **[COLLABORATION_METHODOLOGY.md](COLLABORATION_METHODOLOGY.md)** (v1.1)
  - How we work as a team
  - Communication protocols
  - Definition of Done
  - Security rules (Section 12)

### Getting Started
- **[QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md)**
  - 5-minute setup guide
  - First commands to try
  - Common troubleshooting

- **[TUTORIALS.md](TUTORIALS.md)**
  - Tutorial 1: First Feature Implementation
  - Tutorial 2: Daily Developer Workflow
  - Tutorial 3: Daemon Monitoring & Control
  - Tutorial 4: Bidirectional Communication
  - Tutorial 5: Troubleshooting
  - Tutorial 6: Writing User Stories
  - Tutorial 7: Code Review Workflow

### Feature Documentation
- **[PROJECT_MANAGER_FEATURES.md](PROJECT_MANAGER_FEATURES.md)**
  - Complete command reference
  - All available features
  - Configuration options

- **[DAEMON_USAGE.md](DAEMON_USAGE.md)** (540 lines)
  - How the autonomous daemon works
  - Starting/stopping the daemon
  - Monitoring progress

- **[USER_JOURNEY_PROJECT_MANAGER.md](USER_JOURNEY_PROJECT_MANAGER.md)**
  - Complete workflow walkthrough
  - Daily/weekly usage patterns
  - Code review process

---

## 🏗️ Technical Specifications

### User Stories (Completed Features)
- **[US-006_TECHNICAL_SPEC.md](US-006_TECHNICAL_SPEC.md)** - Chat UX improvements
- **[US-009_TECHNICAL_SPEC.md](US-009_TECHNICAL_SPEC.md)** - Process management & status monitoring

### Architecture & Design
- **[PROJECT_MANAGER_MVP_DESIGN.md](PROJECT_MANAGER_MVP_DESIGN.md)** (696 lines)
  - System architecture
  - Database design
  - CLI commands spec

- **[PRIORITY_1.5_DATABASE_SYNC_DESIGN.md](PRIORITY_1.5_DATABASE_SYNC_DESIGN.md)** (450 lines)
  - Database synchronization architecture
  - 4 architectural options analyzed
  - Implementation guidelines

- **[PRIORITY_2_TECHNICAL_SPEC.md](PRIORITY_2_TECHNICAL_SPEC.md)**
  - Project Manager CLI detailed spec
  - Notification system design

### Architecture Decision Records (ADRs)
- **[ADR_001_DATABASE_SYNC_STRATEGY.md](ADR_001_DATABASE_SYNC_STRATEGY.md)**
  - Why we chose SQLite with WAL mode
  - Alternatives considered
  - Trade-offs and consequences

---

## 🧪 Testing & Quality

- **[E2E_TESTING_GUIDE.md](E2E_TESTING_GUIDE.md)** - End-to-end testing strategy
- **[DOD_TESTING_DESIGN.md](DOD_TESTING_DESIGN.md)** - Definition of Done for testing
- **[USER_STORY_DESIGN.md](USER_STORY_DESIGN.md)** - How we write user stories

---

## 🔧 Setup & Integration

- **[SLACK_SETUP_GUIDE.md](SLACK_SETUP_GUIDE.md)** - Get notifications in Slack
- **[CLAUDE_CLI_MODE.md](CLAUDE_CLI_MODE.md)** - Using Claude CLI vs API
- **[PROJECT_MANAGER_CLI_USAGE.md](PROJECT_MANAGER_CLI_USAGE.md)** - CLI internals

---

## 📊 Session Summaries & Changelogs

Recent work and decisions:
- **[SESSION_SUMMARY_2025_10_09_PRIORITY_2_COMPLETE.md](SESSION_SUMMARY_2025_10_09_PRIORITY_2_COMPLETE.md)**
- **[SESSION_SUMMARY_2025_10_09_DB_SYNC_COMPLETE.md](SESSION_SUMMARY_2025_10_09_DB_SYNC_COMPLETE.md)**
- **[CHANGELOG_2025_10_09_database_guardrails.md](CHANGELOG_2025_10_09_database_guardrails.md)**
- **[SPRINT_SUMMARY_2025_10_09.md](SPRINT_SUMMARY_2025_10_09.md)**

---

## 📁 Documentation Organization

### By Document Type

```
docs/
├── README.md                          ← You are here!
├── DOCUMENTATION_INDEX.md             ← Complete navigation hub
├── ROADMAP.md                         ⭐ Single source of truth
│
├── Quick Start/
│   ├── QUICKSTART_PROJECT_MANAGER.md
│   ├── TUTORIALS.md
│   └── USER_JOURNEY_PROJECT_MANAGER.md
│
├── Feature Docs/
│   ├── PROJECT_MANAGER_FEATURES.md
│   ├── DAEMON_USAGE.md
│   └── COLLABORATION_METHODOLOGY.md
│
├── Technical Specs/
│   ├── US-*_TECHNICAL_SPEC.md
│   ├── PRIORITY_*_TECHNICAL_SPEC.md
│   └── *_DESIGN.md
│
├── Testing & Quality/
│   ├── E2E_TESTING_GUIDE.md
│   ├── DOD_TESTING_DESIGN.md
│   └── USER_STORY_DESIGN.md
│
├── Setup Guides/
│   ├── SLACK_SETUP_GUIDE.md
│   └── CLAUDE_CLI_MODE.md
│
├── Architecture Decisions/
│   └── ADR_*_*.md
│
├── Session Summaries/
│   └── SESSION_SUMMARY_*.md
│
└── Templates/
    └── DEVELOPER_DOCUMENTATION_TEMPLATE.md
```

### By User Type

**📱 End Users** (using the system):
→ Start: [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md)
→ Learn: [TUTORIALS.md](TUTORIALS.md)
→ Reference: [PROJECT_MANAGER_FEATURES.md](PROJECT_MANAGER_FEATURES.md)

**👨‍💻 Developers** (understanding the system):
→ Architecture: [COLLABORATION_METHODOLOGY.md](COLLABORATION_METHODOLOGY.md)
→ Roadmap: [ROADMAP.md](ROADMAP.md)
→ Specs: US-XXX_TECHNICAL_SPEC.md files

**🔧 Contributors** (building the system):
→ Workflow: [COLLABORATION_METHODOLOGY.md](COLLABORATION_METHODOLOGY.md)
→ Testing: [E2E_TESTING_GUIDE.md](E2E_TESTING_GUIDE.md)
→ Templates: [templates/DEVELOPER_DOCUMENTATION_TEMPLATE.md](templates/DEVELOPER_DOCUMENTATION_TEMPLATE.md)

---

## 🔍 How to Find What You Need

| I want to... | Check this document |
|--------------|---------------------|
| Get started quickly | [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md) |
| Learn with examples | [TUTORIALS.md](TUTORIALS.md) |
| See all features | [PROJECT_MANAGER_FEATURES.md](PROJECT_MANAGER_FEATURES.md) |
| Understand the roadmap | [ROADMAP.md](ROADMAP.md) |
| Learn the workflow | [COLLABORATION_METHODOLOGY.md](COLLABORATION_METHODOLOGY.md) |
| Run the daemon | [DAEMON_USAGE.md](DAEMON_USAGE.md) |
| Set up Slack | [SLACK_SETUP_GUIDE.md](SLACK_SETUP_GUIDE.md) |
| Write tests | [E2E_TESTING_GUIDE.md](E2E_TESTING_GUIDE.md) |
| Troubleshoot issues | [TUTORIALS.md](TUTORIALS.md#tutorial-5-troubleshooting) |
| Navigate all docs | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |

---

## ⚠️ Important: ROADMAP.md is Special

**[ROADMAP.md](ROADMAP.md)** is the **SINGLE SOURCE OF TRUTH** for:
- All project priorities and features
- Current implementation status
- What the daemon works on next

**Rules:**
- ✅ Always edit ROADMAP.md directly (never create alternative roadmap files)
- ✅ Both daemon and project-manager read/write this same file
- ✅ Uses file locking to prevent conflicts
- ❌ NEVER create ROADMAP_v2.md, roadmap_backup.md, etc.

See [README_DOCS.md](README_DOCS.md) for detailed documentation structure rules.

---

## 📊 Documentation Statistics

- **Total Files**: 26+ documentation files
- **Total Lines**: ~10,000+ lines of documentation
- **Tutorials**: 7 practical step-by-step guides
- **Technical Specs**: 3 major specifications
- **Last Updated**: 2025-10-10 (US-010 completion)

---

## 🆘 Getting Help

**Quick questions?**
→ Check [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md) or [TUTORIALS.md](TUTORIALS.md)

**Feature details?**
→ See [PROJECT_MANAGER_FEATURES.md](PROJECT_MANAGER_FEATURES.md)

**Architecture questions?**
→ See technical specs (US-XXX_TECHNICAL_SPEC.md)

**Troubleshooting?**
→ See [TUTORIALS.md](TUTORIALS.md#tutorial-5-troubleshooting)

**Still stuck?**
→ Create an issue on GitHub or check [ROADMAP.md](ROADMAP.md) for planned improvements

---

## 🎯 Key Takeaways

1. ✅ Start with [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md) (5 min)
2. ✅ Practice with [TUTORIALS.md](TUTORIALS.md) (20-30 min)
3. ✅ Reference [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for navigation
4. ✅ [ROADMAP.md](ROADMAP.md) is the single source of truth
5. ✅ [COLLABORATION_METHODOLOGY.md](COLLABORATION_METHODOLOGY.md) explains how we work

**Welcome to Coffee Maker Agent!** 🚀☕

---

**Maintained by**: Project Manager + code_developer daemon + community
**Questions?**: Check [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) or create a GitHub issue
