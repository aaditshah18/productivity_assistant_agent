import asyncio
import os
import json
from anthropic import Anthropic
from typing import Any, List, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Default level, can be configured higher in main.py


class MCPClient: # Renamed from MCPAgent
    """Client that uses MCP tools to interact with Calendar and Gmail."""
    
    def __init__(self):
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.mcp_sessions = {}
        self.messages = []
        
    async def initialize(self):
        """Initialize connections to MCP servers."""
        logger.info("Initializing MCP servers...")
        
        # Initialize Calendar MCP
        try:
            calendar_params = StdioServerParameters(
                command="python",
                args=["-m", "productivity_assistant.servers.calendar_server"],
                env=None
            )
            
            calendar_client = stdio_client(calendar_params)
            calendar_read, calendar_write = await calendar_client.__aenter__()
            calendar_session = ClientSession(calendar_read, calendar_write)
            await asyncio.wait_for(calendar_session.initialize(), timeout=10.0)
            self.mcp_sessions['calendar'] = {
                'session': calendar_session,
                'client': calendar_client
            }
            logger.info("✓ Calendar MCP initialized")
        except Exception as e:
            breakpoint()
            logger.error(f"✗ Failed to initialize Calendar MCP: {e}")
        
        # Initialize Gmail MCP
        try:
            gmail_params = StdioServerParameters(
                command="python",
                args=["-m", "productivity_assistant.servers.gmail_server"],
                env=None
            )
            
            gmail_client = stdio_client(gmail_params)
            gmail_read, gmail_write = await gmail_client.__aenter__()
            gmail_session = ClientSession(gmail_read, gmail_write)
            await gmail_session.initialize()
            self.mcp_sessions['gmail'] = {
                'session': gmail_session,
                'client': gmail_client
            }
            logger.info("✓ Gmail MCP initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Gmail MCP: {e}")
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from MCP servers in Anthropic format."""
        anthropic_tools = []
        
        for server_name, server_data in self.mcp_sessions.items():
            session = server_data['session']
            try:
                # List tools from MCP server
                tools_result = await session.list_tools()
                
                # Convert MCP tool format to Anthropic tool format
                for tool in tools_result.tools:
                    anthropic_tool = {
                        "name": tool.name,
                        "description": tool.description or "",
                        "input_schema": tool.inputSchema
                    }
                    # Tag with server name for routing
                    anthropic_tool['_mcp_server'] = server_name
                    anthropic_tools.append(anthropic_tool)
                    
            except Exception as e:
                logger.error(f"Error getting tools from {server_name}: {e}")
        
        return anthropic_tools
    
    async def call_tool(self, tool_name: str, tool_input: Dict[str, Any], server_name: str) -> Any:
        """Call a tool on the specified MCP server."""
        if server_name not in self.mcp_sessions:
            return {"error": f"MCP server '{server_name}' not found"}
        
        session = self.mcp_sessions[server_name]['session']
        
        try:
            result = await session.call_tool(tool_name, tool_input)
            return result.content
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def chat(self, user_message: str) -> str:
        """Send a message to Claude and handle tool use loop."""
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        tools = await self.get_available_tools()
        
        tools_for_claude = []
        tool_server_map = {}
        for tool in tools:
            server_name = tool.pop('_mcp_server')
            tool_server_map[tool['name']] = server_name
            tools_for_claude.append(tool)
        
        while True:
            # Call Claude
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=self.messages,
                tools=tools_for_claude
            )
            
            # Add Claude's response to history
            self.messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Check if Claude wants to use tools
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
            
            if not tool_use_blocks:
                # No tools used, extract text response
                text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
                return "\n".join(text_blocks) if text_blocks else "No response"
            
            # Process tool calls
            tool_results = []
            for tool_block in tool_use_blocks:
                tool_name = tool_block.name
                tool_input = tool_block.input
                server_name = tool_server_map.get(tool_name)
                
                logger.info(f"🔧 Calling tool: {tool_name} on {server_name}")
                logger.info(f"   Input: {json.dumps(tool_input, indent=2)}")
                
                # Execute the tool
                result = await self.call_tool(tool_name, tool_input, server_name)
                
                logger.info(f"   Result: {json.dumps(result, indent=2)[:200]}...")
                
                # Add tool result to send back to Claude
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": json.dumps(result)
                })
            
            # Send tool results back to Claude
            self.messages.append({
                "role": "user",
                "content": tool_results
            })
    
    async def cleanup(self):
        """Close all MCP sessions."""
        for server_name, server_data in self.mcp_sessions.items():
            try:
                await server_data['client'].__aexit__(None, None, None)
                logger.info(f"✓ Closed {server_name} MCP session")
            except Exception as e:
                logger.error(f"✗ Error closing {server_name}: {e}")