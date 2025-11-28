import json
import base64
from datetime import datetime
from productivity_assistant.models import EmailItem, EmailItems, MessageBody

class GmailTool:
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"] # Readonly scope for now

    def __init__(self, client_secret_file: str, create_service_func) -> None:
        self.client_secret_file = client_secret_file
        self.create_service_func = create_service_func
        self._service = None # Lazy load the service
    
    @property
    def service(self):
        """Lazy load the service only when needed."""
        if self._service is None:
            self._service = self.create_service_func(
                self.client_secret_file,
                self.API_NAME,
                self.API_VERSION,
                self.SCOPES
            )
        return self._service

    def list_messages(self, max_results: int = 10, query: str = '') -> 'EmailItems':
        """
        Lists messages from the user's Gmail inbox.

        Args:
            max_results (int): Maximum number of messages to return.
            query (str): Optional Gmail search query (e.g., "from:sender@example.com subject:important").

        Returns:
            EmailItems: A Pydantic model of message metadata.
        """
        try:
            response = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = response.get('messages', [])
            
            messages_list = []
            for msg in messages:
                msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
                headers = msg_data['payload']['headers']
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
                
                # Robust date parsing
                if date_str:
                    try:
                        # Remove timezone name in parentheses
                        if ' (' in date_str:
                            date_str = date_str.split(' (')[0]
                        date = datetime.strptime(date_str.strip(), '%a, %d %b %Y %H:%M:%S %z')
                    except ValueError:
                        date = datetime.now() # Fallback
                else:
                    date = datetime.now()


                messages_list.append(EmailItem(
                    id=msg['id'],
                    subject=subject,
                    sender=sender,
                    date=date,
                    body=msg_data.get('snippet', '')
                ))
            return EmailItems(count=len(messages_list), messages=messages_list)
        except Exception as e:
            return EmailItems(count=0, messages=[])

    def get_message_body(self, message_id: str) -> 'MessageBody':
        """
        Retrieves the full body of a specific message.

        Args:
            message_id (str): The ID of the message to retrieve.

        Returns:
            MessageBody: A Pydantic model containing the message body.
        """
        try:
            message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
            
            # Helper to decode base64url data
            def decode_data(data):
                return base64.urlsafe_b64decode(data).decode('utf-8')

            # Extract the plain text body part
            payload = message['payload']
            body_parts = []
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and 'body' in part and 'data' in part['body']:
                        body_parts.append(decode_data(part['body']['data']))
            elif 'body' in payload and 'data' in payload['body']: # Fallback for messages without 'parts'
                body_parts.append(decode_data(payload['body']['data']))

            if body_parts:
                return MessageBody(status="success", body="\n".join(body_parts))
            else:
                return MessageBody(status="success", body="No plain text body found.")

        except Exception as e:
            return MessageBody(status="error", body=str(e))