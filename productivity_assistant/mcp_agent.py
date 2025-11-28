from datetime import datetime
import os
import json
from typing import List, Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv
import logging
from pydantic import BaseModel

# Direct imports of your MCP servers
from productivity_assistant.servers.calendar_server import app as calendar_app
from productivity_assistant.servers.gmail_server import app as gmail_app

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MCPAgent:
    """Agent that uses MCP tools by directly importing FastMCP apps."""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.messages = []
        self.all_tools = []
        self.tool_map = {}
        
    async def initialize(self):
        """Load tools from MCP apps."""
        # Get tools from MCP apps
        calendar_tools = await self._get_tools_from_app(calendar_app, "calendar")
        gmail_tools = await self._get_tools_from_app(gmail_app, "gmail")
        
        self.all_tools = calendar_tools + gmail_tools
        
        logger.info(f"✓ Loaded {len(calendar_tools)} calendar tools")
        logger.info(f"✓ Loaded {len(gmail_tools)} gmail tools")
        
    async def _get_tools_from_app(self, mcp_app, server_name: str) -> List[Dict[str, Any]]:
        """Extract tools from FastMCP app."""
        tools = []
        
        try:
            # Use FastMCP's async list_tools() method
            tools_list = await mcp_app.list_tools()
            
            for tool in tools_list:
                # Get the actual Tool object from the tool manager
                tool_obj = mcp_app._tool_manager._tools.get(tool.name)
                
                if tool_obj:
                    # Extract the actual function from the Tool object
                    tool_func = tool_obj.fn if hasattr(tool_obj, 'fn') else tool_obj
                    
                    tool_schema = {
                        "name": tool.name,
                        "description": tool.description or f"Tool: {tool.name}",
                        "input_schema": tool.inputSchema,
                        "_server": server_name,
                        "_func": tool_func
                    }
                    tools.append(tool_schema)
                    # Store in tool map for execution
                    self.tool_map[tool.name] = {'func': tool_func, 'server': server_name}
                    
        except Exception as e:
            logger.error(f"Error extracting tools from {server_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return tools
    
    def chat(self, user_message: str) -> str:
        """Chat with Claude using MCP tools."""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        self.messages.append({"role": "assistant", "content": f"Current Date is {current_date}"})
        self.messages.append({"role": "user", "content": user_message})
        
        # Prepare tools for Claude (remove internal fields)
        tools_for_claude = []
        
        for tool in self.all_tools:
            clean_tool = {
                "name": tool['name'],
                "description": tool['description'],
                "input_schema": tool['input_schema']
            }
            tools_for_claude.append(clean_tool)
        
        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=self.messages,
                tools=tools_for_claude
            )
            
            self.messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Check for tool use
            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            
            if not tool_use_blocks:
                # Return text response
                text_blocks = [b.text for b in response.content if hasattr(b, 'text')]
                return "\n".join(text_blocks) if text_blocks else "No response"
            
            # Execute tools
            tool_results = []
            for tool_block in tool_use_blocks:
                tool_name = tool_block.name
                tool_input = tool_block.input
                
                logger.info(f"🔧 Calling: {tool_name}")
                logger.info(f"   Input: {json.dumps(tool_input, indent=2)}")
                
                # Call the tool directly
                tool_func = self.tool_map[tool_name]['func']
                result = tool_func(**tool_input)
                
                # Handle Pydantic models by serializing them
                if isinstance(result, BaseModel):
                    content = result.model_dump_json(indent=2)
                    logger.info(f"   Result: {content[:200]}...")
                else:
                    content = str(result)
                    logger.info(f"   Result: {content[:200]}...")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": content
                })
            
            # Send results back
            self.messages.append({
                "role": "user",
                "content": tool_results
            })