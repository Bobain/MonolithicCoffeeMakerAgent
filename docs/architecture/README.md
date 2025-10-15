# Architecture Documentation

This directory contains architectural decisions, technical specifications, and implementation guidelines created by the architect agent.

## Directory Structure

- `specs/` - Detailed technical specifications for features and systems
- `decisions/` - Architectural Decision Records (ADRs) documenting key decisions
- `guidelines/` - Implementation guidelines for code_developer

## Workflow

1. User requests feature or architectural change
2. architect analyzes requirements and creates specification in `specs/`
3. architect documents decisions in `decisions/` (ADRs)
4. architect provides guidelines in `guidelines/`
5. code_developer reads specifications and implements
6. architect reviews implementation

## Ownership

**Owner**: architect (read/write)
**Others**: code_developer (read-only), project_manager (read-only)
