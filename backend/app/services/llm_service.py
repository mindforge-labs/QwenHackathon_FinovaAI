from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import ProcessingFailureError


class LLMService(Protocol):
    def is_enabled(self) -> bool: ...

    def extract_json(self, *, system_prompt: str, user_prompt: str) -> str: ...


@dataclass(slots=True)
class DisabledLLMService:
    reason: str = "LLM extraction is disabled."

    def is_enabled(self) -> bool:
        return False

    def extract_json(self, *, system_prompt: str, user_prompt: str) -> str:
        raise ProcessingFailureError(self.reason)


class OpenAICompatibleLLMService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def is_enabled(self) -> bool:
        return True

    def extract_json(self, *, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.settings.llm_base_url.rstrip('/')}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.settings.llm_api_key:
            headers["Authorization"] = f"Bearer {self.settings.llm_api_key}"

        payload = {
            "model": self.settings.llm_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProcessingFailureError("LLM extraction request failed.") from exc

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProcessingFailureError("LLM extraction response was missing message content.") from exc

        if not isinstance(content, str) or not content.strip():
            raise ProcessingFailureError("LLM extraction response was empty.")
        return content


def build_llm_service(settings: Settings | None = None) -> LLMService:
    config = settings or get_settings()
    if not config.llm_enabled:
        return DisabledLLMService()
    if not config.llm_model.strip():
        return DisabledLLMService("LLM extraction is enabled but LLM_MODEL is empty.")
    if not config.llm_base_url.strip():
        return DisabledLLMService("LLM extraction is enabled but LLM_BASE_URL is empty.")
    return OpenAICompatibleLLMService(config)
