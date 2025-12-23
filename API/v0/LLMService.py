from dotenv import load_dotenv
from google import genai
from mistralai import Mistral
from google.genai import types
import os

client = None


def LLMChat(prompt, model):
    if model == 'gemini':
        return gemini_chat(prompt)
    elif model == 'mistral':
        return mistral_chat(prompt)


def gemini_chat(prompt):
    client = gemini_init()
    llm_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return llm_response.text


def gemini_init():
    if client != None:
        return client
    load_dotenv()
    return genai.Client()


def mistral_chat(prompt):
    with Mistral(
        api_key=os.getenv("MISTRAL_API_KEY", ""),
    ) as mistral:

        res = mistral.chat.complete(model="mistral-small-latest", messages=[
            {
                "content": prompt,
                "role": "user",
            },
        ], stream=False)

        return res.choices[0].message.content


def embed(texts, batch_size=100):
    client = gemini_init()
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        response = client.models.embed_content(
            model="text-embedding-004",
            contents=batch,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
        ).embeddings

        batch_vectors = [e.values for e in response]
        vectors.extend(batch_vectors)

    return vectors
