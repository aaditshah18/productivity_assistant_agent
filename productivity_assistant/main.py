import os
import logging
from productivity_assistant.agent import AssistantAgent
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def main():
    # Ensure ANTHROPIC_API_KEY, GMAIL_MCP_URL, CALENDAR_MCP_URL, GOOGLE_CLIENT_SECRET_FILE are set in your .env file
    if not os.getenv("ANTHROPIC_API_KEY"):
        logging.error("ANTHROPIC_API_KEY not set in .env file.")
        return
    if not os.getenv("GMAIL_MCP_URL"):
        logging.error("GMAIL_MCP_URL not set in .env file. Cannot interact with Gmail.")
    if not os.getenv("CALENDAR_MCP_URL"):
        logging.error("CALENDAR_MCP_URL not set in .env file. Cannot interact with Calendar.")
    if not os.getenv("GOOGLE_CLIENT_SECRET_FILE"):
        logging.error("GOOGLE_CLIENT_SECRET_FILE not set in .env file. Cannot interact with Google APIs.")

    agent = AssistantAgent()

    print("--- Personal Assistant Agent Demo ---")

    # Example 1: List emails
    print("\nAttempting to list recent emails (max 5)...")
    try:
        agent.run("list_emails", max_results=5)
    except Exception as e:
        print(f"Error listing emails: {e}")

    # Example 2: Create a calendar event
    print("\nAttempting to create a calendar event...")
    try:
        # Define start and end times for the event
        now = datetime.now()
        start_time_iso = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
        end_time_iso = (now + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat()
        
        agent.run("create_calendar_event",
                  summary="Gemini CLI Demo Meeting",
                  description="Demo meeting created by Gemini CLI personal assistant agent.",
                  start_time=start_time_iso,
                  end_time=end_time_iso,
                  timezone="America/Los_Angeles")
    except Exception as e:
        print(f"Error creating calendar event: {e}")

    # Example 3: List upcoming calendar events
    print("\nAttempting to list upcoming calendar events...")
    try:
        agent.run("list_calendar_events", max_results=5)
    except Exception as e:
        print(f"Error listing calendar events: {e}")

    # Example 4: Search for calendar events
    print("\nAttempting to search for calendar events with 'Gemini CLI'...")
    try:
        agent.run("search_calendar_events", query="Gemini CLI", max_results=3)
    except Exception as e:
        print(f"Error searching calendar events: {e}")

    # Example 5: Delete a calendar event (requires an event_id)
    # To test this, uncomment and replace 'YOUR_EVENT_ID_HERE' with an actual event ID
    # that you can get from list_calendar_events or search_calendar_events.
    # print("\nAttempting to delete a calendar event...")
    # try:
    #     agent.run("delete_calendar_event", event_id="YOUR_EVENT_ID_HERE")
    # except Exception as e:
    #     print(f"Error deleting calendar event: {e}")

    print("\n--- Demo Complete ---")

if __name__ == "__main__":
    main()
