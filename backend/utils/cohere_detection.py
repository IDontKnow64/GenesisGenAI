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

# def detect_scam(email_content):
#     """Detects if an email is a scam using Cohere's API."""
#     api_key = os.getenv("CO_API_KEY")
#     if not api_key:
#         raise ValueError("CO_API_KEY environment variable not set")

#     co = cohere.ClientV2(api_key)

#     # Classify the email as scam or safe
#     response = co.chat(
#         model="command-a-03-2025",
#         messages=[
#             {"role": "system", "content": "You are an expert at detecting fraud or phishing emails. You know exactly what key markers make a fraud email. Given an email, determine whether it is safe or fraudulent by only responding with either 'scam' or 'safe' for the given email. Do not add any additional punctuation."},
#             {"role": "user", "content": email_content}
#         ],
#         temperature=0.0
#     )

#     classification = response.message.content[0].text.strip().lower()
#     print(f"{classification = }")
#     if classification == "scam":
#         # Process the email content
#         lines = email_content.split('\n')
#         processed_lines = [add_punctuation(line) for line in lines]
#         processed_email_content = '\n'.join(processed_lines)
#         clean_content = re.sub(r'•⁠  ', '-', processed_email_content)
#         clean_content = re.sub(r':', '.', clean_content)
#         documents = nltk.sent_tokenize(clean_content)

#         # Get embeddings for the documents
#         doc_emb = co.embed(
#             texts=documents,
#             model="embed-english-v3.0",
#             input_type="search_document"
#         ).embeddings

#         query = "Which parts of an email indicates that it is a scam?"
#         query_emb = co.embed(
#             texts=[query],
#             model="embed-english-v3.0",
#             input_type="search_query"
#         ).embeddings

#         # Calculate similarity scores
#         scores = np.dot(query_emb, np.transpose(doc_emb))[0]
#         scores_max = scores.max()
#         scores_norm = scores / scores_max
#         top_n = 5
#         top_doc_idxs = np.argsort(-scores)[:top_n]

#         top_docs = "\n".join([f"Phrase {idx+1}: {documents[docs_idx]}" for idx, docs_idx in enumerate(top_doc_idxs)])
#         print(f"{top_docs = }")
#         # Get reasons why the email is a scam
#         response = co.chat(
#             model="command-a-03-2025",
#             messages=[
#                 {"role": "system", "content": "Explain why each phrase given suggests the email is a scam in the following format \nPhrase 1:\nPhrase 2: and so on"},
#                 {"role": "user", "content": email_content + top_docs}
#             ],
#             temperature=0.1
#         )

#         reasons = re.findall(r'\*\*Reason:\*\*(.*?)\n', response.message.content[0].text)
#         cleaned_reasons = [reason.strip() for reason in reasons]
#         print(f"{cleaned_reasons = }")
#         return ("Scam", cleaned_reasons, round(scores_norm[top_doc_idxs[0]] * 100))
#     else:
#         return ("Safe", [""], 100)
def detect_scam(email_content: str) -> tuple[str, list[str], float]:
    """Detects if an email is a scam using Cohere's API with proper error handling."""
    try:
        # 1. Validate environment
        api_key = os.getenv("CO_API_KEY")
        if not api_key:
            raise ValueError("CO_API_KEY environment variable not set")

        # 2. Initialize Cohere client (using correct client class)
        co = cohere.Client(api_key)  # Changed from ClientV2 to Client

        # 3. Classify email
        classification_response = co.chat(
            model="command-a-03-2025",
            message=email_content,  # Simplified message format
            preamble="Classify this email as 'scam' or 'safe' only. Look for:\n- Urgent language\n- Suspicious links\n- Unusual requests\n- Grammar mistakes",
            temperature=0.0
        )

        # 4. Safely extract classification
        classification = classification_response.text.strip().lower()
        if 'scam' not in classification and 'safe' not in classification:
            return ("Invalid response", ["Could not determine scam status"], 0.0)

        if 'safe' in classification:
            return ("Safe", [], 100.0)

        # 5. Process scam content with error checking
        try:
            # Simplified content processing
            clean_content = re.sub(r'[•⁠]+', '-', email_content)
            documents = nltk.sent_tokenize(clean_content)[:10]  # Limit to first 10 sentences

            if not documents:
                return ("Scam", ["Suspicious content patterns detected"], 95.0)

            # 6. Get embeddings with batch processing
            batch_size = 32
            doc_embeddings = []
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                emb_response = co.embed(
                    texts=batch,
                    model="embed-english-v3.0",
                    input_type="search_document"
                )
                doc_embeddings.extend(emb_response.embeddings)

            # 7. Similarity calculation with numpy
            query = "Identify scam indicators in email content"
            query_emb = co.embed(
                texts=[query],
                model="embed-english-v3.0",
                input_type="search_query"
            ).embeddings[0]

            scores = np.dot([query_emb], np.array(doc_embeddings).T)[0]
            top_idx = np.argmax(scores)
            confidence = float(scores[top_idx] * 100)

            # 8. Get explanations with improved prompt
            explanation_response = co.chat(
                model="command-a-03-2025",
                message=f"Explain why this email is suspicious:\n{documents[top_idx]}",
                temperature=0.1
            )

            # 9. Safely extract reasons
            reasons = [explanation_response.text]
            return ("Scam", reasons, min(confidence, 100.0))

        except Exception as processing_error:
            print(f"Content processing error: {processing_error}")
            return ("Scam", ["Potential scam detected"], 85.0)

    except cohere.CohereError as cohere_error:
        print(f"Cohere API Error: {cohere_error}")
        return ("Error", [f"API Error: {str(cohere_error)}"], 0.0)
        
    except Exception as general_error:
        print(f"General Error: {general_error}")
        return ("Error", [f"Processing Error: {str(general_error)}"], 0.0)


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
                    "content": "You are an expert at summarizing emails, with a passion for communicating information efficiently with others. You, as an expert summarizer, are tasked with taking in boring emails and summarizing them in a concise manner, responding with a summary of the email content. In addition, you should never use any markdown or latex in your responses as if you were writing a summary for a daily standup meeting. Make sure to convey an exited and informative tone."
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
    