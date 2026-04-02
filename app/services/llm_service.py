"""
LLM Service — abstraction layer for LLM calls.
Supports OpenAI. Easily extendable to Gemini, Anthropic, etc.
"""

import json
import logging
from pathlib import Path
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Handles all LLM interactions with structured output parsing."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model

    def _load_prompt(self, prompt_name: str) -> str:
        """Load a prompt template from the prompts directory."""
        path = settings.prompts_dir / prompt_name
        if path.exists():
            return path.read_text().strip()
        logger.warning(f"Prompt file not found: {path}")
        return ""

    def call(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.2,
        max_tokens: int = 4000,
    ) -> str:
        """Make a raw LLM call and return the text response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def call_json(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> dict:
        """Make an LLM call expecting JSON output. Parses and returns dict."""
        raw = self.call(system_prompt, user_content, temperature, max_tokens)

        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last lines (```json and ```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}\nRaw: {raw[:500]}")
            return {"error": "Failed to parse LLM response", "raw": raw[:1000]}

    def call_with_prompt_file(
        self,
        prompt_filename: str,
        user_content: str,
        as_json: bool = True,
        **kwargs,
    ) -> dict | str:
        """Load a prompt file and make an LLM call."""
        system_prompt = self._load_prompt(prompt_filename)
        if not system_prompt:
            system_prompt = "You are a post-merger integration analysis assistant. Respond in valid JSON."

        if as_json:
            return self.call_json(system_prompt, user_content, **kwargs)
        return self.call(system_prompt, user_content, **kwargs)


# Singleton
llm_service = LLMService()
