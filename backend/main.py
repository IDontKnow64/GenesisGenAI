import os
import backend.main as main
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    api_key = os.getenv("CO_API_KEY")
    co = main.ClientV2(api_key)
    
    response = co.chat(
        model="command-a-03-2025", 
        messages=[{"role": "user", "content": "hello world!"}],
    )
    
    message_response = response.message.content[0].text
    print(message_response)