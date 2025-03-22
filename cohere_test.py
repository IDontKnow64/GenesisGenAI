from API_KEY import KEY
import cohere

co = cohere.ClientV2(KEY)

response = co.chat(model="command-a-03-2025", messages=[{"role": "user", "content": "tell me about university of toronto"}])

print(response)