---
name: hello-world
version: 1.0.0
agent: shared
scope: shared
description: Simple example skill that demonstrates the Claude Skills infrastructure. Prints a greeting message based on provided context.
triggers:
  - hello world
  - test skill
  - example skill
requires: []
inputs:
  name:
    type: string
    required: false
    description: Name to greet
outputs:
  message:
    type: string
    description: Greeting message
author: code_developer
created: 2025-10-19
---

# Hello World Skill

Simple example skill for testing the Claude Skills infrastructure.

## Workflow

1. Read name from context (or use default "World")
2. Generate greeting message
3. Return message as output

## Expected Output

```json
{
  "message": "Hello, World!"
}
```
