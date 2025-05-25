from mcp.client.stdio import StdioServerParameters
from smolagents import ToolCollection

server_parameters = StdioServerParameters(command="poetry", args=["run", "python", "server.py"])

with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tools:
    print("\n".join(f"{tool.name}: {tool.description}" for tool in tools.tools))
