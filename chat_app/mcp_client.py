from contextlib import AsyncExitStack
from dotenv import load_dotenv
from typing import Optional 
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio

load_dotenv('../.env')
MCP_SERVER_PATH = '../mcp_backend/mcp_server.py'


class MCPClient:
    def __init__(self, openai_key: str, mcp_server_path: str, model: str = "gpt-4.1-nano"):
        self.session: Optional[ClientSession] = None 
        self.stack = AsyncExitStack()
        self.server_file = mcp_server_path
        self.model = ChatOpenAI(model=model, api_key=openai_key)
        self.prompt = """You are a helpful and knowledgeable real estate assistant. 
The system has provided you with tools to access a database containing some real estate data from Zillow describing current and historical market trends. 
Call the tools to answer the user's questions. 
Describe the tables to know which relevant tables are valid to inspect. 
Inspect the tables for more information if needed to answer the user's questions. 
Show your step by step train of thought in answering the user's questions. 
"""


    async def connect_to_mcp_server(self) -> None:
        if not self.server_file.endswith('.py'):
            raise ValueError("Server script must be a .py file")

        server_params = StdioServerParameters(
            command="python",
            args=[self.server_file],
            env=None
        )
        self.receive_stream, self.send_stream = await self.stack.enter_async_context(stdio_client(server_params))
        self.session = await self.stack.enter_async_context(ClientSession(self.receive_stream, self.send_stream))
        await self.session.initialize()

        tools = await load_mcp_tools(self.session)
        print(f"tools: {[ (tool.name, tool.description) for tool in tools ]}")

        self.agent = create_react_agent(
            model=self.model, 
            tools=tools,
            prompt=self.prompt
        )


    async def process_query(self, query: str = None) -> dict[str, any]: 
        agent_response = await self.agent.ainvoke({"messages": query})
        return agent_response


    async def cleanup(self):
        await self.stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_mcp_server(MCP_SERVER_PATH)
        gen = await client.process_query("what's (3 + 5) x 12?")
        print(gen)
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())