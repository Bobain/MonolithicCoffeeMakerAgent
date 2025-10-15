# Streamlit ACE Configuration & Monitoring App

**Status**: 📝 Planned (NEXT PRIORITY after ACE full implementation)
**Date**: 2025-10-15
**Priority**: HIGH (User-requested next priority)

---

## Overview

A Streamlit web application for visual configuration and monitoring of the ACE Framework (Agentic Context Engineering). This app provides a user-friendly interface for:

1. **Configuration**: Enable/disable ACE per agent, adjust parameters
2. **Monitoring**: Real-time trace visualization, playbook inspection
3. **Analytics**: Agent performance metrics, learning progress
4. **Curation**: Interactive playbook management and refinement

---

## User Requirements

> **User Request**: "The next priority, when ACE framework is fully implemented will be to have a streamlit app that enables to configure and monitor the ACE system"

### Key Goals

- ✅ **Visual Configuration**: No more editing .env files manually
- ✅ **Real-Time Monitoring**: See what agents are learning in real-time
- ✅ **Playbook Management**: Review and curate agent playbooks visually
- ✅ **Performance Insights**: Understand which agents benefit most from ACE
- ✅ **Easy Opt-Out**: Toggle ACE per agent with visual feedback

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Streamlit App (Port 8501)                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Config Tab │  │ Monitor  │  │ Playbook │           │
│  │            │  │   Tab    │  │   Tab    │           │
│  └────────────┘  └──────────┘  └──────────┘           │
│        │              │              │                  │
│        ↓              ↓              ↓                  │
│  ┌──────────────────────────────────────────┐          │
│  │ ACE API Layer                             │          │
│  │ (coffee_maker/autonomous/ace/api.py)      │          │
│  └──────────────────────────────────────────┘          │
│        │              │              │                  │
└────────┼──────────────┼──────────────┼──────────────────┘
         │              │              │
         ↓              ↓              ↓
┌────────────────────────────────────────────────┐
│ ACE Framework Components                       │
├────────────────────────────────────────────────┤
│ • Generator (traces)                           │
│ • Reflector (insights)                         │
│ • Curator (playbooks)                          │
│ • Config (settings)                            │
└────────────────────────────────────────────────┘
         │              │              │
         ↓              ↓              ↓
┌────────────────────────────────────────────────┐
│ File System                                    │
├────────────────────────────────────────────────┤
│ • docs/generator/traces/                       │
│ • docs/reflector/deltas/                       │
│ • docs/curator/playbooks/                      │
│ • .env (configuration)                         │
└────────────────────────────────────────────────┘
```

---

## Features Specification

### 1. Configuration Tab

**Purpose**: Visual configuration of ACE settings

#### 1.1 Agent ACE Toggles

```
┌─────────────────────────────────────────────────────┐
│ ACE Agent Configuration                              │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ✅ user_interpret          [ENABLED] [Disable]      │
│    └─ Fast operations, high volume                  │
│    └─ Traces: 127 today, 1,453 total                │
│                                                      │
│ ✅ assistant               [ENABLED] [Disable]      │
│    └─ Good volume, quick feedback                   │
│    └─ Traces: 89 today, 982 total                   │
│                                                      │
│ ✅ code-searcher           [ENABLED] [Disable]      │
│    └─ Moderate volume, clear metrics                │
│    └─ Traces: 34 today, 401 total                   │
│                                                      │
│ ❌ code_developer          [DISABLED] [Enable]      │
│    └─ Slow operations (opt-out during dev)          │
│    └─ Traces: 0 today, 15 total                     │
│                                                      │
│ ❌ user_listener           [DISABLED] [Enable]      │
│    └─ UI only (no learning needed)                  │
│    └─ Traces: 0 today, 0 total                      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Toggle ACE per agent with immediate visual feedback
- Show trace counts (today / total)
- Display agent description and recommended status
- Color-coded status (green = enabled, red = disabled)
- One-click enable/disable (writes to .env)

#### 1.2 ACE Parameters

```
┌─────────────────────────────────────────────────────┐
│ ACE Configuration Parameters                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Trace Directory:                                     │
│ [docs/generator/traces/           ] 📁              │
│                                                      │
│ Delta Directory:                                     │
│ [docs/reflector/deltas/           ] 📁              │
│                                                      │
│ Playbook Directory:                                  │
│ [docs/curator/playbooks/          ] 📁              │
│                                                      │
│ Similarity Threshold: [0.85] ───────────────●───┐   │
│                                            (0-1)    │
│                                                      │
│ Pruning Rate: [0.10] ────●──────────────────────┐   │
│                      (0-1, 10% default)            │
│                                                      │
│ Max Bullets: [150] ━━━━━━━━━━●━━━━━━━━━━━━━━━━┐   │
│                           (50-300)                  │
│                                                      │
│ Auto-Reflect: ☐ Enabled                             │
│ Auto-Curate: ☐ Enabled                              │
│                                                      │
│            [Save Configuration] [Reset to Defaults] │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Visual sliders for numeric parameters
- Directory pickers with validation
- Checkboxes for boolean settings
- Save button writes to .env
- Reset to defaults button
- Validation warnings (e.g., "similarity threshold must be 0-1")

---

### 2. Monitor Tab

**Purpose**: Real-time monitoring of ACE system activity

#### 2.1 Live Trace Feed

```
┌─────────────────────────────────────────────────────┐
│ Live Trace Feed                    [Pause] [Resume] │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 🟢 user_interpret     2025-10-15 14:32:15          │
│    Prompt: "add a login feature"                    │
│    Result: success                                   │
│    Duration: 1.2s                                    │
│    Intent: add_feature → code_developer             │
│    [View Details] [View Trace JSON]                 │
│                                                      │
│ 🟢 assistant          2025-10-15 14:31:48          │
│    Prompt: "how do I run tests?"                    │
│    Result: success                                   │
│    Duration: 2.5s                                    │
│    [View Details] [View Trace JSON]                 │
│                                                      │
│ 🔴 code_developer     2025-10-15 14:28:12          │
│    Prompt: "Implement login feature"                │
│    Result: failure                                   │
│    Duration: 1200.3s (20min)                        │
│    Error: "ModuleNotFoundError: bcrypt"             │
│    [View Details] [View Trace JSON]                 │
│                                                      │
│ [Load More (showing 3 of 127 today)]               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Real-time streaming of new traces (WebSocket or polling)
- Color-coded status (🟢 success, 🔴 failure, 🟡 partial)
- Expandable details per trace
- Link to full trace JSON
- Filters: by agent, by date, by result status
- Search traces by prompt content

#### 2.2 Agent Performance Dashboard

```
┌─────────────────────────────────────────────────────┐
│ Agent Performance (Last 7 Days)                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│ user_interpret                                       │
│ ████████████████████████████████████ 95% success   │
│ 127 traces today │ 1,453 total │ Avg: 1.2s         │
│                                                      │
│ assistant                                            │
│ ████████████████████████████████ 89% success       │
│ 89 traces today │ 982 total │ Avg: 2.8s            │
│                                                      │
│ code-searcher                                        │
│ ████████████████████████████████████ 97% success   │
│ 34 traces today │ 401 total │ Avg: 5.4s            │
│                                                      │
│ code_developer                                       │
│ ██████████████████ 65% success (⚠️ needs attention)│
│ 0 traces today │ 15 total │ Avg: 1200s (20min)     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Success rate bars (visual progress bars)
- Trace counts (today / total)
- Average execution time
- Warnings for low success rates
- Click to drill down into specific agent

#### 2.3 Reflection Status

```
┌─────────────────────────────────────────────────────┐
│ Reflector Status                                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Last Run: 2025-10-15 14:00:00 (32 minutes ago)     │
│ Traces Analyzed: 45                                  │
│ Delta Items Generated: 12                            │
│                                                      │
│ Pending Traces: 82 (waiting for reflection)         │
│                                                      │
│ [Run Reflector Now] [Schedule Auto-Reflect]         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Show last reflection run timestamp
- Pending trace count
- Manual trigger button
- Schedule auto-reflection
- View latest delta items

---

### 3. Playbook Tab

**Purpose**: Interactive playbook management and curation

#### 3.1 Playbook Browser

```
┌─────────────────────────────────────────────────────┐
│ Agent Playbooks                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [user_interpret ▼]                                  │
│                                                      │
│ Playbook: user_interpret                             │
│ Last Updated: 2025-10-15 14:00:00                   │
│ Size: 147 bullets (out of 150 max)                  │
│ Effectiveness: 0.82 (⭐⭐⭐⭐)                      │
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 🎯 Intent Interpretation (42 bullets)           │ │
│ │ ├─ When user says "implement" → add_feature     │ │
│ │ │  Helpful: 25 | Unhelpful: 2 | Confidence: 0.9 │ │
│ │ ├─ When user says "broken" → report_bug         │ │
│ │ │  Helpful: 18 | Unhelpful: 1 | Confidence: 0.88│ │
│ │ └─ ... (40 more)                                 │ │
│ │                                                  │ │
│ │ 💭 Sentiment Analysis (38 bullets)              │ │
│ │ ├─ Detect frustration from repeated issues      │ │
│ │ │  Helpful: 14 | Unhelpful: 0 | Confidence: 0.95│ │
│ │ └─ ... (37 more)                                 │ │
│ │                                                  │ │
│ │ 🤝 Agent Delegation (35 bullets)                │ │
│ │ ├─ delegate to code_developer for features      │ │
│ │ │  Helpful: 32 | Unhelpful: 3 | Confidence: 0.85│ │
│ │ └─ ... (34 more)                                 │ │
│ │                                                  │ │
│ │ 🔍 Context Understanding (32 bullets)           │ │
│ │ └─ ... (32 bullets)                              │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ [Run Curator Now] [Export Playbook] [Import]        │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Dropdown to select agent playbook
- Collapsible categories with bullet counts
- Expandable bullets showing helpfulness scores
- Visual effectiveness rating (stars)
- Manual curation trigger
- Export playbook to JSON
- Import playbook from JSON

#### 3.2 Bullet Detail View

```
┌─────────────────────────────────────────────────────┐
│ Bullet Detail                                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Content:                                             │
│ "When user says 'implement' → interpret as           │
│  add_feature intent and delegate to code_developer"  │
│                                                      │
│ Category: Intent Interpretation                      │
│ Confidence: 0.90                                     │
│ Helpful Count: 25                                    │
│ Unhelpful Count: 2                                   │
│                                                      │
│ Source Traces:                                       │
│ • trace_2025-10-15_14-32-15_user_interpret.json     │
│ • trace_2025-10-15_12-18-42_user_interpret.json     │
│ • ... (23 more traces)                               │
│                                                      │
│ Similar Bullets (semantic similarity > 0.85):        │
│ • "implement keyword suggests feature request"       │
│   (similarity: 0.88)                                 │
│                                                      │
│ [Mark Helpful] [Mark Unhelpful] [Edit] [Delete]     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- View full bullet content
- Show confidence and helpfulness scores
- Link to source traces that generated this bullet
- Show similar bullets (potential duplicates)
- Manual curation actions (mark helpful/unhelpful)
- Edit bullet content
- Delete bullet

#### 3.3 Curation Queue

```
┌─────────────────────────────────────────────────────┐
│ Pending Curation (12 new bullets)                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 🆕 "check status intent often needs clarification"  │
│    From: user_interpret | Confidence: 0.65          │
│    [Approve] [Edit] [Reject]                        │
│                                                      │
│ 🆕 "frustrated users need empathetic responses"     │
│    From: user_interpret | Confidence: 0.82          │
│    [Approve] [Edit] [Reject]                        │
│                                                      │
│ ... (10 more pending bullets)                        │
│                                                      │
│ [Approve All] [Review Individually]                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Show pending bullets from latest reflection
- Quick approve/reject buttons
- Edit before approving
- Batch actions (approve all, reject all)
- Sort by confidence, agent, or date

---

### 4. Analytics Tab

**Purpose**: High-level insights into ACE system effectiveness

#### 4.1 Learning Progress

```
┌─────────────────────────────────────────────────────┐
│ ACE Learning Progress (Last 30 Days)                │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Total Traces Generated: 3,241                        │
│ Delta Items Created: 287                             │
│ Playbook Bullets Added: 147                          │
│ Playbook Bullets Pruned: 23                          │
│                                                      │
│ [Chart: Traces over time (line graph)]              │
│ [Chart: Success rate over time (line graph)]        │
│ [Chart: Playbook growth over time (line graph)]     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Time-series charts (Plotly or Altair)
- Trend analysis (improving/stable/declining)
- Compare agents side-by-side
- Export charts as PNG

#### 4.2 Agent Comparison

```
┌─────────────────────────────────────────────────────┐
│ Agent Performance Comparison                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [Chart: Radar chart comparing agents]               │
│                                                      │
│         Success Rate                                 │
│              ▲                                       │
│              │                                       │
│    Traces ──●── Speed                               │
│              │                                       │
│         Playbook Size                                │
│                                                      │
│ Legend:                                              │
│ ─── user_interpret (highest performing)             │
│ ─── assistant (good performance)                    │
│ ─── code-searcher (moderate performance)            │
│ ─── code_developer (needs improvement)              │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Radar/spider chart for multi-dimensional comparison
- Select agents to compare
- Highlight outliers (best/worst performers)
- Export comparison data

---

## Technical Implementation

### Stack

```python
# Core
streamlit==1.32.0       # Web framework
python-dotenv==1.0.0    # .env file management

# Visualization
plotly==5.19.0          # Interactive charts
altair==5.2.0           # Alternative charting

# Data
pandas==2.2.0           # Data manipulation
numpy==1.26.0           # Numerical operations

# ACE Integration
# (use existing ACE modules)
```

### File Structure

```
coffee_maker/
├── streamlit_app/
│   ├── __init__.py
│   ├── app.py                      # Main Streamlit app
│   ├── pages/
│   │   ├── 1_Configuration.py      # Config tab
│   │   ├── 2_Monitor.py            # Monitor tab
│   │   ├── 3_Playbooks.py          # Playbook tab
│   │   └── 4_Analytics.py          # Analytics tab
│   ├── components/
│   │   ├── agent_toggle.py         # Reusable agent toggle widget
│   │   ├── trace_card.py           # Trace display card
│   │   ├── playbook_tree.py        # Playbook tree view
│   │   └── charts.py               # Chart components
│   └── utils/
│       ├── env_manager.py          # .env file read/write
│       ├── trace_loader.py         # Load traces from filesystem
│       ├── playbook_loader.py      # Load playbooks
│       └── realtime.py             # Real-time updates (polling/WebSocket)
│
├── autonomous/ace/
│   └── api.py                      # NEW: API layer for Streamlit
│
└── cli/
    └── streamlit_cli.py            # CLI command: `coffee-maker ace-ui`
```

### API Layer

```python
# coffee_maker/autonomous/ace/api.py
"""API layer for Streamlit app to interact with ACE framework."""

from typing import Dict, List, Any
from pathlib import Path
import json

class ACEApi:
    """API for Streamlit app to interact with ACE."""

    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get ACE status for all agents."""
        pass

    def enable_agent(self, agent_name: str) -> bool:
        """Enable ACE for specific agent."""
        pass

    def disable_agent(self, agent_name: str) -> bool:
        """Disable ACE for specific agent."""
        pass

    def get_traces(self, agent: str = None, date: str = None) -> List[Dict]:
        """Get traces (optionally filtered)."""
        pass

    def get_playbook(self, agent_name: str) -> Dict[str, Any]:
        """Get playbook for agent."""
        pass

    def update_bullet(self, agent_name: str, bullet_id: str, action: str) -> bool:
        """Update bullet (mark helpful/unhelpful, edit, delete)."""
        pass

    def run_reflector(self, agent_name: str = None) -> Dict[str, Any]:
        """Manually trigger reflector."""
        pass

    def run_curator(self, agent_name: str = None) -> Dict[str, Any]:
        """Manually trigger curator."""
        pass

    def get_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get ACE metrics for analytics."""
        pass
```

### CLI Command

```bash
# Launch Streamlit app
poetry run coffee-maker ace-ui

# Or with options
poetry run coffee-maker ace-ui --port 8501 --reload
```

---

## Development Phases

### Phase 1: Basic Configuration (1-2 days)
- ✅ Streamlit app structure
- ✅ Configuration tab with agent toggles
- ✅ .env file read/write
- ✅ CLI command to launch app

### Phase 2: Monitoring (2-3 days)
- ✅ Trace loader
- ✅ Live trace feed (polling)
- ✅ Agent performance dashboard
- ✅ Reflection status

### Phase 3: Playbook Management (2-3 days)
- ✅ Playbook browser
- ✅ Bullet detail view
- ✅ Curation queue
- ✅ Manual curation actions

### Phase 4: Analytics (1-2 days)
- ✅ Time-series charts
- ✅ Agent comparison
- ✅ Export capabilities

### Phase 5: Polish & Testing (1-2 days)
- ✅ UI/UX refinement
- ✅ Error handling
- ✅ Documentation
- ✅ Integration tests

**Total Estimated Time**: 7-12 days

---

## User Workflows

### Workflow 1: Enable ACE for New Agent

1. Open Streamlit app (`coffee-maker ace-ui`)
2. Navigate to Configuration tab
3. Find agent in list (e.g., "my_new_agent")
4. Click [Enable] button
5. See confirmation: "✅ ACE enabled for my_new_agent"
6. Check Monitor tab to see traces start appearing

### Workflow 2: Review Agent Performance

1. Open Monitor tab
2. Select agent from dropdown (e.g., "user_interpret")
3. View success rate, trace count, avg duration
4. Click [View Details] on specific trace
5. Inspect trace JSON to debug issues

### Workflow 3: Curate Playbook

1. Open Playbook tab
2. Select agent (e.g., "assistant")
3. Expand category (e.g., "Query Handling")
4. Click on bullet to view details
5. Review helpfulness scores
6. Click [Mark Helpful] or [Mark Unhelpful]
7. Save changes (auto-saves)

### Workflow 4: Monitor Learning Progress

1. Open Analytics tab
2. View "Learning Progress" chart
3. See traces increase over time
4. See playbook size grow
5. Compare success rates across agents
6. Export chart for reporting

---

## Security Considerations

1. **Authentication**: Add login (Streamlit auth or OAuth)
2. **.env Security**: Never display API keys in UI
3. **File Access**: Validate file paths (no directory traversal)
4. **Input Validation**: Sanitize all user inputs
5. **Read-Only Mode**: Option to launch in read-only mode (no .env writes)

---

## Future Enhancements

1. **Real-Time Streaming**: WebSocket for live trace feed (vs. polling)
2. **A/B Testing**: Compare playbook versions side-by-side
3. **Playbook Versioning**: Git-like version control for playbooks
4. **Agent Chat**: Test agents directly from UI (interactive sandbox)
5. **Export/Import**: Backup and restore entire ACE configuration
6. **Alerts**: Email/Slack notifications for low success rates
7. **Multi-User**: Team collaboration on playbook curation
8. **Mobile**: Responsive design for mobile monitoring

---

## Success Metrics

The Streamlit app is successful if:

1. ✅ **Configuration Time**: <30 seconds to enable/disable ACE per agent
2. ✅ **Trace Visibility**: See traces within 5 seconds of generation
3. ✅ **Playbook Inspection**: Browse 150-bullet playbook in <10 seconds
4. ✅ **Curation Speed**: Review and approve/reject bullet in <5 seconds
5. ✅ **User Satisfaction**: "This makes ACE 10x easier to use"

---

## Related Documentation

- [ACE Framework Guide](ACE_FRAMEWORK_GUIDE.md)
- [ACE Automatic Integration](ACE_AUTOMATIC_INTEGRATION.md)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## Summary

The Streamlit ACE Configuration & Monitoring app will provide:

1. ✅ **Visual Configuration**: No more manual .env editing
2. ✅ **Real-Time Monitoring**: See what agents are learning
3. ✅ **Playbook Management**: Interactive curation interface
4. ✅ **Analytics**: Understand ACE effectiveness
5. ✅ **User-Friendly**: Non-technical users can manage ACE

**This is the NEXT PRIORITY** after ACE framework full implementation! 🚀
