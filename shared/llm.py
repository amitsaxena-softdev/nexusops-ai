import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-2.5-flash"

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def ask(prompt: str, system_instruction: str = None) -> str:
    client = _get_client()
    config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config,
    )
    return response.text


def ask_with_file(prompt: str, file_bytes: bytes, mime_type: str, system_instruction: str = None) -> str:
    client = _get_client()
    config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
    part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model=MODEL,
        contents=[part, prompt],
        config=config,
    )
    return response.text


def chat(system_instruction: str = None):
    client = _get_client()
    config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
    return client.chats.create(model=MODEL, config=config)
