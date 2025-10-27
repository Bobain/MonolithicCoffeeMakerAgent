---
command: generate-docs
agent: assistant
action: generate_documentation
tables: [specs_specification, roadmap_priority]
tools: [file_system, llm]
duration: 20m
---

## Purpose

Auto-generate documentation from technical specs and code with cross-references and examples.

## Input Parameters

```yaml
SOURCE:
  type: string
  enum: [spec, code, both]
  description: Documentation source

TARGET_PATH:
  type: string
  description: Output documentation path
  example: "docs/generated/authentication.md"

SPEC_ID:
  type: string
  optional: true
  description: Spec ID if SOURCE=spec or both

INCLUDE_EXAMPLES:
  type: boolean
  optional: true
  default: true
  description: Include code examples

INCLUDE_API:
  type: boolean
  optional: true
  default: true
  description: Include API documentation
```

## Database Operations

### SELECT specs_specification

```sql
SELECT content FROM specs_specification WHERE id = ?
```

## Success Criteria

- Documentation generated in markdown
- Cross-references resolved
- Examples included
- File written to TARGET_PATH
- Formatting validated

## Output Format

```json
{
  "success": true,
  "generated_doc_path": "docs/generated/authentication.md",
  "word_count": 2450,
  "sections": 8,
  "cross_references": 12,
  "code_examples": 5,
  "message": "Documentation generated successfully"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Spec not found | Invalid SPEC_ID | List available specs |
| File write error | Permission denied | Check TARGET_PATH |
| Generation failed | LLM error | Retry up to 3 times |

## Examples

### Example 1: Generate from Spec

```bash
/agents:assistant:generate-docs \
  SOURCE="spec" \
  SPEC_ID="SPEC-115" \
  TARGET_PATH="docs/generated/authentication.md"
```

### Example 2: Generate from Code and Spec

```bash
/agents:assistant:generate-docs \
  SOURCE="both" \
  SPEC_ID="SPEC-115" \
  TARGET_PATH="docs/generated/authentication.md" \
  INCLUDE_EXAMPLES=true \
  INCLUDE_API=true
```

## Implementation Notes

- Read spec content from specs_specification table
- Use LLM to format and enhance documentation
- Include examples from code if SOURCE=code or both
- Generate table of contents
- Create cross-reference links
- Validate markdown syntax
- Save to TARGET_PATH (create directory if needed)
