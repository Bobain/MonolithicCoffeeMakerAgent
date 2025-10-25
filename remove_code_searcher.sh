#!/bin/bash
# Script to remove all code-searcher agent references
# Keeps code-searcher skills (code-forensics, security-audit)

echo "Removing code-searcher agent references..."
echo ""

# Find all files with code-searcher references (excluding skills directory and backups)
files=$(grep -rl "code-searcher\|CODE_SEARCHER" \
    --include="*.py" \
    --include="*.md" \
    . 2>/dev/null | \
    grep -v ".git/" | \
    grep -v "__pycache__" | \
    grep -v ".pyc" | \
    grep -v ".claude/skills/code-searcher/" | \
    grep -v "../MonolithicCoffeeMakerAgent_backups")

echo "Found $(echo "$files" | wc -l) files to process"
echo ""

# Process each file
for file in $files; do
    # Skip if file doesn't exist
    [ ! -f "$file" ] && continue

    # Count occurrences before
    before=$(grep -c "code-searcher\|CODE_SEARCHER" "$file" 2>/dev/null || echo "0")

    if [ "$before" -gt 0 ]; then
        echo "Processing: $file ($before references)"

        # Create backup
        cp "$file" "$file.tmp"

        # Replace references in comments/docs with notes about skills
        sed -i '' \
            -e 's/code-searcher agent/assistant agent (with code-forensics and security-audit skills)/g' \
            -e 's/code_searcher agent/assistant agent (with code-forensics and security-audit skills)/g' \
            -e 's/CODE_SEARCHER agent/ASSISTANT agent (with code-forensics and security-audit skills)/g' \
            "$file"

        # For Python code, replace enum references with ASSISTANT
        if [[ "$file" == *.py ]]; then
            sed -i '' \
                -e 's/AgentType\.CODE_SEARCHER/AgentType.ASSISTANT/g' \
                -e 's/"code-searcher"/"assistant"/g' \
                "$file"
        fi

        # Remove from lists/arrays where it's just listed as an agent
        sed -i '' \
            -e '/^[[:space:]]*[-*][[:space:]]*code-searcher[[:space:]]*$/d' \
            -e '/^[[:space:]]*code-searcher[[:space:]]*$/d' \
            "$file"

        # Count after
        after=$(grep -c "code-searcher\|CODE_SEARCHER" "$file" 2>/dev/null || echo "0")

        if [ "$after" -eq 0 ]; then
            rm "$file.tmp"
            echo "  ✅ All references removed"
        else
            echo "  ⚠️  $after references remain (may need manual review)"
            rm "$file.tmp"
        fi
    fi
done

echo ""
echo "✅ Bulk replacement complete"
echo ""
echo "Note: .claude/skills/code-searcher/ directory kept (skills still valid)"
