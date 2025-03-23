import os
import re
import nltk
from flask import Blueprint, jsonify, session, redirect, request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from base64 import urlsafe_b64decode
from dotenv import load_dotenv
from sql import *
from utils import cohere_detection as chd

load_dotenv()
nltk.download('punkt_tab')
   
api_key = os.getenv("CO_API_KEY")

def get_gmail_service():
    """Authenticate and return Gmail service object."""
    credentials = session.get("google_credentials")
    if not credentials:
        return None  # No credentials found

    creds = Credentials(
        token=credentials["token"],
        refresh_token=credentials["refresh_token"],
        token_uri=credentials["token_uri"],
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        scopes=credentials["scopes"],
    )

    return build("gmail", "v1", credentials=creds)

def extract_email_details(message, id):
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

    return {
        "id": str(id),
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
            email_details = extract_email_details(message, msg_id)
            email_list.append(email_details)

        return email_list

    except Exception as e:
        return f"❌ Error fetching emails: {str(e)}"

email_blueprint = Blueprint('emails', __name__)

@email_blueprint.route('/')
def check_email_connection():
    return {
        'message': 'Email Connected?',
        'connected': str("google_credentials" in session) 
        }

@email_blueprint.route('/address', methods=["GET"])
def get_email():
    """Fetch the user's email using the Gmail API service."""
    try:
        email = get_user_email()
        return jsonify({"email": email})
    except Exception as e:
        print(f"Error fetching email: {str(e)}")
        return jsonify({"error": "Failed to fetch email", "details": str(e)}), 500

@email_blueprint.route('/raw', methods=["GET"])
def get_raw_email():
    """Fetch the user's email using the Gmail API service."""
    max_emails = request.args.get('max', default=10, type=int)
    emails = fetch_emails(max_emails)
    if isinstance(emails, str):  # If fetch_emails() returned an error string
        return jsonify({"error": emails}), 500

    return jsonify(emails)  # Return results as JSON


@email_blueprint.route('/creds', methods=["GET"])
def get_user_creds():
    # First check authentication
    service = get_gmail_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        # Get credentials from session
        credentials = session.get("google_credentials")
        
        if not credentials:
            return jsonify({"error": "No credentials found in session"}), 404

        # Construct proper JSON response
        return jsonify({
            "token": credentials.get("token"),
            "refresh_token": credentials.get("refresh_token"),
            "token_uri": credentials.get("token_uri"),
            "client_id": credentials.get("client_id"),
            "client_secret": credentials.get("client_secret"),
            "scopes": credentials.get("scopes")
        })

    except Exception as e:
        print(f"Error fetching credentials: {str(e)}")
        return jsonify({
            "error": "Failed to fetch credentials",
            "details": str(e)
        }), 500

@email_blueprint.route('/messages/<message_id>')
def get_message(message_id):
    # Check if user is authenticated
    service = get_gmail_service()
    
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    # Refresh token if expired
    # if credentials.expired:
    #     try:
    #         credentials.refresh(Request())
    #         # Update session with new token
    #         session['google_credentials']['token'] = credentials.token
    #     except Exception as e:
    #         return jsonify({'error': 'Failed to refresh token', 'details': str(e)}), 401

    try:
        # Build Gmail API client        
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
    
@email_blueprint.route('/setfolders', methods=["GET", "POST"])
def set_email_db():
    email = get_user_email()  # Fetch the email address using Gmail API
    db = SQL("sqlite:///users.db")

    user = db.execute("SELECT * FROM users WHERE emailaddress = :emailaddress", emailaddress=email)

    if len(user) == 0:
        db.execute("INSERT INTO users (emailaddress) VALUES (:emailaddress)", emailaddress=email)
        db.commit()

    if email:
        return jsonify({'email': email})  # Return the email in a JSON response
    else:
        return jsonify({'error': 'Failed to retrieve email'}), 400

@email_blueprint.route('/check', methods=['GET'])
def check():
    emails = fetch_emails(10)  # Fetch emails

    if isinstance(emails, str):  # If fetch_emails() returned an error string
        return jsonify({"error": emails}), 500

    results = []

    for email in emails:
        scam_result = chd.detect_scam(email['Body'])  # Call the updated function
        results.append({"email": email, "scam_status": scam_result[0], "confidence": scam_result[2]})  # Store both email and scam result

    return jsonify(results)  # Return results as JSON
