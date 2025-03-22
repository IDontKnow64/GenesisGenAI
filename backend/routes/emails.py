from flask import Blueprint, jsonify, session, redirect
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import google.auth
from googleapiclient.discovery import build
from flask import session
from base64 import urlsafe_b64decode
import requests
import re
#from main import checkSpam, sortFolders, createSummary

def get_gmail_service():
    """Authenticate and return Gmail service object."""
    credentials = session.get("google_credentials")
    if not credentials:
        return None  # No credentials found

    from google.oauth2.credentials import Credentials
    creds = Credentials(
        token=credentials["token"],
        refresh_token=credentials["refresh_token"],
        token_uri=credentials["token_uri"],
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        scopes=credentials["scopes"],
    )

    return build("gmail", "v1", credentials=creds)

def extract_email_details(message):
    """Extract email details like Subject, From, To, CC, and Body."""
    headers = message.get("payload", {}).get("headers", [])
    parts = message.get("payload", {}).get("parts", [])

    def get_header(name):
        return next((h["value"] for h in headers if h["name"].lower() == name.lower()), "N/A")

    subject = get_header("Subject")
    sender = get_header("From")
    recipient = get_header("To")
    cc = get_header("Cc")
    date_received = get_header("Date")

    body = "N/A"
    if parts:
        for part in parts:
            if part.get("mimeType") == "text/plain":
                body = urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break
            elif part.get("mimeType") == "text/html":
                body = urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

    # Filter out long, random-looking URLs using regex
    body = re.sub(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL Removed]', body)

    # Filter long random links (optional additional step)
    body = re.sub(r'http[s]?://(?:[A-Za-z0-9-]+\.)+[A-Za-z0-9]{2,6}/[A-Za-z0-9\-_/]*', '[URL Removed]', body)

    body = re.sub(r'[\u200B\u200C\u200D\u200E\u200F\u202A-\u202E\u2060\uFEFF\u034F\u00AD\u2007\r\n]+', '', body)


    return {
        "Subject": subject,
        "From": sender,
        "To": recipient,
        "CC": cc,
        "Date Received": date_received,
        "Body": body.strip()  # Limit body preview to 500 chars
    }

def get_user_email():
    """Fetch the user's email using the Gmail API service."""
    service = get_gmail_service()  # Get the authenticated service
    if not service:
        return None  # No service available, not authenticated

    try:
        # Fetch user profile using 'me' (authenticated user)
        profile = service.users().getProfile(userId='me').execute()
        return profile.get('emailAddress')  # Return email address
    except Exception as e:
        print(f"Error fetching email: {str(e)}")
        return None

def fetch_emails(max):
    """Fetch the latest 10 emails from the user's Gmail inbox."""
    service = get_gmail_service()
    if not service:
        return redirect("/auth/login")

    try:
        results = service.users().messages().list(userId="me", maxResults=max, q="to:me").execute()

        messages = results.get("messages", [])

        if not messages:
            return "📭 No emails found."

        email_list = []
        for msg in messages:
            msg_id = msg["id"]
            message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            email_details = extract_email_details(message)
            email_list.append(email_details)

        return email_list

    except Exception as e:
        return f"❌ Error fetching emails: {str(e)}"

email_blueprint = Blueprint('email', __name__)

@email_blueprint.route('/messages/<message_id>')
def get_message(message_id):
    # Check if user is authenticated
    if 'google_credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Retrieve stored credentials from session
    creds_data = session['google_credentials']
    
    # Create Credentials object
    credentials = Credentials(
        token=creds_data['token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes']
    )

    # Refresh token if expired
    if credentials.expired:
        try:
            credentials.refresh(Request())
            # Update session with new token
            session['google_credentials']['token'] = credentials.token
        except Exception as e:
            return jsonify({'error': 'Failed to refresh token', 'details': str(e)}), 401

    try:
        # Build Gmail API client
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get message details
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='metadata'  # Can be 'full', 'metadata', 'minimal', or 'raw'
        ).execute()

        return jsonify(message)
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve message',
            'details': str(e)
        }), 500
    
@email_blueprint.route('/setfolders')
def get_email():
    email = get_user_email()  # Fetch the email address using Gmail API
    print(email)
    if email:
        return jsonify({'email': email})  # Return the email in a JSON response
    else:
        return jsonify({'error': 'Failed to retrieve email'}), 400


@email_blueprint.route('/check')
def check():
    emails = fetch_emails(10) # Change parameter to fetch more emails

    #checkSpam()
    #sortFolders()
    #createSummary()

    #Clean email format for AI formatting

    return emails
