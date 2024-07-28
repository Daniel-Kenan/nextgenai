# groq_client.py

from groq import Groq

def get_groq_response(user_message):
    client = Groq(api_key='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')
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    
    return response

if __name__ == "__main__":
    print(get_groq_response("hello there. how are you?"))