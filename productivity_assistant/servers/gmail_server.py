import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
# from mcp.server.stdio import stdio_server # Import run_app_stdio

from productivity_assistant.tools.gmail_tool import GmailTool
from productivity_assistant.tools.google_api_service import create_service


load_dotenv()

GOOGLE_API_CLIENT_SECRET_FILE = os.getenv("GOOGLE_API_CLIENT_SECRET_FILE")
if not GOOGLE_API_CLIENT_SECRET_FILE:
    raise ValueError("GOOGLE_API_CLIENT_SECRET_FILE environment variable not set.")
if not os.path.exists(GOOGLE_API_CLIENT_SECRET_FILE):
    raise FileNotFoundError(f"Client secret file not found at {GOOGLE_API_CLIENT_SECRET_FILE}")

# Initialize FastMCP instance
app = FastMCP(name='Google Gmail')

gmail_tool = GmailTool(client_secret_file=GOOGLE_API_CLIENT_SECRET_FILE, create_service_func=create_service)

app.add_tool(
    gmail_tool.list_messages,
    name='list-messages',
    description='Lists messages from the user\'s Gmail inbox with optional query and max results.'
)

app.add_tool(
    gmail_tool.get_message_body,
    name='get-message-body',
    description='Retrieves the full body of a specific Gmail message by its ID.'
)



