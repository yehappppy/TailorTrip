import json
from typing import Dict, List, Optional, Union, Any
import requests
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
from requests.exceptions import RequestException

class Role(Enum):
    """
    Enumeration for message roles
    """
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class MCPConfig:
    """
    MCP Protocol Core Configuration
    """
    model_endpoint: str  # Model API endpoint (e.g., "https://api.openai.com/v1")
    protocol_version: str = "mcp-v1.0"
    context_window: int = 8192  # Context window size (tokens)
    default_headers: Optional[Dict[str, str]] = None  # Custom request headers
    timeout: int = 30  # Request timeout in seconds
    max_retries: int = 3  # Maximum number of retries for failed requests
    
    def __post_init__(self):
        if not self.model_endpoint.startswith(('http://', 'https://')):
            raise ValueError("Model endpoint must start with http:// or https://")

class MCPError(Exception):
    """Custom exception for MCP-related errors"""
    pass

class MCPToolbox:
    def __init__(self, config: MCPConfig):
        self.config = config
        self._session = self._initialize_session()
        self.logger = logging.getLogger(__name__)

    def _initialize_session(self) -> requests.Session:
        """
        Initialize HTTP session with configuration
        """
        session = requests.Session()
        headers = {
            "Content-Type": "application/json",
            "MCP-Protocol": self.config.protocol_version,
            "User-Agent": f"MCPToolbox/{self.config.protocol_version}",
            **(self.config.default_headers or {})
        }
        session.headers.update(headers)
        return session

    async def _send_mcp_request(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Send MCP protocol formatted request with error handling and retries
        """
        payload = {
            "model": self.config.model_endpoint,
            "messages": self._format_mcp_messages(messages),
            "context_window": self.config.context_window,
            "temperature": temperature,
            "timestamp": datetime.utcnow().isoformat(),
            **({"tools": tools} if tools else {})
        }
        
        for attempt in range(self.config.max_retries):
            try:
                response = self._session.post(
                    f"{self.config.model_endpoint}/chat/completions",
                    json=payload,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise MCPError(f"Failed to complete request after {self.config.max_retries} attempts") from e

    @staticmethod
    def _format_mcp_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages according to MCP protocol (supports multi-role context)
        Format: [{"role": "user|system|assistant", "content": str, "meta": Optional[Dict]}]
        """
        formatted_messages = []
        for msg in messages:
            if not isinstance(msg.get("role"), Role):
                try:
                    role = Role(msg["role"])
                except ValueError:
                    raise MCPError(f"Invalid role: {msg['role']}")
            
            formatted_msg = {
                "role": role.value,
                "content": msg["content"],
                **({"meta": msg["meta"]} if "meta" in msg else {})
            }
            formatted_messages.append(formatted_msg)
        return formatted_messages

    async def chat_completion(
        self,
        prompt: str,
        context: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Basic chat completion with context management
        """
        messages = [{"role": Role.USER, "content": prompt}]
        if context:
            messages = context + messages
            
        response = await self._send_mcp_request(messages, tools, temperature)
        return response["choices"][0]["message"]["content"]

    async def tool_enhanced_query(
        self,
        query: str,
        available_tools: List[Dict[str, Any]],
        max_tool_calls: int = 3
    ) -> Union[str, Dict[str, Any]]:
        """
        Tool-enhanced query with automatic tool selection and execution
        """
        messages = [{
            "role": Role.USER,
            "content": f"Answer this query using tools if needed: {query}"
        }]
        
        tool_call_count = 0
        while tool_call_count < max_tool_calls:
            response = await self._send_mcp_request(messages, tools=available_tools)
            msg = response["choices"][0]["message"]
            
            if "tool_calls" in msg:
                tool_results = await self._execute_tools(msg["tool_calls"])
                messages.append({
                    "role": Role.TOOL,
                    "content": json.dumps(tool_results),
                    "meta": {"tool_call_index": tool_call_count}
                })
                tool_call_count += 1
            else:
                return msg["content"]
        
        return {"error": "Maximum tool calls exceeded", "tool_call_count": tool_call_count}

    async def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute tool calls with validation and error handling
        """
        results = []
        for call in tool_calls:
            try:
                tool_name = call["name"]
                args = json.loads(call["arguments"])
                
                result = await self._execute_single_tool(tool_name, args)
                results.append({
                    "tool": tool_name,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Tool execution failed: {str(e)}")
                results.append({
                    "tool": call.get("name", "unknown"),
                    "error": str(e)
                })
        
        return results

    async def _execute_single_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a single tool with proper validation and execution
        """
        # Implement tool execution logic here
        raise NotImplementedError("Tool execution must be implemented by subclasses")

    async def compress_context(
        self,
        context: List[Dict[str, Any]],
        target_size: int,
        preservation_priority: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Context compression with preservation priorities and validation
        """
        if not context:
            return []
            
        if preservation_priority is None:
            preservation_priority = ["system", "user"]
            
        summary_prompt = (
            f"Compress the following context to under {target_size} tokens while "
            f"prioritizing {', '.join(preservation_priority)} messages:\n{json.dumps(context)}"
        )
        
        compressed = await self.chat_completion(summary_prompt)
        return [{
            "role": Role.SYSTEM,
            "content": compressed,
            "meta": {
                "compression_timestamp": datetime.utcnow().isoformat(),
                "original_length": len(context)
            }
        }]