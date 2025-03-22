from flask import Flask
from flask_cors import CORS
from routes.auth import auth_blueprint
from routes.emails import email_blueprint

app = Flask(__name__)
CORS(app)


app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(email_blueprint, url_prefix='/emails')

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def home():
    return {'message': 'Flask Backend Running'}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 
