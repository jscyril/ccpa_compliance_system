"""
LLM Engine — Gemini API

Manages Google Gemini API for CCPA compliance analysis.
Supports configurable model selection (flash/pro) via settings.

The model is configured lazily via load() — called during FastAPI startup.
"""

import logging

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMEngine:
    """Manages Gemini API configuration and inference."""

    def __init__(self):
        self._model = None
        self._model_name = None

    @property
    def is_ready(self) -> bool:
        """Check if the Gemini API is configured and ready."""
        return self._model is not None

    def load(self) -> None:
        """
        Configure the Gemini API and create the model instance.

        Reads GEMINI_API_KEY and GEMINI_MODEL from settings.
        """
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY not set. "
                "Set it as an environment variable or in .env"
            )

        genai.configure(api_key=settings.GEMINI_API_KEY)

        self._model_name = settings.GEMINI_MODEL
        self._model = genai.GenerativeModel(self._model_name)

        logger.info(f"Gemini API configured with model: {self._model_name}")

    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt using the Gemini API.

        Args:
            prompt: The full prompt string.

        Returns:
            The generated text as a string.
        """
        if not self.is_ready:
            raise RuntimeError("Model not loaded. Call load() first.")

        response = self._model.generate_content(prompt)
        return response.text.strip()

    def generate_stream(self, prompt: str):
        """
        Generate text with streaming from the Gemini API.

        Yields text chunks as they arrive from the API.
        Used by the SSE endpoint in Phase 3.

        Args:
            prompt: The full prompt string.

        Yields:
            str: Text chunks from the Gemini API.
        """
        if not self.is_ready:
            raise RuntimeError("Model not loaded. Call load() first.")

        response = self._model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text


# Module-level singleton (loaded lazily via load())
llm_engine = LLMEngine()
