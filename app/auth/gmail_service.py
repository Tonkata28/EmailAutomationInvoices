from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load credentials
creds = Credentials.from_authorized_user_file('token.json')
# Intiialize gmail connection
gmail_service = build('gmail', 'v1', credentials=creds)
gmail_upload_service = build('gmail', 'v1', credentials=creds)
