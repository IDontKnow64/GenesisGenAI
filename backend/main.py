import os
import cohere
import numpy as np
import nltk
import re
from dotenv import load_dotenv

load_dotenv()
nltk.download('punkt_tab')

def add_punctuation(line):
    # Strip extra spaces at the start and end of the line
    line = line.strip()
    if line and not line[-1] in ['.', '?', '!',":"]:
        return line + '.'
    return line

if __name__ == "__main__":

    api_key = os.getenv("CO_API_KEY")

    co = cohere.ClientV2(api_key)

    with open("email_test.txt","r", encoding='utf-8') as file:
            email_content = file.read()

    response = co.chat(
        model="command-a-03-2025",
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
        temperature = 0.0
    )

    print (response.message.content[0].text)

    if (response.message.content[0].text == "scam"):
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
        reasons = re.findall(r'\*\*Reason:\*\*(.*?)\n', response.message.content[0].text)
        cleaned_reasons = [reason.strip() for reason in reasons]
    else:
        print("Safe")