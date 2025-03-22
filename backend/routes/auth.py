import os
from google_auth_oauthlib.flow import Flow
from flask import redirect, session, request, Blueprint, jsonify

client_config = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
    }
}

flow = Flow.from_client_config(
    client_config=client_config,
    scopes=['https://www.googleapis.com/auth/gmail.readonly'],
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
)

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login')
def login():
    # Handle login logic
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'  # Force refresh token
    )
    session['oauth_state'] = state
    print(f"User Logging in")
    return redirect(authorization_url)

@auth_blueprint.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    
    # Verify state matches
    if session['oauth_state'] != request.args.get('state'):
        return f"State mismatch {session['oauth_state']} != {request.args.get('state')}", 403
    
    # Get credentials
    credentials = flow.credentials
    
    # Store credentials in DB (example using simple session)
    session['google_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect("http://localhost:5173/")
