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

def sort_into_folders(folders, descriptions, emails):
    """Sort emails into folders based on AI classification using descriptions."""
    categorized_emails = {folder: [] for folder in folders.values()}

    for email in emails:
        classification = chd.classify_email(email['Body'], descriptions)  # AI determines the best fit
        folder_name = folders.get(classification, "Uncategorized")  # Match to a folder
        categorized_emails[folder_name].append(email)  # Store email in folder
    
    return categorized_emails


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
            return " No emails found."

        email_list = []
        for msg in messages:
            msg_id = msg["id"]
            message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            email_details = extract_email_details(message, msg_id)
            email_list.append(email_details)

        return email_list

    except Exception as e:
        return f"Error fetching emails: {str(e)}"

def sort_into_folders(folders, descriptions, emails):
    """Sort emails into folders based on AI classification using descriptions."""
    categorized_emails = {folder: [] for folder in folders.values()}

    for email in emails:
        classification = chd.classify_email_using_embeddings(email['Body'], descriptions)  # AI determines the best fit
        folder_name = folders.get(classification, "Uncategorized")  # Match to a folder
        categorized_emails[folder_name].append(email)  # Store email in folder
    
    return categorized_emails

email_blueprint = Blueprint('emails', __name__)

@email_blueprint.route('/connected', methods=["GET"])
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

@email_blueprint.route('/createfolder', methods=["GET", "POST"])
def createFolder():
    email = get_user_email()  # Fetch the email address using Gmail API
    folder_name = request.form.get('folder_name')  # Assume the folder name is passed in the form
    folder_description = request.form.get('folder_description')  # Assume the description is passed as well
    db = SQL("sqlite:///users.db")

    # Check if the user exists in the database
    user = db.execute("SELECT * FROM users WHERE emailaddress = :emailaddress", emailaddress=email)

    if len(user) == 0:
        # If the user doesn't exist, create a new user record
        db.execute("INSERT INTO users (emailaddress, folder, description) VALUES (:emailaddress, :folder_name, :folder_description)",
                   emailaddress=email, folder_name=folder_name, folder_description=folder_description)
        db.commit()
    else:
        # If the user exists, check if the folder already exists
        existing_folders = db.execute("SELECT folder FROM users WHERE emailaddress = :emailaddress", emailaddress=email)
        existing_folder_names = [folder['folder'] for folder in existing_folders]

        if folder_name not in existing_folder_names:
            # If the folder doesn't exist, add the new folder for the user
            db.execute("INSERT INTO users (emailaddress, folder, description) VALUES (:emailaddress, :folder_name, :folder_description)",
                       emailaddress=email, folder_name=folder_name, folder_description=folder_description)
            db.commit()
        else:
            # Optionally, you can update the folder description if the folder already exists
            db.execute("UPDATE users SET description = :folder_description WHERE emailaddress = :emailaddress AND folder = :folder_name",
                       emailaddress=email, folder_name=folder_name, folder_description=folder_description)
            db.commit()

    return jsonify({"message": "Folder created/updated successfully"})

@email_blueprint.route('/sortintofolders', methods=["GET", "POST"])
def sortintofolders():
    email = get_user_email()  # Fetch the email address using Gmail API
    emails = fetch_emails(10)  # Fetch emails

    # Fetch user folders from the database based on email address
    db = SQL("sqlite:///users.db")
    folders_data = db.execute("SELECT folder, description FROM users WHERE emailaddress = :emailaddress", emailaddress=email)
    
    if isinstance(emails, str):  # If fetch_emails() returned an error string
        return jsonify({"error": emails}), 500

    # Prepare the folders dictionary based on the data fetched
    folders = {folder['folder']: folder['description'] for folder in folders_data}
    
    # Default folder for uncategorized emails
    if "Uncategorized" not in folders:
        folders["Uncategorized"] = "Emails that could not be categorized."

    categorized_emails = sort_into_folders(folder, folders, emails)  # Calls classify_email internally
    return jsonify(categorized_emails)

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

@email_blueprint.route('/summary', methods=['GET'])
def summary():
    emails = fetch_emails(10)  # Fetch emails

    if isinstance(emails, str):  # If fetch_emails() returned an error string
        return jsonify({"error": emails}), 500

    results = []

    for email in emails:
        summary = chd.generate_summary(email['Body'])  # Call the updated function
        results.append({"email": email, "summary": summary})  

    return jsonify(results)  # Return results as JSON

@email_blueprint.route('/summarize/<message_id>', methods=['GET'])
def summarize(message_id):
    service = get_gmail_service()

    # Check authentication
    if service is None:
        return jsonify({"error": "Authentication required"}), 401

    # Fetch email from Gmail API
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
    except Exception as e:
        return jsonify({"error": f"Gmail API Error: {e}"}), 500

    # Extract structured email data using helper
    email = extract_email_details(message, message_id)
    
    # Generate summary and prepare response
    try:
        summary = chd.generate_summary(email['Body'])
    except Exception as e:
        return jsonify({"error": f"Summary generation failed: {e}"}), 500

    return jsonify({
        "email": email,
        "summary": summary
    })

@email_blueprint.route('/measure/<message_id>', methods=['GET'])
def measure(message_id):
    service = get_gmail_service()
    print(f"{service = }")
    # Check authentication
    if service is None:
        return jsonify({"error": "Authentication required"}), 401

    # Fetch email from Gmail API
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        print(f"{message = }")
    except Exception as e:
        return jsonify({"error": f"Gmail API Error: {e}"}), 500

    # Extract structured email data using helper
    email = extract_email_details(message, message_id)
    print(f"{email = }")
    # Generate summary and prepare response
    try:
        type, reasons, score = chd.detect_scam(email['Body'])  # Call the updated function
        print(type, reasons, score)
    except Exception as e:
        return jsonify({"error": f"Summary generation failed: {e}"}), 520

    return jsonify({
        "email": email,
        "type": type,
        "reasons": reasons,
        "score": score
    })

