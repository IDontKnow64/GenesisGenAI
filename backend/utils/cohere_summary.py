import cohere, os

def add_punctuation(line):
    # Strip extra spaces at the start and end of the line
    line = line.strip()
    if line and not line[-1] in ['.', '?', '!',":"]:
        return line + '.'
    return line

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
    