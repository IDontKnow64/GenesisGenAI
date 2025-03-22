import os
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from routes.auth import auth_blueprint
from routes.emails import email_blueprint

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # Use Redis in production
app.secret_key = os.getenv("GOOGLE_API_KEY")
Session(app)
CORS(app)

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(email_blueprint, url_prefix='/emails')


@app.route('/')
def home():
    return {'message': 'Flask Backend Running'}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 
