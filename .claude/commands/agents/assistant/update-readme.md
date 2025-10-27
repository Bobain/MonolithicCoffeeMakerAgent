---
command: update-readme
agent: assistant
action: update_readme_file
tables: [roadmap_priority, specs_specification]
tools: [file_system, llm]
duration: 15m
---

## Purpose

Keep README files synchronized with latest features from roadmap and specs.

## Input Parameters

```yaml
README_PATH:
  type: string
  description: Path to README file to update
  example: "README.md"

SECTION:
  type: string
  optional: true
  description: Specific section to update (optional)
  example: "Features"

INCLUDE_PRIORITIES:
  type: boolean
  optional: true
  default: true
  description: Include completed priorities

INCLUDE_LINKS:
  type: boolean
  optional: true
  default: true
  description: Include cross-references to specs
```

## Database Operations

### SELECT roadmap_priority

```sql
SELECT name, status, description FROM roadmap_priority
WHERE status IN ('completed', 'in_progress')
ORDER BY sequence ASC
```

### SELECT specs_specification

```sql
SELECT id, title, status FROM specs_specification LIMIT 20
```

## Success Criteria

- README file updated
- Latest features included
- Links validated
- Formatting preserved
- File written successfully

## Output Format

```json
{
  "success": true,
  "readme_path": "README.md",
  "sections_updated": ["Features", "Getting Started"],
  "features_added": 5,
  "links_updated": 12,
  "message": "README updated with latest features"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| File not found | README_PATH doesn't exist | Create new file |
| Permission denied | Can't write to path | Check permissions |
| Update failed | Parsing error | Use backup and retry |

## Examples

### Example 1: Update All Sections

```bash
/agents:assistant:update-readme \
  README_PATH="README.md" \
  INCLUDE_PRIORITIES=true \
  INCLUDE_LINKS=true
```

### Example 2: Update Features Section

```bash
/agents:assistant:update-readme \
  README_PATH="README.md" \
  SECTION="Features" \
  INCLUDE_PRIORITIES=true
```

## Implementation Notes

- Read README file and parse sections
- Query roadmap_priority for completed/in_progress items
- Query specs_specification for technical details
- Update Features section with latest priorities
- Update Architecture/Design sections with relevant specs
- Preserve custom sections (e.g., Contributing, License)
- Validate all markdown links
- Create backup before updating
- Use LLM to enhance and format content
