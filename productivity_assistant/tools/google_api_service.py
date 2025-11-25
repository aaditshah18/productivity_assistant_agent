import os

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def create_service(client_secret_file, api_name, api_version, *scopes, prefix=''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    
    creds = None

    working_dir = os.path.dirname(os.path.abspath(__file__))
    token_dir = 'token_files'
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'
    
    token_path = os.path.join(working_dir, token_dir)
    
    if not os.path.exists(token_path):
        os.makedirs(token_path, exist_ok=True)
    
    token_file_path = os.path.join(token_path, token_file)
    
    if os.path.exists(token_file_path):
        creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_file_path, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        return service
    except Exception as e:
        if os.path.exists(token_file_path):
            os.remove(token_file_path)
        raise e