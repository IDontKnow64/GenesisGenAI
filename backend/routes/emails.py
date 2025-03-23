from flask import Blueprint, jsonify, session, redirect, request
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
import json
import os
import cohere
import numpy as np
import nltk
import re
from dotenv import load_dotenv
from sql import *

load_dotenv()
nltk.download('punkt_tab')

def add_punctuation(line):
    # Strip extra spaces at the start and end of the line
    line = line.strip()
    if line and not line[-1] in ['.', '?', '!',":"]:
        return line + '.'
    return line


def detect_scam(mail):
     api_key = os.getenv("CO_API_KEY")
     email_content = mail
     model = 'command-a-03-2025'
     temperature = 0.1

     try:

        co = cohere.ClientV2(api_key)

        response = co.chat(
            model=model,
            messages=[
                    {  
                        "role": "system",
                        "content": "You respond with only either 'scam' or 'safe' for the given email and then you respond with only a number that gives a scam rating from 0 (safe) to 100 (guaranteened scam)"
                    },
                    {
                    "role": "user",
                    "content": email_content,
                    }
                ],
            temperature = temperature
        )
        #print (response.message.content[0].text)
        scam_score = response.message.content[0].text.split()[1]

        if (response.message.content[0].text.split()[0]=="scam"):
            result = "scam"
            lines = email_content.split('\n')
            processed_lines = [add_punctuation(line) for line in lines]
            processed_email_content = '\n'.join(processed_lines)
            clean_content = re.sub(r'•⁠  ', '-', processed_email_content)
            clean_content = re.sub(r':', '.', clean_content)
            documents = nltk.sent_tokenize(clean_content)

            doc_emb = co.embed(
                texts=documents,
                model="embed-english-v3.0",
                input_type="search_document",
                embedding_types=["float"],
            ).embeddings.float

            query = "Which parts of an email indicates that it is a scam?"

            query_emb = co.embed(
                texts=[query],
                model="embed-english-v3.0",
                input_type="search_query",
                embedding_types=["float"],
            ).embeddings.float

            scores = np.dot(query_emb, np.transpose(doc_emb))[0]
            scores_max = scores.max()
            scores_norm = (scores) / (scores_max)
            # Sort and filter documents based on scores
            top_n = 5
            top_doc_idxs = np.argsort(-scores)[:top_n]

            top_docs = "\n"
            
            for idx, docs_idx in enumerate(top_doc_idxs):
                print(f"Rank: {idx+1}")
                print(f"Document: {documents[docs_idx]}\n")
                print(f"Score: {scores_norm[docs_idx]}\n")
                top_docs += (f"Phrase {idx+1}:{documents[docs_idx]}\n")

            response = co.chat(
            model="command-a-03-2025",
            messages=[
                    {  
                        "role": "system",
                        "content": "Explain why each phrase given suggests the email is a scam in the following format \nPhrase 1:\nPhrase 2: and so on"
                    },
                    {
                    "role": "user",
                    "content": email_content+top_docs,
                    }
                ],
            temperature = 0.1
            )

            #print (response.message.content[0].text)
            raw_reasons = re.findall(r'\*\*Reason:\*\*(.*?)\n', response.message.content[0].text)
            reasons = [reason.strip() for reason in raw_reasons]
        else:
            result = "safe"
            top_docs = "N/A"
            reasons = "N/A"
            scores_norm = [100]
        
        print(result)

        return ({
            "result": result,
            "scam_score": scam_score,
            "text": top_docs,
            "reason": reasons,
            "model": model,
            "scores": scores_norm*100
        })
     
     except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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
    
@email_blueprint.route('/setfolders', methods=["GET", "POST"])
def get_email():
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
        scam_result = detect_scam(email['Body'])  # Call the updated function
        """
            "result": result,
            "text": top_docs,
            "reason": reasons,
            "model": model,
            "scores": scores_norm
        """
        print(scam_result)
        results.append({"email": email, "scam_status": scam_result['result'], "confidence": round(scam_result['scores'][0])})  # Store both email and scam result

    return jsonify(results)  # Return results as JSON
