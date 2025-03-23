import cohere
import os
import numpy as np
from scipy.spatial.distance import cosine
import re
import nltk
from base64 import urlsafe_b64decode

def add_punctuation(line):
    """Adds punctuation to a line if it doesn't end with one."""
    line = line.strip()
    if line and not line[-1] in ['.', '?', '!', ":"]:
        return line + '.'
    return line

def detect_scam(email_content):
    """Detects if an email is a scam using Cohere's API."""
    api_key = os.getenv("CO_API_KEY")
    if not api_key:
        raise ValueError("CO_API_KEY environment variable not set")

    co = cohere.Client(api_key)

    # Classify the email as scam or safe
    response = co.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": "You respond with only either 'scam' or 'safe' for the given email"},
            {"role": "user", "content": email_content}
        ],
        temperature=0.0
    )

    classification = response.text.strip().lower()
    if classification == "scam":
        # Process the email content
        lines = email_content.split('\n')
        processed_lines = [add_punctuation(line) for line in lines]
        processed_email_content = '\n'.join(processed_lines)
        clean_content = re.sub(r'•⁠  ', '-', processed_email_content)
        clean_content = re.sub(r':', '.', clean_content)
        documents = nltk.sent_tokenize(clean_content)

        # Get embeddings for the documents
        doc_emb = co.embed(
            texts=documents,
            model="embed-english-v3.0",
            input_type="search_document"
        ).embeddings

        query = "Which parts of an email indicates that it is a scam?"
        query_emb = co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        ).embeddings

        # Calculate similarity scores
        scores = np.dot(query_emb, np.transpose(doc_emb))[0]
        scores_max = scores.max()
        scores_norm = scores / scores_max
        top_n = 5
        top_doc_idxs = np.argsort(-scores)[:top_n]

        top_docs = "\n".join([f"Phrase {idx+1}: {documents[docs_idx]}" for idx, docs_idx in enumerate(top_doc_idxs)])

        # Get reasons why the email is a scam
        response = co.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": "Explain why each phrase given suggests the email is a scam in the following format \nPhrase 1:\nPhrase 2: and so on"},
                {"role": "user", "content": email_content + top_docs}
            ],
            temperature=0.1
        )

        reasons = re.findall(r'\*\*Reason:\*\*(.*?)\n', response.text)
        cleaned_reasons = [reason.strip() for reason in reasons]
        return ["Scam", cleaned_reasons, round(scores_norm[top_doc_idxs[0]] * 100)]
    else:
        return ["Safe", "Reasons", 100]

def summarize_email(email_body):
    """Summarizes the email content using Cohere's API."""
    api_key = os.getenv("CO_API_KEY")
    if not api_key:
        raise ValueError("CO_API_KEY environment variable not set")

    co = cohere.Client(api_key)
    try:
        response = co.summarize(
            model="command-r",
            text=email_body,
            length="short",
            format="paragraph"
        )
        return response.summary
    except Exception as e:
        print(f"Error summarizing email: {e}")
        return email_body

def extract_email_body(email_data):
    """Extracts email body from raw email MIME structure."""
    try:
        if isinstance(email_data, str):
            return email_data.strip()

        parts = email_data.get('payload', {}).get('parts', [])
        body = None

        if not parts:
            body_data = email_data['payload']['body'].get('data', '')
            body = urlsafe_b64decode(body_data).decode('utf-8')
        else:
            for part in parts:
                mime_type = part.get('mimeType')
                if mime_type == 'text/plain':
                    body = urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
                elif mime_type == 'text/html':
                    body = urlsafe_b64decode(part['body']['data']).decode('utf-8')

        return body.strip() if body else None
    except Exception as e:
        print(f"Error extracting email body: {e}")
        return None

def get_embedding(text):
    """Generates embedding for a given text using Cohere API."""
    api_key = os.getenv("CO_API_KEY")
    if not api_key:
        raise ValueError("CO_API_KEY environment variable not set")

    co = cohere.Client(api_key)
    if not text:
        print("Warning: Email content is empty.")
        return np.zeros(1024)

    try:
        response = co.embed(
            model="embed-english-v3.0",
            texts=[text],
            input_type="search_document"
        )
        return np.array(response.embeddings[0])
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return np.zeros(1024)

def cosine_similarity(vec1, vec2):
    """Computes cosine similarity between two embeddings."""
    if vec1 is None or vec2 is None or len(vec1) == 0 or len(vec2) == 0:
        print("Warning: One or both vectors are missing. Returning similarity of 0.")
        return 0

    return 1 - cosine(vec1, vec2)

def classify_email_using_embeddings(email_body, folder_descriptions):
    """
    Classifies an email into a folder based on its similarity to predefined folder descriptions.
    :param email_body: The content of the email.
    :param folder_descriptions: Dictionary mapping folder names to their descriptions.
    :return: The best matching folder.
    """
    email_embedding = get_embedding(email_body)
    folder_embeddings = {folder: get_embedding(desc) for folder, desc in folder_descriptions.items()}

    best_match = "Uncategorized"
    best_score = 0

    for folder, folder_embedding in folder_embeddings.items():
        similarity = cosine_similarity(email_embedding, folder_embedding)
        print(f"Similarity with {folder}: {similarity:.4f}")

        if similarity > best_score:
            best_match = folder
            best_score = similarity

    if best_score < 0.1:
        best_match = "Uncategorized"

    return best_match


def generate_summary(email_content):
    api_key = os.getenv("CO_API_KEY")

    co = cohere.ClientV2(api_key)

    response = co.chat(
        model="command-a-03-2025",
        messages=[
                {  
                    "role": "system",
                    "content": "You respond with a summary of the email content and it should be in bullet points of main ideas."
                },
                {
                "role": "user",
                "content": email_content,
                }
            ],
        temperature = 0.0
    )

    print(response.message.content[0].text)
    return response.message.content[0].text
    