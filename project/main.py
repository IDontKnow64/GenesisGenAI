import os
import cohere
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":

    api_key = os.getenv("CO_API_KEY")
    
    co = cohere.ClientV2(api_key)
    
    response = co.chat(
        model="command-r-plus-08-2024",
        messages=[{"role": "user", "content": "hello world!"}],
    )
    
    message_response = response.message.content[0].text
    print(message_response)