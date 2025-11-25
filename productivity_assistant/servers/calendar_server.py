import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
# from mcp.server.stdio import stdio_server # Import run_app_stdio

from productivity_assistant.tools.calendar_tool import CalendarTool
from productivity_assistant.tools.google_api_service import create_service


load_dotenv()


# Get client secret file path from environment variable
GOOGLE_API_CLIENT_SECRET_FILE = os.getenv("GOOGLE_API_CLIENT_SECRET_FILE")
if not GOOGLE_API_CLIENT_SECRET_FILE:
    raise ValueError("GOOGLE_API_CLIENT_SECRET_FILE environment variable not set.")
if not os.path.exists(GOOGLE_API_CLIENT_SECRET_FILE):
    raise FileNotFoundError(f"Client secret file not found at {GOOGLE_API_CLIENT_SECRET_FILE}")

# Initialize FastMCP instance
app = FastMCP(name='Google Calendar')

# Initialize CalendarTool, passing create_service to it
calendar_tool = CalendarTool(client_secret_file=GOOGLE_API_CLIENT_SECRET_FILE, create_service_func=create_service)

# Add tools to FastMCP instance
app.add_tool(
    calendar_tool.create_calendar_event,
    name='create-calendar-event',
    description='Create a new calendar event with summary, description, start time, end time, and optional timezone.'
)

app.add_tool(
    calendar_tool.list_calendar_events,
    name='list-calendar-events',
    description='List upcoming calendar events, with optional max_results, time_min, and time_max.'
)

app.add_tool(
    calendar_tool.search_calendar_events,
    name='search-calendar-events',
    description='Search for calendar events matching a query, with optional max_results.'
)

app.add_tool(
    calendar_tool.delete_calendar_event,
    name='delete-calendar-event',
    description='Delete a calendar event by its event ID.'
)


if __name__ == '__main__':
    app.run()