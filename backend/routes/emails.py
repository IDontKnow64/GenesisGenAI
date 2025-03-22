from flask import Blueprint, jsonify, session
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

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