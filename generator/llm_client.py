"""OpenAI-compatible LLM client used by QYIR generation."""

from __future__ import annotations

import os
from typing import Protocol


DEFAULT_MODEL = "gpt-4o-mini"


class LLMClient(Protocol):
    """Minimal protocol that keeps generation easy to mock in tests."""

    def generate(self, prompt: str) -> str:
        """Return raw model text for a prompt."""


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM client cannot be configured."""


class OpenAILLMClient:
    """Small OpenAI chat-completions client configured from environment."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.base_url = base_url if base_url is not None else os.getenv("OPENAI_BASE_URL")
        self.model = model if model is not None else os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

        if not self.api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is required to generate QYIR. "
                "Set OPENAI_API_KEY, and optionally OPENAI_BASE_URL and OPENAI_MODEL."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMConfigurationError(
                "The openai package is required. Install project dependencies before using run_qsga.py."
            ) from exc

        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self._client = OpenAI(**kwargs)

    def generate(self, prompt: str) -> str:
        """Generate raw text from the configured OpenAI-compatible model."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate strict QYIR JSON only. "
                        "Never return Python, markdown, or prose."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content
        if not content:
            return ""
        return content
