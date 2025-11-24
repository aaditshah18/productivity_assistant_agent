from productivity_assistant.mcp_client import MCPClient
from datetime import datetime, timedelta

class AssistantAgent:
    def __init__(self):
        self.mcp_client = MCPClient()
        
    def list_emails(self, max_results: int = 10):
        print(f"Listing {max_results} emails...")
        emails = self.mcp_client.list_emails(max_results=max_results)
        if emails:
            print("Recent Emails:")
            for email in emails:
                print(f"- From: {email.get('from')}, Subject: {email.get('subject')}, Date: {email.get('date')}")
        else:
            print("No emails found or error fetching emails.")
        return emails

    def get_email_content(self, email_id: str):
        print(f"Fetching content for email ID: {email_id}...")
        body = self.mcp_client.get_email_body(email_id)
        if body:
            print(f"Email Body:\n{body}")
        else:
            print(f"Could not fetch body for email ID: {email_id}")
        return body

    def create_calendar_event(self, summary: str, description: str, start_time: str, end_time: str, timezone: str = 'America/Los_Angeles'):
        print(f"Creating calendar event: {summary} from {start_time} to {end_time}...")
        result = self.mcp_client.create_calendar_event(summary, description, start_time, end_time, timezone)
        if result.get("status") == "success":
            print(f"Successfully created event: {result.get('message')}")
        else:
            print(f"Failed to create event: {result.get('message')}")
        return result
    
    def list_calendar_events(self, max_results: int = 10, time_min: str = None, time_max: str = None):
        print(f"Listing upcoming calendar events (max {max_results})...")
        result = self.mcp_client.list_calendar_events(max_results=max_results, time_min=time_min, time_max=time_max)
        if result.get("status") == "success":
            events = result.get("events")
            if events:
                print("Upcoming Events:")
                for event in events:
                    print(f"- Summary: {event.get('summary')}, Start: {event.get('start')}, Link: {event.get('html_link')}")
            else:
                print("No upcoming events found.")
        else:
            print(f"Failed to list events: {result.get('message')}")
        return result

    def search_calendar_events(self, query: str, max_results: int = 10):
        print(f"Searching calendar events for '{query}' (max {max_results})...")
        result = self.mcp_client.search_calendar_events(query=query, max_results=max_results)
        if result.get("status") == "success":
            events = result.get("events")
            if events:
                print(f"Events matching '{query}':")
                for event in events:
                    print(f"- Summary: {event.get('summary')}, Start: {event.get('start')}, Link: {event.get('html_link')}")
            else:
                print(f"No events found matching '{query}'.")
        else:
            print(f"Failed to search events: {result.get('message')}")
        return result

    def delete_calendar_event(self, event_id: str):
        print(f"Deleting calendar event with ID: {event_id}...")
        result = self.mcp_client.delete_calendar_event(event_id=event_id)
        if result.get("status") == "success":
            print(f"Successfully deleted event: {result.get('message')}")
        else:
            print(f"Failed to delete event: {result.get('message')}")
        return result
        
    def run(self, command: str, **kwargs):
        if command == "list_emails":
            return self.list_emails(kwargs.get("max_results", 10))
        elif command == "get_email_content":
            return self.get_email_content(kwargs.get("email_id"))
        elif command == "create_calendar_event":
            return self.create_calendar_event(
                kwargs.get("summary"),
                kwargs.get("description"),
                kwargs.get("start_time"),
                kwargs.get("end_time"),
                kwargs.get("timezone", 'America/Los_Angeles')
            )
        elif command == "list_calendar_events":
            return self.list_calendar_events(
                kwargs.get("max_results", 10),
                kwargs.get("time_min"),
                kwargs.get("time_max")
            )
        elif command == "search_calendar_events":
            return self.search_calendar_events(
                kwargs.get("query"),
                kwargs.get("max_results", 10)
            )
        elif command == "delete_calendar_event":
            return self.delete_calendar_event(kwargs.get("event_id"))
        else:
            print(f"Unknown command: {command}")
            return None

if __name__ == "__main__":
    agent = AssistantAgent()
    print("Agent setup complete. To run, ensure .env is configured.")