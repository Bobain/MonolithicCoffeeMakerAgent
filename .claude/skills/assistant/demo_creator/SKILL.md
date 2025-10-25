---
name: demo-creator
version: 1.0.0
agent: assistant
scope: agent-specific
description: >
  Automated demo creation: use Puppeteer MCP to interact with app,
  capture screenshots, generate narration, create visual demo.

triggers:
  - "create demo"
  - "show how feature works"
  - "visual demonstration"
  - "generate demo video"

requires:
  - puppeteer (MCP)

inputs:
  feature_name:
    type: string
    required: true
    description: Feature to demonstrate

  url:
    type: string
    required: false
    description: App URL (default: http://localhost:8000)

  steps:
    type: list[string]
    required: false
    description: Demo steps (auto-generated if not provided)

outputs:
  screenshots:
    type: list[string]
    description: List of screenshot paths

  narration:
    type: string
    description: Demo narration text

  demo_path:
    type: string
    description: Path to demo markdown file

author: architect agent
created: 2025-10-19
---

# Demo Creator Skill

Automated demo creation for assistant.

## Workflow

1. **Plan Demo**: Define interaction steps
2. **Launch Browser**: Start Puppeteer session
3. **Execute Steps**: Interact with app, capture screenshots
4. **Generate Narration**: Create demo narration text
5. **Compile Demo**: Create markdown with screenshots + narration
6. **Save Demo**: Write to docs/demos/

## Expected Time Savings

- **Manual Demo Creation**: 45 minutes
- **With Skill**: 10 minutes
- **Time Saved**: 78% reduction
