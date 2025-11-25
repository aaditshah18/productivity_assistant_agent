from datetime import datetime, timedelta
import json

class CalendarTool:
    API_NAME = 'calendar'
    API_VERSION = 'v3'
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, client_secret_file: str, create_service_func) -> None:
        self.client_secret_file = client_secret_file
        self.create_service_func = create_service_func # Store the passed function
        self._service = None # Lazy load the service
        self.today = datetime.now()
        self.delta = timedelta(days=7)
    
    @property
    def service(self):
        """Lazy load the service only when needed."""
        if self._service is None:
            self._service = self.create_service_func( # Use the stored function
                self.client_secret_file,
                self.API_NAME,
                self.API_VERSION,
                self.SCOPES
            )
        return self._service

    def create_calendar_event(self, summary: str, description: str, start_time: str, end_time: str, timezone: str = 'America/Los_Angeles') -> str:
        """
        Creates a new calendar event.

        Args:
            summary (str): Title of the event.
            description (str): Description of the event.
            start_time (str): Start time of the event in ISO format (e.g., '2025-12-25T09:00:00-07:00').
            end_time (str): End time of the event in ISO format (e.g., '2025-12-25T10:00:00-07:00').
            timezone (str): Timezone for the event (e.g., 'America/Los_Angeles').

        Returns:
            str: A JSON string indicating success or failure and event details.
        """
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }
        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return json.dumps({"status": "success", "message": "Event created", "event_id": event.get('id'), "html_link": event.get('htmlLink')})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def list_calendar_events(self, max_results: int = 10, time_min: str = None, time_max: str = None) -> str:
        """
        Lists upcoming calendar events.

        Args:
            max_results (int): Maximum number of events to return.
            time_min (str): Start time for the query in ISO format. Defaults to now.
            time_max (str): End time for the query in ISO format. Defaults to 7 days from now.

        Returns:
            str: A JSON string of upcoming events.
        """
        now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        if not time_min:
            time_min = now
        if not time_max:
            time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            if not events:
                return json.dumps({"status": "success", "message": "No upcoming events found."})
            
            events_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                events_list.append({
                    "id": event['id'],
                    "summary": event['summary'],
                    "start": start,
                    "html_link": event['htmlLink']
                })
            return json.dumps({"status": "success", "events": events_list})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def search_calendar_events(self, query: str, max_results: int = 10) -> str:
        """
        Searches for calendar events matching a query.

        Args:
            query (str): The search query string.
            max_results (int): Maximum number of events to return.

        Returns:
            str: A JSON string of matching events.
        """
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            if not events:
                return json.dumps({"status": "success", "message": f"No events found matching '{query}'."})
            
            events_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                events_list.append({
                    "id": event['id'],
                    "summary": event['summary'],
                    "start": start,
                    "html_link": event['htmlLink']
                })
            return json.dumps({"status": "success", "events": events_list})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def delete_calendar_event(self, event_id: str) -> str:
        """
        Deletes a calendar event by its ID.

        Args:
            event_id (str): The ID of the event to delete.

        Returns:
            str: A JSON string indicating success or failure.
        """
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return json.dumps({"status": "success", "message": f"Event with ID '{event_id}' deleted successfully."})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})