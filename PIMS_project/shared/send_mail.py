import os, base64, json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pydantic import BaseModel
from typing import Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from shared.config import get_settings

settings = get_settings()

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
TOKEN_FILE = os.getenv('TOKEN_FILE')

def get_gmail_service() -> Any:
    """Authenticate and return the Gmail API service."""
    creds = None

    if not os.path.isfile(CREDENTIALS_FILE):
     raise Exception(f"Credentials file not found at {CREDENTIALS_FILE}")
  
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
    
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
 
    return build('gmail', 'v1', credentials=creds)

def send_email(sender: str, to: str, subject: str, body: str):

    try:
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        msg_body = MIMEText(body, 'plain')
        message.attach(msg_body)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        service = get_gmail_service()
        message_response = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        print(f"Message sent successfully: {message_response}")
        
    except Exception as error:
        print(f"Error sending email: {error}")
        raise Exception("Failed to send email")


