from flask import Flask, request, redirect
import msal
import requests
import threading
import webbrowser
import time
import os
from dotenv import load_dotenv

import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("MS_CLIENT_ID")
TENANT_ID = os.getenv("MS_TENANT_ID")
MS_REDIRECT_URI = os.getenv("MS_REDIRECT_URI")

GOOGLE_REDIRECT_URI = os.getenv("G_REDIRECT_URI")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SCOPES_MICROSOFT = ["Mail.Read", "User.Read"]
SCOPES_GOOGLE = ["https://www.googleapis.com/auth/gmail.readonly"]

app = Flask(__name__)
token_result = {}
google_credentials = {}

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if code:
        app_instance = msal.ConfidentialClientApplication(
            CLIENT_ID,
            authority=AUTHORITY
        )
        result = app_instance.acquire_token_by_authorization_code(
            code,
            scopes=SCOPES_MICROSOFT,
            redirect_uri=MS_REDIRECT_URI
        )
        token_result["token"] = result
        return """
        <html>
            <head><title>Authenticated</title></head>
            <body>
                ✅ Authentication complete. You can close this window.
            </body>
        </html>
        """
    return """
    <html>
        <head><title>Auth Failed</title></head>
        <body>
            ❌ Authentication failed.
        </body>
    </html>
    """


def authenticate_microsoft():
    app_instance = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY
    )
    auth_url = app_instance.get_authorization_request_url(SCOPES_MICROSOFT, redirect_uri=MS_REDIRECT_URI)
    print("🔐 Starting OAuth flow. Browser will open...")
    webbrowser.open(auth_url)
    port = int(MS_REDIRECT_URI.split(":")[-1].split("/")[0])
    app.run(port=port)

def test_microsoft_identity(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    print("\n🔍 Testing /me endpoint...")
    response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Signed in as: {user['displayName']} ({user['userPrincipalName']})")
        return user
    else:
        print(f"❌ Identity check failed: {response.status_code}")
        print(response.text)
        return None

def fetch_microsoft_emails(access_token, user_email=None):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
 
    url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"

    print("\n📬 Fetching latest emails...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json().get("value", [])
        if not messages:
            print("📭 Inbox is empty.")
        for msg in messages:
            print(f"Subject: {msg['subject']}")
            print(f"From: {msg['from']['emailAddress']['address']}")
            print(f"Received: {msg['receivedDateTime']}")
            print("-" * 50)
    if response.status_code == 401:
        print("❌ Unauthorized: Mailbox might not exist or token is invalid.")
        print("Try with a Microsoft 365 work/school account.")


# Google OAuth (PKCE, No secret)
def authenticate_google():
    flow = InstalledAppFlow.from_client_secrets_file(
        "src/client_secret.json",
        scopes=SCOPES_GOOGLE
    )
    creds = flow.run_local_server(
        port=5001,
        prompt="consent",
        success_message="✅ Authentication complete. You can close this window.",
        authorization_prompt_message=""
    )
    google_credentials["token"] = creds


def fetch_gmail_emails(credentials):
    print("\n📬 Gmail: Fetching latest emails...")
    service = build('gmail', 'v1', credentials=credentials)
    result = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = result.get('messages', [])
    if not messages:
        print("📭 Gmail inbox is empty.")
    for msg in messages:
        message_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = message_detail['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        print(f"Subject: {subject}")
        print(f"From: {sender}")
        print("-" * 50)


if __name__ == "__main__":
    choice = input("Which service do you want to authenticate and fetch emails from? (microsoft/gmail): ").strip().lower()

    if choice == "microsoft":
        threading.Thread(target=authenticate_microsoft).start()

        # Wait until Microsoft token is retrieved
        while "token" not in token_result:
            time.sleep(1)

        token_data = token_result["token"]

        if "access_token" in token_data:
            access_token = token_data["access_token"]
            print("✅ Microsoft access token retrieved.")

            identity = test_microsoft_identity(access_token)
            fetch_microsoft_emails(access_token)
        else:
            print("❌ Failed to get Microsoft access token:")
            print(token_data)

    elif choice == "gmail":
        threading.Thread(target=authenticate_google).start()

        # Wait until Google token is retrieved
        while "token" not in google_credentials:
            time.sleep(1)

        google_creds = google_credentials["token"]
        if google_creds:
            print("✅ Google access token retrieved.")
            fetch_gmail_emails(google_creds)
        else:
            print("❌ Failed to get Google access token.")
    else:
        print("❌ Invalid choice. Please run the script again and enter 'microsoft' or 'gmail'.")