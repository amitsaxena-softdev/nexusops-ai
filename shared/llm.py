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


def _config(system_instruction: str = None) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0,
    )


def ask(prompt: str, system_instruction: str = None) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=_config(system_instruction),
    )
    return response.text


def ask_with_file(prompt: str, file_bytes: bytes, mime_type: str, system_instruction: str = None) -> str:
    client = _get_client()
    part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model=MODEL,
        contents=[part, prompt],
        config=_config(system_instruction),
    )
    return response.text


def chat(system_instruction: str = None):
    client = _get_client()
    return client.chats.create(model=MODEL, config=_config(system_instruction))
