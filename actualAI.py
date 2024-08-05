import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_groq_response(user_message, memory):
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)
    
    # Construct the messages list including the memory context
    messages = [
        {"role": "user", "content": msg} for msg in memory
    ] + [{"role": "user", "content": user_message}]

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
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




# completion = client.chat.completions.create(
#     model="llama3-70b-8192",
#     messages=[
#         {
#             "role": "user",
#             "content": "Build a custom resume for this job posting here is the resume:" + resume + "  and here is the job description " + jobDescription
#         },
#         {
#             "role": "assistant",
#             "content": "Please provide the job posting details, and I'll create a custom resume tailored to the job requirements.\n\nPlease provide the following information:\n\n1. Job title\n2. Job description\n3. Requirements (e.g., skills, experience, education)\n4. Any specific keywords or phrases mentioned in the job posting\n\nOnce I have this information, I'll create a custom resume that highlights your relevant skills and experiences, increasing your chances of getting noticed by the hiring manager."
#         }
#     ],
#     temperature=1,
#     max_tokens=1024,
#     top_p=1,
#     stream=False,
#     stop=None,
# )
