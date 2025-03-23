import os
from google_auth_oauthlib.flow import Flow
from flask import redirect, session, request, Blueprint, jsonify
import secrets


client_config = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
    }
}

def get_flow():
    return Flow.from_client_config(
        client_config=client_config,
        scopes=['https://www.googleapis.com/auth/gmail.readonly'],
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login')
def login():
    # Handle login logic
    flow = get_flow()

    # print(f"V1 = {session.get('oauth_state2') = }")
    # Generate and store state FIRST
    session.clear()
    # print(f"V2 = {session.get('oauth_state2') = }")
    state = secrets.token_urlsafe(32)
    session['oauth_state2'] = state
    print(f"I am trying to log in with {session['oauth_state2'] = }!")
    session.permanent = True  # Required for server-side sessions
    
    # Force session save before redirect
    session.modified = True
    session.sid  # Access session ID to trigger save

    authorization_url = flow.authorization_url(
        state=state,
        access_type='offline',
        prompt='consent'  # Force refresh token
    )[0]

    # print(f'''
    # [LOGIN] New State Generated:
    # - Session ID: {session.sid}
    # - State: {state}
    # - Authorization URL: {authorization_url}
    # ''')

    # print(f"V3 = {session.get('oauth_state2') = }")
    # print(f"Login: {session = }")

    # print(f"[LOGIN] Before Redirect - Stored State: {session.get('oauth_state2')}, Session ID: {session.sid if hasattr(session, 'sid') else 'N/A'}")
    # print(f"User Logging in\nReturning: {authorization_url}")

    response = redirect(authorization_url)
    response.set_cookie(
        key='oauth_state',
        value=state,
        domain=None,  # Critical!
        path='/',
        max_age=300,  # 5 minutes
        secure=False,  # True in production
        httponly=True,
        samesite='Lax'
    )

    session['test_field'] = state
    print(f"I am trying to log in with {session['test_field'] = }!")

    return response

@auth_blueprint.route('/callback')
def callback():
    flow = get_flow()
    # print(f"Callback: {session = }")
    # stored_state = session.get('oauth_state2')
    print(f"I finished calling with {session['test_field'] = }!")
    print(f"I finished calling with {session['oauth_state2'] = }!")

    stored_state = request.cookies.get('oauth_state')
    print(f"{stored_state = }")
    request_state = request.args.get('state')
    # print(f"[CALLBACK] Session Before State Check: {session.items()}")  
    # Log state comparison
    # print(f'''
    # [CALLBACK] State Check:
    # - Session ID: {session.sid}
    # - Stored State: {stored_state}
    # - Received State: {request_state}
    # - Match: {stored_state == request_state}
    # ''')

    
    if not stored_state or stored_state != request_state:
        print(f'''
            State Mismatch!
            Session ID: {session.sid}
            Stored: {stored_state}
            Received: {request_state}
        ''')

    # Get credentials
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    print(f"I just logged in with {session['test_field'] = }!")

    
    # Store credentials in DB (example using simple session)
    session['google_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect("http://localhost:5173/mail")
