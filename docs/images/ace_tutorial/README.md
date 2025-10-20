# ACE Tutorial Screenshots

This directory contains screenshots and visual assets for the ACE Console Demo Tutorial.

## Screenshot Requirements

Screenshots should demonstrate:

1. **Generator Initialization** - Python console showing Generator import and initialization
2. **File Operation Interception** - Example of `intercept_file_operation()` call with results
3. **Delegation in Action** - Console output showing ownership violation and auto-delegation
4. **Trace Retrieval** - Output from `get_delegation_traces()` showing trace details
5. **Statistics Display** - Output from `get_delegation_stats()` showing metrics
6. **Database Query** - SQLite query results showing generator_traces table
7. **Context Loading** - `load_agent_context()` output showing loaded files
8. **Search Monitoring** - Warning message when unexpected search detected

## Screenshot Naming Convention

- `01_generator_init.png` - Generator initialization
- `02_file_operation.png` - File operation interception
- `03_delegation_output.png` - Delegation console output
- `04_traces_list.png` - Trace retrieval output
- `05_statistics.png` - Statistics display
- `06_database_query.png` - Database query results
- `07_context_loading.png` - Context loading output
- `08_search_monitoring.png` - Search monitoring warning

## Creating Screenshots

To create screenshots for the tutorial:

```bash
# 1. Start Python shell
poetry shell
python

# 2. Run example commands from ACE_CONSOLE_DEMO_TUTORIAL.md
# 3. Take screenshots using:
#    - macOS: Cmd+Shift+4 (select area)
#    - Linux: gnome-screenshot -a
#    - Windows: Win+Shift+S

# 4. Save screenshots to this directory with proper naming
```

## Tools for Screenshot Annotation

- **macOS**: Preview (built-in)
- **Linux**: GIMP, Shutter
- **Windows**: Paint, Greenshot
- **Cross-platform**: Flameshot

## Screenshot Standards

- **Format**: PNG (lossless)
- **Resolution**: At least 1280x720
- **Text**: Clear, readable terminal font (14pt+)
- **Annotations**: Use arrows/boxes to highlight key points
- **Background**: Dark terminal theme recommended for consistency

---

**Note**: Screenshots can be taken using real terminal sessions or using Puppeteer MCP for web-based demonstrations if a web UI is developed.
