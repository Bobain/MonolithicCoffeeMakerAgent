# Proactive Refactoring Analysis - Scripts

This directory contains the entry point scripts for the proactive-refactoring-analysis skill.

## Scripts

### `refactoring_analysis.py`

Main entry point for running proactive refactoring analysis.

**Usage:**
```bash
# From project root
python .claude/skills/proactive-refactoring-analysis/scripts/refactoring_analysis.py

# Or directly
cd .claude/skills/proactive-refactoring-analysis/scripts
./refactoring_analysis.py
```

**Options:**
- `--codebase-path PATH`: Path to codebase root (default: current directory)
- `--output-dir DIR`: Output directory for reports (default: codebase_path/evidence)
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Analyze current codebase
python refactoring_analysis.py

# Analyze specific codebase with verbose output
python refactoring_analysis.py --codebase-path /path/to/project -v

# Save report to custom directory
python refactoring_analysis.py --output-dir /path/to/reports
```

## Output

Reports are saved to:
```
evidence/refactoring-analysis-YYYYMMDD-HHMMSS.md
```

Each report contains:
- Executive summary with code health score
- Top refactoring recommendations (sorted by ROI)
- Detailed metrics (complexity, duplication, coverage, dependencies)
- Trend analysis (week-over-week comparison)
- Next steps for project_manager, architect, and code_developer

## Implementation

The actual analysis logic is implemented in:
```
coffee_maker/skills/refactoring_analysis/proactive_refactoring_analysis.py
```

This script directory provides a convenient entry point that:
1. Parses command-line arguments
2. Validates inputs
3. Calls the main analysis implementation
4. Formats and displays results
5. Handles errors gracefully

## Integration

This skill is designed to be:
- **Called manually** by users via command line
- **Invoked automatically** by architect agent (weekly schedule)
- **Integrated** into CI/CD pipelines (future enhancement)

## Performance

- **Execution Time**: <5 minutes for ~50,000 LOC
- **Memory Usage**: <500 MB
- **CPU Usage**: Low (I/O bound)

## Dependencies

Required Python packages (installed via poetry):
- `radon` - Code complexity analysis
- `pytest-cov` - Test coverage analysis
- `autoflake` - Unused import detection

## Testing

Run tests for this skill:
```bash
pytest tests/unit/test_proactive_refactoring_analyzer.py -v
```

## Troubleshooting

### Script not executable
```bash
chmod +x refactoring_analysis.py
```

### Module not found errors
Ensure you're running from project root or the script directory has been added to PYTHONPATH.

### Analysis takes too long
- Check if test suite is running (can take 3-5 minutes)
- Consider excluding large generated files
- Increase timeout values if needed

## Version

**Version**: 1.0.0
**Last Updated**: 2025-10-19
**Status**: Production Ready ✅
