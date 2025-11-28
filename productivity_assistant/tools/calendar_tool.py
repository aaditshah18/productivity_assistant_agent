from datetime import datetime, timedelta
import json

from productivity_assistant.models import CalendarEvent, CalendarEvents, CalendarAddResult, DeleteResult

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

    def create_calendar_event(self, summary: str, description: str, start_time: str, end_time: str, attendees: list[str] = None, timezone: str = 'America/Los_Angeles') -> CalendarAddResult:
        """
        Creates a new calendar event.

        Args:
            summary (str): Title of the event.
            description (str): Description of the event.
            start_time (str): Start time of the event in ISO format (e.g., '2025-12-25T09:00:00-07:00').
            end_time (str): End time of the event in ISO format (e.g., '2025-12-25T10:00:00-07:00').
            attendees (list[str]): Optional list of attendee emails.
            timezone (str): Timezone for the event (e.g., 'America/Los_Angeles').

        Returns:
            CalendarAddResult: A Pydantic model indicating success or failure and event details.
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
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        try:
            event = self.service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
            return CalendarAddResult(event_id=event.get('id'), success=True, message="Event created")
        except Exception as e:
            return CalendarAddResult(event_id="", success=False, message=str(e))

    def list_calendar_events(self, max_results: int = 10, time_min: str = None, time_max: str = None) -> CalendarEvents:
        """
        Lists upcoming calendar events.

        Args:
            max_results (int): Maximum number of events to return.
            time_min (str): Start time for the query in ISO format. Defaults to now.
            time_max (str): End time for the query in ISO format. Defaults to 7 days from now.

        Returns:
            CalendarEvents: A Pydantic model of upcoming events.
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
            next_page_token = events_result.get('nextPageToken')

            if not events:
                return CalendarEvents(count=0, events=[], next_page_token=None)

            events_list = []
            for event_data in events:
                # Ensure organizer and attendees are handled correctly
                organizer = event_data.get('organizer', {})
                attendees_data = event_data.get('attendees', [])

                # Create CalendarEvent instance with proper validation
                event = CalendarEvent(
                    id=event_data.get('id'),
                    name=event_data.get('summary', 'No Title'),
                    status=event_data.get('status'),
                    description=event_data.get('description'),
                    html_link=event_data.get('htmlLink'),
                    created=event_data.get('created'),
                    updated=event_data.get('updated'),
                    organizer_name=organizer.get('displayName', organizer.get('email')),
                    organizer_email=organizer.get('email'),
                    start_time=event_data.get('start', {}).get('dateTime'),
                    end_time=event_data.get('end', {}).get('dateTime'),
                    location=event_data.get('location'),
                    time_zone=event_data.get('start', {}).get('timeZone'),
                    attendees=[{'email': att.get('email'), 'display_name': att.get('displayName'), 'response_status': att.get('responseStatus')} for att in attendees_data]
                )
                events_list.append(event)
            
            return CalendarEvents(count=len(events_list), events=events_list, next_page_token=next_page_token)
        except Exception as e:
            # For simplicity, returning an empty list on error. 
            # In a real app, you'd want more robust error handling.
            return CalendarEvents(count=0, events=[], next_page_token=None)

    def search_calendar_events(self, query: str, max_results: int = 10) -> CalendarEvents:
        """
        Searches for calendar events matching a query.

        Args:
            query (str): The search query string.
            max_results (int): Maximum number of events to return.

        Returns:
            CalendarEvents: A Pydantic model of matching events.
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
            next_page_token = events_result.get('nextPageToken')

            if not events:
                return CalendarEvents(count=0, events=[], next_page_token=None)
            
            events_list = []
            for event_data in events:
                organizer = event_data.get('organizer', {})
                attendees_data = event_data.get('attendees', [])
                event = CalendarEvent(
                    id=event_data.get('id'),
                    name=event_data.get('summary', 'No Title'),
                    status=event_data.get('status'),
                    description=event_data.get('description'),
                    html_link=event_data.get('htmlLink'),
                    created=event_data.get('created'),
                    updated=event_data.get('updated'),
                    organizer_name=organizer.get('displayName', organizer.get('email')),
                    organizer_email=organizer.get('email'),
                    start_time=event_data.get('start', {}).get('dateTime'),
                    end_time=event_data.get('end', {}).get('dateTime'),
                    location=event_data.get('location'),
                    time_zone=event_data.get('start', {}).get('timeZone'),
                    attendees=[{'email': att.get('email'), 'display_name': att.get('displayName'), 'response_status': att.get('responseStatus')} for att in attendees_data]
                )
                events_list.append(event)

            return CalendarEvents(count=len(events_list), events=events_list, next_page_token=next_page_token)
        except Exception as e:
            return CalendarEvents(count=0, events=[], next_page_token=None)

    def delete_calendar_event(self, event_id: str) -> DeleteResult:
        """
        Deletes a calendar event by its ID.

        Args:
            event_id (str): The ID of the event to delete.

        Returns:
            DeleteResult: A Pydantic model indicating success or failure.
        """
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return DeleteResult(status="success", message=f"Event with ID '{event_id}' deleted successfully.")
        except Exception as e:
            return DeleteResult(status="error", message=str(e))

    def add_attendees_to_event(self, event_id: str, attendees: list[str]) -> CalendarAddResult:
        """
        Adds attendees to an existing calendar event.

        Args:
            event_id (str): The ID of the event to update.
            attendees (list[str]): A list of attendee emails to add.

        Returns:
            CalendarAddResult: A Pydantic model indicating success or failure and event details.
        """
        try:
            # First, get the existing event to preserve existing attendees
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()

            # Get the current list of attendees, or initialize a new list if none
            current_attendees = event.get('attendees', [])
            
            # Add new attendees to the list
            for email in attendees:
                current_attendees.append({'email': email})

            # Update the event with the new list of attendees
            updated_event_body = {'attendees': current_attendees}
            
            updated_event = self.service.events().patch(
                calendarId='primary',
                eventId=event_id,
                body=updated_event_body,
                sendUpdates='all'
            ).execute()

            return CalendarAddResult(event_id=updated_event.get('id'), success=True, message="Attendees added successfully")
        except Exception as e:
            return CalendarAddResult(event_id=event_id, success=False, message=str(e))