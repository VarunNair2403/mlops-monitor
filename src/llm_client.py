import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_narrative(prompt: str) -> str:
    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
    )
    return resp.choices[0].message.content