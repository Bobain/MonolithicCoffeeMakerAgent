# PRIORITY 4.1: Puppeteer MCP Server Integration

**Status**: 📝 Planned
**Priority**: High
**Created**: 2025-10-12
**Assignee**: code_developer
**Depends on**: PRIORITY 4 (Developer Status Dashboard)

---

## Overview

Integrate the Puppeteer MCP (Model Context Protocol) server to enable Coffee Maker's autonomous agents (code_developer, project_manager, assistant) to interact with web browsers and see visual output through screenshots, page navigation, and DOM interaction.

**User Story**:
> "I want the code_developer, project_manager, and assistant agents to see their output through a browser interface using the Puppeteer MCP server."

---

## Goals

### Primary Goals
1. **Browser Automation**: Enable agents to navigate web pages programmatically
2. **Visual Feedback**: Allow agents to take screenshots and see rendered output
3. **Interactive Testing**: Enable agents to test web applications and UIs
4. **Documentation**: Agents can capture visual documentation of their work

### Success Criteria
- ✅ Puppeteer MCP server running and accessible to Coffee Maker agents
- ✅ Agents can navigate to URLs and capture screenshots
- ✅ Agents can interact with web pages (click, fill forms, execute JS)
- ✅ Integration works with both Claude CLI and API modes
- ✅ Documented usage examples for all agents

---

## Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│              Coffee Maker Agents                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐      │
│  │code_developer│  │project_manager│  │  assistant │      │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘      │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│                    ┌──────▼──────┐                        │
│                    │ MCP Client   │                        │
│                    │  Wrapper     │                        │
│                    └──────┬───────┘                        │
└───────────────────────────┼────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Puppeteer MCP  │
                    │     Server      │
                    └───────┬─────────┘
                            │
                    ┌───────▼─────────┐
                    │   Puppeteer     │
                    │  (Chromium)     │
                    └─────────────────┘
```

### Integration Approaches

We'll implement **two approaches** for maximum flexibility:

#### Approach 1: Claude Desktop Integration (Interactive Use)
- **When**: User interacts with agents through Claude Desktop app
- **How**: Configure `claude_desktop_config.json` with Puppeteer MCP server
- **Benefit**: Native MCP support, seamless integration

#### Approach 2: Programmatic Integration (Autonomous Use)
- **When**: Autonomous agents run via `code-developer` daemon
- **How**: Python MCP client connects to Puppeteer server directly
- **Benefit**: Works in headless mode, no UI required

---

## Technical Specification

### 1. Puppeteer MCP Server Setup

#### 1.1 Installation

**NPX-based (Recommended)**:
```bash
# Test server availability
npx -y @modelcontextprotocol/server-puppeteer
```

**Docker-based (Alternative)**:
```bash
# Use pre-built Docker image
docker run -i --rm mcp/puppeteer
```

#### 1.2 Configuration

**Claude Desktop Configuration**:

File: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "darkMode": "dark",
  "scale": 0,
  "locale": "fr-FR",
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
      "env": {
        "PUPPETEER_LAUNCH_OPTIONS": "{\"headless\": true}"
      }
    }
  }
}
```

---

## Implementation Plan

### Phase 1: Setup & Configuration (2 hours)
1. Test Node.js and npx availability
2. Test Puppeteer MCP server launch
3. Configure Claude Desktop with MCP server
4. Verify server appears in Claude Desktop

### Phase 2: CLI Tool Development (4 hours)
1. Create `coffee_maker mcp test` command
2. Create `coffee_maker mcp browser` command for testing
3. Document usage

### Phase 3: Documentation & Testing (2 hours)
1. Write usage guide
2. Create examples
3. Test with all agents

---

## Quick Start

### Step 1: Install Dependencies

```bash
# Node.js should already be installed on macOS
node --version  # Should be >= 16.x

# Test npx
npx --version
```

### Step 2: Configure Claude Desktop

```bash
# Backup existing config
cp ~/Library/Application\ Support/Claude/config.json ~/Library/Application\ Support/Claude/config.json.backup

# Add MCP server configuration (see Configuration section above)
```

### Step 3: Test Integration

```bash
# Test server starts
npx -y @modelcontextprotocol/server-puppeteer

# Test with Claude Desktop
# Open Claude Desktop and check for Puppeteer tools
```

---

## Usage Examples

### Example 1: Screenshot a Website

```bash
# Using Claude Desktop with Puppeteer MCP
"Navigate to https://example.com and take a screenshot"
```

### Example 2: Test Web Application

```bash
# code_developer daemon use case
"Test the new login page at http://localhost:3000/login by:
1. Taking a screenshot of the initial state
2. Filling in test credentials
3. Clicking submit
4. Taking a screenshot of the result"
```

### Example 3: Visual Documentation

```bash
# project_manager use case
"Document the new dashboard feature by capturing screenshots of:
1. The main dashboard view
2. The analytics panel
3. The settings page
Save screenshots to docs/screenshots/"
```

---

## Dependencies

### External Dependencies
- **Node.js**: >= 16.x (already installed on macOS)
- **@modelcontextprotocol/server-puppeteer**: npm package (installed on-demand via npx)
- **Puppeteer**: Auto-installed by MCP server
- **Chromium**: Auto-installed by Puppeteer

### System Requirements
- **macOS**: 10.13 or later
- **Disk Space**: ~300MB for Chromium
- **RAM**: 2GB+ recommended for browser automation

---

## Testing Strategy

### Manual Testing

**Test 1: Server Launch**
```bash
npx -y @modelcontextprotocol/server-puppeteer
# Should start without errors
```

**Test 2: Claude Desktop Integration**
1. Configure claude_desktop_config.json
2. Restart Claude Desktop
3. Check for Puppeteer tools in tool list
4. Test a simple navigation command

**Test 3: Screenshot Capture**
1. Navigate to a test page
2. Capture screenshot
3. Verify screenshot saved correctly

---

## Security Considerations

### Browser Sandboxing
- Puppeteer runs with sandboxing by default
- Only disable sandbox in trusted environments
- Use `--no-sandbox` flag with caution

### URL Validation
- Validate URLs before navigation
- Block access to private/internal IPs in production
- Implement allowlist for approved domains if needed

### Screenshot Privacy
- Don't capture pages with sensitive data
- Store screenshots in secure location
- Auto-cleanup old screenshots

---

## Performance Considerations

### Headless vs Headed Mode
- **Headless (default)**: Faster, lower resources
- **Headed**: Useful for debugging, slower

### Resource Management
- Chromium uses ~100-200MB RAM per instance
- Close browser instances when done
- Limit concurrent browser sessions

---

## Troubleshooting

### Issue: npx command not found
**Solution**: Install Node.js from https://nodejs.org/

### Issue: Server fails to start
**Solution**: Check Node.js version, ensure >= 16.x

### Issue: Chromium download fails
**Solution**: Check internet connection, check disk space

### Issue: Screenshots are blank
**Solution**: Wait for page load before capturing

---

## Documentation

### Files to Create
1. `docs/PUPPETEER_MCP_GUIDE.md` - User guide
2. `docs/MCP_ARCHITECTURE.md` - Architecture overview
3. `examples/puppeteer_demo.md` - Usage examples

---

## Success Metrics

### Technical Metrics
- Server startup time: <5 seconds
- Navigation time: <3 seconds per page
- Screenshot capture: <2 seconds

### Usage Metrics
- Number of browser sessions per day
- Most common commands
- Error rate

---

## Future Enhancements

1. **Video Recording**: Capture agent actions as video
2. **Network Mocking**: Mock API responses for testing
3. **Performance Testing**: Measure page load times
4. **Multi-Browser**: Support Firefox, Safari
5. **Visual Regression**: Compare screenshots over time

---

## References

- **Puppeteer MCP Server**: https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Puppeteer Docs**: https://pptr.dev/
- **Claude Desktop MCP**: https://docs.anthropic.com/claude/docs/mcp

---

## Implementation Status

**Phase 1**: Setup & Configuration
- [ ] Verify Node.js installation
- [ ] Test Puppeteer MCP server
- [ ] Configure Claude Desktop
- [ ] Verify integration

**Phase 2**: CLI Tools
- [ ] Create test commands
- [ ] Document usage
- [ ] Create examples

**Phase 3**: Testing
- [ ] Manual testing
- [ ] Document results
- [ ] Create user guide

---

**Next Step**: Begin Phase 1 - Setup & Configuration
**Estimated Time**: 2-4 hours total
