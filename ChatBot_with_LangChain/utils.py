import os
from dotenv import load_dotenv
import openai

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4-1106-preview"
EMBEDDING_MODEL = "text-embedding-ada-002"
client = openai.OpenAI()


def get_embedding(text):
    if text:
        try:
            response = openai.embeddings.create(input=text, model=EMBEDDING_MODEL)
            return response.data[0].embedding
        except Exception as e:
            print(f"OpenAI API call error: {str(e)}")

    return None


def get_gpt_response(system_message, user_message):

    response = None
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",
                 "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        response = completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API call error: {str(e)}")
    return response