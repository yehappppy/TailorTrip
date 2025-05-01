import asyncio
import logging
from typing import Any, Optional
from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import AsyncExitStack
from langchain_core.tools import BaseTool
from pydantic import create_model, Field

logger = logging.getLogger(__name__)

class AmapMCPServer:
    def __init__(self, url: str):
        self.url = url
        self._exit_stack: Optional[AsyncExitStack] = None
        self.session: Optional[ClientSession] = None
        self.tool_names = {}
        self._lock = asyncio.Lock()

    async def connect_server(self):
        """Connect to the MCP server and retrieve the list of tool_names."""
        async with self._lock:
            logger.info(f"Connecting to: {self.url}")
            self._exit_stack = AsyncExitStack()
            sse_cm = sse_client(self.url)
            streams = await self._exit_stack.enter_async_context(sse_cm)
            logger.info("SSE stream acquired.")
            session_cm = ClientSession(streams[0], streams[1])
            self.session = await self._exit_stack.enter_async_context(session_cm)
            logger.info("ClientSession created.")
            await self.session.initialize()
            logger.info("Session initialized.")
            response = await self.session.list_tools()
            self.tool_names = {tool.name: tool for tool in response.tools}
            logger.info(f"Retrieved {len(self.tool_names)} tools:")
            for name, tool in self.tool_names.items():
                logger.info(f"  - {name}: {tool.description}")

    async def disconnect(self):
        """Close the session and connection."""
        async with self._lock:
            if self._exit_stack:
                await self._exit_stack.aclose()
                logger.info("Disconnected from server.")

    # def get_tool_schema(self, tool_name: str):
    #     """Return the input schema for a specified tool."""
    #     if tool_name in self.tool_names:
    #         return self.tool_names[tool_name].inputSchema
    #     raise ValueError(f"Tool '{tool_name}' not found.")

    async def call_tool(self, tool_name: str, arguments: dict):
        """Execute a tool with the given arguments."""
        if tool_name not in self.tool_names:
            raise ValueError(f"Tool '{tool_name}' not found.")
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_server first.")
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            logger.info(error_msg)
            return error_msg

class AmapToolWrapper(BaseTool):
    """Wrapper for Amap tools to integrate with LangChain. MCP Tools are not compatible with LangChain's tool interface, so we need to create a wrapper."""
    session: Any  # MCP ClientSession

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Asynchronous calls only")

    async def _arun(self, **kwargs: Any) -> Any:
        return await self.session.call_tool(self.name, kwargs)

class AmapTools(AmapMCPServer):
    def __init__(self, url: str):
        super().__init__(url)
        self.tools = []
    
    async def setup_tools(self):
        """Set up the tools for the AmapMCPServer."""
        type_mapping = {
            'string': str,
            'number': float,
            'integer': int,
            'array': list,
            'object': dict,
            'boolean': bool
        }
        
        async with self._lock:
            for name, meta in self.tool_names.items():
                fields = {}
                for param, props in meta.inputSchema["properties"].items():
                    field_type = type_mapping[props.get("type")]
                    description = props.get("description", "")
                    default_value = ... if param in meta.inputSchema.get("required", []) else None
                    fields[param] = (field_type, Field(default=default_value, description=description))
                InputModel = create_model(f"{name}Input", **fields)
                self.tools.append(AmapToolWrapper(
                    name=name,
                    description=meta.description,
                    args_schema=InputModel,
                    session=self.session
                ))