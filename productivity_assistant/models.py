from pydantic import BaseModel, Field
from datetime import datetime



class EmailItem(BaseModel):
    """Represents an email from the inbox"""
    id: str
    subject: str
    sender: str
    date: datetime
    body: str

class Calendar(BaseModel):
    id: str = Field(..., description="The ID of the calendar.")
    name: str = Field(..., description="The name of the calendar.")
    time_zone: str = Field(..., description="The time zone of the calendar.")
    description: str | None = Field(..., description="The description of the calendar.")

class Calendars(BaseModel):
    count: int = Field(..., description="The number of calendars.")
    calendars: list[Calendar] = Field(..., description="List of calendars.")
    next_page_token: str | None = Field(..., description="Token for the next page of results.")

class Attendee(BaseModel):
    email: str = Field(..., description="The email of the attendee.")
    display_name: str | None = Field(..., description="The display name of the attendee.")
    response_status: str | None = Field(..., description="The response status of the attendee.")

class CalendarEvent(BaseModel):
    id: str = Field(..., description="The ID of the calendar event.")
    name: str = Field(..., description="The name of the calendar event.")
    status: str = Field(..., description="The status of the calendar event.")
    description: str | None = Field(..., description="The description of the calendar event.")
    html_link: str = Field(..., description="The HTML link to the calendar event.")
    created: str = Field(..., description="The creation date of the calendar event.")
    updated: str = Field(..., description="The last updated date of the calendar event.")
    organizer_name: str = Field(..., description="The name of the event organizer.")
    organizer_email: str = Field(..., description="The email of the event organizer.")
    start_time: str = Field(..., description="The start time of the calendar event.")
    end_time: str = Field(..., description="The end time of the calendar event.")
    location: str | None = Field(..., description="The location of the calendar event.")
    time_zone: str = Field(..., description="The time zone of the calendar event.")
    attendees: list[Attendee] = Field(default_factory=list, description="List of event attendees.")


class ReviewSession(BaseModel):
    """Stores a review session with extracted events"""
    session_id: str
    events: list[CalendarEvent]
    created_at: datetime = Field(default_factory=datetime.now)


class ApprovalRequest(BaseModel):
    """Request to approve specific events"""
    approved_event_ids: list[str]


class CalendarAddResult(BaseModel):
    """Result of adding events to calendar"""
    event_id: str
    success: bool
    message: str

class CalendarEvents(BaseModel):
    count: int = Field(..., description="The number of calendar events.")
    events: list[CalendarEvent] = Field(..., description="List of calendar events.")
    next_page_token: str | None = Field(..., description="Token for the next page of results.")

class DeleteResult(BaseModel):
    """Result of a delete operation"""
    status: str
    message: str

class EmailItems(BaseModel):
    """A list of emails"""
    count: int
    messages: list[EmailItem]

class MessageBody(BaseModel):
    """The body of an email message"""
    status: str
    body: str