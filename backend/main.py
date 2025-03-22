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
                "role": "user",
                "content": 'Identify if this email is a scam. If so, say "scam"\n\n'+email_content,
                }
            ],
        temperature = 0.1
    )

    print (response.message)

    if ("Verdict: Scam" in response.message.content[0].text):
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
        
        # response = co.chat(
        #     model="command-r-plus-08-2024",
        #     messages=[{"role": "user", "content": "hello world!"}],
        # )

        scores = np.dot(query_emb, np.transpose(doc_emb))[0]
        # Sort and filter documents based on scores
        top_n = 5
        top_doc_idxs = np.argsort(-scores)[:top_n]
        
        for idx, docs_idx in enumerate(top_doc_idxs):
            print(f"Rank: {idx+1}")
            print(f"Document: {documents[docs_idx]}\n")

    else:
        print("Safe")