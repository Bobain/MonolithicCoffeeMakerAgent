from dotenv import load_dotenv
from mcp.client.stdio import StdioServerParameters
from smolagents import CodeAgent, InferenceClientModel, ToolCollection

load_dotenv()

model = InferenceClientModel()

server_parameters = StdioServerParameters(command="poetry", args=["run", "python", "server.py"])

input = "Quel température en celsius fait il à Conpenhague???"

with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
    print("Here are the tools on the MCP server we connected to:")
    print("\n".join(f"{tool.name}: {tool.description}" for tool in tool_collection.tools))
    agent = CodeAgent(tools=[*tool_collection.tools], model=model)
    agent.run(input)
