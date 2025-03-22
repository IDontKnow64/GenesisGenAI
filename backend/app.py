import os
import cohere
import numpy as np
import nltk
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_session import Session
from routes.auth import auth_blueprint
from routes.emails import email_blueprint
from dotenv import load_dotenv

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()
nltk.download('punkt_tab')

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # Use Redis in production
app.secret_key = os.getenv("GOOGLE_API_KEY")
Session(app)
CORS(app)

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(email_blueprint, url_prefix='/emails')

api_key = os.getenv("CO_API_KEY")

if not api_key:
    print("Cohere API key not found.")

@app.route('/')
def home():
    return {'message': 'Flask Backend Running'}

def add_punctuation(line):
    # Strip extra spaces at the start and end of the line
    line = line.strip()
    if line and not line[-1] in ['.', '?', '!',":"]:
        return line + '.'
    return line

@app.route('/api/generate', methods=['POST'])
def detect_scam():
     """
     JSON:
     {
        "model": model
        "email_content": email_content
        "temperature": temperature
     }
     """
     
     data = request.json

     if not data or 'email_content' not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

     email_content = data.get('email_content')
     model = data.get('model', 'command-a-03-2025')
     temperature = data.get('temperature','0.1')

     try:

        co = cohere.ClientV2(api_key)

        response = co.chat(
            model=model,
            messages=[
                    {  
                        "role": "system",
                        "content": "You respond with only either 'scam' or 'safe' for the given email"
                    },
                    {
                    "role": "user",
                    "content": email_content,
                    }
                ],
            temperature = temperature
        )

        #print (response.message.content[0].text)

        if ("Verdict: Scam" in response.message.content[0].text):
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
            scores_norm = [0]
        
        print(result)

        return jsonify({
            "result": result,
            "text": top_docs,
            "reason": reasons,
            "model": model,
            "scores": scores_norm
        })

    
     
     except Exception as e:
        return jsonify({"error": str(e)}), 500
     
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"})
     
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 
