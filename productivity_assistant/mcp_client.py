import json
import subprocess
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    """Client to interact with MCP servers directly via stdio"""
    
    def __init__(self):
        self.calendar_mcp_path = "/Users/aaditshah/ReKnew/productivity-assistant/productivity_assistant/mcp_servers/calendar_mcp.py"
        self.mcp_bin = "/Users/aaditshah/ReKnew/productivity-assistant/.venv/bin/mcp"
        
    def _call_mcp_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call an MCP tool directly via stdio protocol
        """
        try:
            # Start MCP server process
            process = subprocess.Popen(
                [self.mcp_bin, "run", self.calendar_mcp_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Initialize the server
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "productivity-assistant", "version": "1.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialization response (skip for now)
            init_line = process.stdout.readline()
            print(f"Init response: {init_line.strip()}")
            
            # Send initialized notification
            init_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write(json.dumps(init_notification) + "\n")
            process.stdin.flush()
            
            # Call the tool
            tool_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            print(f"Calling tool: {tool_name} with args: {arguments}")
            process.stdin.write(json.dumps(tool_request) + "\n")
            process.stdin.flush()
            
            # Read tool response
            response_line = process.stdout.readline()
            print(f"Tool response: {response_line.strip()}")
            
            # Clean up
            process.stdin.close()
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            
            if response_line:
                response_data = json.loads(response_line)
                if "result" in response_data:
                    result = response_data["result"]
                    
                    # Check if result has content array
                    if isinstance(result, dict) and "content" in result:
                        content = result["content"]
                        if isinstance(content, list) and len(content) > 0:
                            # Extract text from first content block
                            first_block = content[0]
                            if isinstance(first_block, dict) and first_block.get("type") == "text":
                                text = first_block.get("text", "")
                                try:
                                    return json.loads(text)
                                except:
                                    return {"status": "success", "message": text}
                    
                    return result
                elif "error" in response_data:
                    return {"status": "error", "message": response_data["error"]["message"]}
            
            return {"status": "error", "message": "No response from MCP server"}
            
        except Exception as e:
            import traceback
            print(f"Exception: {traceback.format_exc()}")
            return {"status": "error", "message": str(e)}

    def list_emails(self, max_results: int = 50) -> list[dict]:
        """
        Fetch recent emails from Gmail
        """
        # For now, return empty list since Gmail MCP isn't set up
        print("Gmail MCP not yet implemented")
        return []

    def get_email_body(self, email_id: str) -> Optional[str]:
        """
        Fetch full email body for a specific email ID
        """
        print("Gmail MCP not yet implemented")
        return None
        
    def create_calendar_event(self, summary: str, description: str, start_time: str, end_time: str, timezone: str = 'America/Los_Angeles') -> dict:
        """
        Create a calendar event in Google Calendar
        """
        return self._call_mcp_tool("create-calendar-event", {
            "summary": summary,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "timezone": timezone
        })

    def list_calendar_events(self, max_results: int = 10, time_min: Optional[str] = None, time_max: Optional[str] = None) -> dict:
        """
        Lists upcoming calendar events
        """
        params = {"max_results": max_results}
        if time_min:
            params["time_min"] = time_min
        if time_max:
            params["time_max"] = time_max
            
        return self._call_mcp_tool("list-calendar-events", params)

    def search_calendar_events(self, query: str, max_results: int = 10) -> dict:
        """
        Searches for calendar events matching a query
        """
        return self._call_mcp_tool("search-calendar-events", {
            "query": query,
            "max_results": max_results
        })

    def delete_calendar_event(self, event_id: str) -> dict:
        """
        Deletes a calendar event by its ID
        """
        return self._call_mcp_tool("delete-calendar-event", {
            "event_id": event_id
        })