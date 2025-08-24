import os
import json
import httpx
from typing import Generator
from django.conf import settings

from .prompts import SYSTEM_PROMPT



def complete(prompt: str) -> str:
    provider = getattr(settings, "LLM_PROVIDER", None)
    if provider == 'ollama':
        return _ollama_complete(prompt)
    elif provider == 'openai':
        return _openai_complete(prompt)
    else:
        raise NotImplementedError('Custom LLM provider not implemented')


def _ollama_complete(prompt: str) -> str:
    url = settings.OLLAMA_URL
    model = settings.LLM_MODEL
    text = []

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    with httpx.stream("POST", url, json=payload, timeout=120) as r:
        for line in r.iter_lines():
            if not line:
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            if "response" in j:
                text.append(j["response"])
            if j.get("done", False):
                break

    return "".join(text)


def _openai_complete(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content
