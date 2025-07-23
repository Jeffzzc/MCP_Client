import asyncio
from autoagentsai.prebuilt import create_react_agent
from autoagentsai.client import MCPClient
# from langchain.agents import AgentExecutor, create_react_agent

async def main():
    mcp_client = MCPClient(
        {
            "math": {
                "command": "python",
                # Replace with absolute path to your math_server.py file
                "args": ["/Users/jeffzzc/code/autoagents/autoagentsai/Server/math_server.py"],
                "transport": "stdio",
                "description": "Perform mathematical calculations",
            },
            "weather": {
                # Ensure you start your weather server on port 8888
                "url": "http://127.0.0.1:8888",
                "transport": "streamable_http",
                "description": "Get current weather information for a location",
            }
        }
    )

    tools = mcp_client.get_tools()

    print("Available tools:", [tool.name for tool in tools])

    agent = create_react_agent("openai:gpt-4o", tools)

    # res = await agent.ainvoke({"input": "What is 1 + 6 / 9?"})

    res = await agent.ainvoke({"input": "What's the weather in San Francisco?"})

    print("Answer:", res["output"])

    print(tools)
    

if __name__ == "__main__":
    asyncio.run(main())

