"""Lightweight helper around OpenAI's chat completions API.

This module keeps every OpenAI-specific detail in one place so callers
can simply import `get_traduction_from_openai` and focus on the calling
logic.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import requests

OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
DEFAULT_MODEL = os.environ.get("OPENAI_TRANSLATION_MODEL", "gpt-4o-mini")
OPENAI_CREDENTIAL_PATH = Path(
    os.environ.get("OPENAI_CREDENTIAL_FILE", Path(__file__).with_name("openAI.cred"))
)
PROMPT_TEMPLATE = (
    "please provide a traduction for {word}, both in English, french and german. "
    "For each language you are only allowed to write 3 words maximum to convey the meaning. "
    "You should also add one short sentence with the {word} as an example"
)
SYSTEM_MESSAGE = "You are a multilingual dictionary specialized in concise translations."


class OpenAITranslationError(RuntimeError):
    """Raised when we fail to fetch a traduction from OpenAI."""


def _build_prompt(word: str) -> str:
    sanitized = word.strip()
    return PROMPT_TEMPLATE.format(word=sanitized or "the provided word")


def _read_api_key() -> str:
    """Read the API key from the `openAI.cred` file (or override path)."""

    try:
        api_key = OPENAI_CREDENTIAL_PATH.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise OpenAITranslationError(
            f"Unable to read OpenAI credentials from {OPENAI_CREDENTIAL_PATH}: {exc}"
        ) from exc

    if not api_key:
        raise OpenAITranslationError(
            f"OpenAI credential file {OPENAI_CREDENTIAL_PATH} is empty."
        )
    return api_key


def get_traduction_from_openai(word: str, *, timeout: Optional[float] = 15.0) -> str:
    """Return OpenAI's traduction suggestion for `word`.

    Args:
        word: The vocabulary entry we want translated.
        timeout: Optional timeout (seconds) for the HTTP call.

    Raises:
        OpenAITranslationError: If the API key is missing or the call fails.
    """

    api_key = _read_api_key()

    model = DEFAULT_MODEL
    if not model:
        raise OpenAITranslationError("OpenAI model is not configured.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": _build_prompt(word)},
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OPENAI_API_URL, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        body = response.json()
    except requests.RequestException as exc:  # pragma: no cover - network layer
        raise OpenAITranslationError(f"Failed to reach OpenAI: {exc}") from exc

    try:
        message = body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError) as exc:
        raise OpenAITranslationError("Invalid response structure from OpenAI.") from exc

    if not message:
        raise OpenAITranslationError("OpenAI returned an empty traduction.")

    return message
