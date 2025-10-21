# MCP Server Configurations

This directory contains Model Context Protocol (MCP) server configurations for the project.

## What is MCP?

MCP (Model Context Protocol) allows AI models to connect to external tools and services. Each JSON file in this directory configures an MCP server that provides specific capabilities to the AI agents.

## Current MCP Servers

### Puppeteer (`puppeteer.json`)

Provides browser automation capabilities:
- Navigate to URLs
- Capture screenshots
- Interact with web pages (click, fill forms, execute JavaScript)
- Test web applications
- Create visual documentation

**Usage in Claude Desktop**:
```
"Navigate to https://example.com and take a screenshot"
```

## Configuration Format

Each MCP server configuration follows this format:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": [
        "-y",
        "package-name"
      ],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

## Adding New MCP Servers

1. Create a new `.json` file in this directory
2. Follow the configuration format above
3. Restart Claude Desktop to load the new server
4. Test the server by trying to use its tools

## Project-scoped vs Global Configuration

**Project-scoped** (`.claude/mcp/*.json`):
- ✅ Only applies to this project
- ✅ Version controlled with git
- ✅ Shared with team
- ✅ Recommended approach

**Global** (`~/Library/Application Support/Claude/config.json`):
- ⚠️ Applies to all Claude Desktop sessions
- ⚠️ Not version controlled
- ⚠️ User-specific
- Use only for personal tools

## Available MCP Servers

Browse the official MCP servers repository:
https://github.com/modelcontextprotocol/servers

Popular servers:
- `@modelcontextprotocol/server-puppeteer` - Browser automation
- `@modelcontextprotocol/server-filesystem` - File operations
- `@modelcontextprotocol/server-github` - GitHub API integration
- `@modelcontextprotocol/server-postgres` - PostgreSQL database
- `chrome-devtools-mcp` - Chrome DevTools integration

## Troubleshooting

### Server not loading

1. Check JSON syntax (use a JSON validator)
2. Ensure `npx` is installed: `npx --version`
3. Restart Claude Desktop
4. Check Claude Desktop logs

### Command not found

Install Node.js from https://nodejs.org/ (includes npx)

### Server starts but tools don't work

1. Check server logs in Claude Desktop
2. Verify environment variables are set correctly
3. Test the underlying tool directly (e.g., `npx -y @modelcontextprotocol/server-puppeteer`)

## References

- MCP Specification: https://spec.modelcontextprotocol.io/
- MCP Servers: https://github.com/modelcontextprotocol/servers
- Claude Desktop MCP Docs: https://docs.anthropic.com/claude/docs/mcp
