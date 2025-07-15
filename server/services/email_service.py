from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from datetime import datetime, timedelta

# Define the scopes needed for Gmail API access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    """
    A service class to interact with the Gmail API.
    Handles authentication, token refreshing, and fetching emails.
    """

    def __init__(self, user_id=None, access_token=None, refresh_token=None, token_expiry=None):
        self.user_id = user_id
        self.credentials = self._build_credentials(access_token, refresh_token, token_expiry)
        self.service = self._build_gmail_service()

    def _build_credentials(self, access_token, refresh_token, token_expiry):
        """
        Builds Google API credentials from stored tokens.
        Refreshes the token if expired.
        """
        if not access_token or not refresh_token or not token_expiry:
            # If no tokens, user needs to go through OAuth flow.
            return None

        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=os.getenv('GMAIL_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            client_id=os.getenv('GMAIL_CLIENT_ID'),
            client_secret=os.getenv('GMAIL_CLIENT_SECRET'),
            scopes=SCOPES
        )

        # Check if token is expired and refresh if necessary
        if creds.expired and creds.refresh_token:
            print("Access token expired, refreshing...")
            try:
                creds.refresh(Request())
                # Update DB with new tokens if refresh successful.
                print(f"Token refreshed. New expiry: {creds.expiry}")
                # Save creds.token, creds.refresh_token, creds.expiry to your User model here.
            except Exception as e:
                print(f"Error refreshing token: {e}")
                return None # Token refresh failed

        return creds

    def _build_gmail_service(self):
        """
        Builds and returns a Gmail API service object.
        """
        if not self.credentials:
            print("Credentials not available. Cannot build Gmail service.")
            return None
        try:
            service = build('gmail', 'v1', credentials=self.credentials)
            return service
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def list_messages(self, query='is:unread', max_results=10):
        """
        Lists messages in the user's inbox based on a query.
        """
        if not self.service:
            return []
        try:
            response = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = response.get('messages', [])
            return messages
        except HttpError as error:
            print(f'An error occurred while listing messages: {error}')
            return []

    def get_message(self, msg_id):
        """
        Retrieves a specific message by its ID.
        """
        if not self.service:
            return None
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            return message
        except HttpError as error:
            print(f'An error occurred while getting message {msg_id}: {error}')
            return None

    def extract_email_details(self, message):
        """
        Extracts subject, sender, and body from a Gmail API message object.
        Handles both plain text and HTML bodies.
        """
        headers = message['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
        thread_id = message.get('threadId')

        body_content = ""
        if 'parts' in message['payload']:
            # Handle multipart messages
            for part in message['payload']['parts']:
                mime_type = part['mimeType']
                if mime_type == 'text/plain' and 'data' in part['body']:
                    body_content += self._decode_base64_url_safe(part['body']['data'])
                elif mime_type == 'text/html' and 'data' in part['body']:
                    body_content += self._decode_base64_url_safe(part['body']['data'])
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            # Handle single part messages
            body_content = self._decode_base64_url_safe(message['payload']['body']['data'])

        return {
            'subject': subject,
            'sender': sender,
            'body': body_content,
            'thread_id': thread_id
        }

    def _decode_base64_url_safe(self, data):
        """Decodes base64url safe string."""
        import base64
        return base64.urlsafe_b64decode(data).decode('utf-8')

# Example Usage (for testing the GmailService)
if __name__ == '__main__':
    # IMPORTANT: For this example to run, you need valid GMAIL_CLIENT_ID,
    # GMAIL_CLIENT_SECRET, and GMAIL_REDIRECT_URI in your .env.
    # You also need to have gone through the OAuth flow to get valid tokens.
    # This example uses hardcoded dummy tokens, which is NOT for production.

    # Dummy tokens for demonstration (REPLACE WITH REAL TOKENS FROM DB)
    dummy_access_token = "YOUR_ACCESS_TOKEN_HERE"
    dummy_refresh_token = "YOUR_REFRESH_TOKEN_HERE"
    # Set an expiry time in the past to test refresh
    dummy_token_expiry = (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z" # ISO format with Z for UTC

    if dummy_access_token == "YOUR_ACCESS_TOKEN_HERE" or dummy_refresh_token == "YOUR_REFRESH_TOKEN_HERE":
        print("Please replace dummy tokens in email_service.py for testing.")
        print("You need to run the /auth/email/authorize and /auth/email/callback routes first to get real tokens.")
    else:
        print("Attempting to initialize GmailService with dummy tokens...")
        gmail_service = GmailService(
            user_id=1, # Dummy user ID
            access_token=dummy_access_token,
            refresh_token=dummy_refresh_token,
            token_expiry=datetime.fromisoformat(dummy_token_expiry.replace('Z', '+00:00')) # Convert to datetime object
        )

        if gmail_service.service:
            print("\nListing unread messages (max 5):")
            messages = gmail_service.list_messages(query='is:unread', max_results=5)
            if messages:
                for msg in messages:
                    print(f"  Message ID: {msg['id']}")
                    full_message = gmail_service.get_message(msg['id'])
                    if full_message:
                        details = gmail_service.extract_email_details(full_message)
                        print(f"    Subject: {details['subject']}")
                        print(f"    Sender: {details['sender']}")
                        print(f"    Thread ID: {details['thread_id']}")
                        print(f"    Body Snippet: {details['body'][:100]}...")
                        # Optionally mark as read after processing
                        # gmail_service.service.users().messages().modify(userId='me', body={'removeLabelIds': ['UNREAD']}).execute()
            else:
                print("No unread messages found.")
        else:
            print("Failed to initialize GmailService. Check your tokens and environment variables.")
