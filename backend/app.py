from flask import Flask
from flask_cors import CORS
import os
import cohere
from dotenv import load_dotenv

"""
load_dotenv()
api_key = os.getenv("CO_API_KEY")
    
co = cohere.ClientV2(api_key)
    
response = co.chat(
        model="command-r-plus-08-2024",
        messages=[{"role": "user", "content": "hello world!"}],
)
    
message_response = response.message.content[0].text
print(message_response)"""

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return {'message': 'Flask Backend Running'}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 
