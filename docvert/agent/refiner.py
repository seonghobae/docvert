"""LLM-powered markdown refinement module."""

import os
from typing import Optional, Any
from loguru import logger

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


class LLMRefiner:
    """An LLM-powered agent to refine and fix markdown structure.

    Attributes:
        client (OpenAI): The OpenAI client instance.
        model (str): The model to use for refinement.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initializes the LLMRefiner.

        Args:
            api_key (str, optional): The OpenAI API key. Defaults to environment variable.
            model (str, optional): The OpenAI model. Defaults to "gpt-4o-mini".

        Raises:
            ImportError: If openai package is not installed.
        """
        if OpenAI is None:
            raise ImportError(
                "The 'openai' package is required for the agent. Run `pip install openai`."
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def refine_markdown(self, raw_markdown: str) -> str:
        """Refines raw markdown by fixing structural and OCR errors via LLM.

        Args:
            raw_markdown (str): The raw markdown string to refine.

        Returns:
            str: The refined markdown string.
        """
        logger.info(f"Refining markdown using {self.model}...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert document structural editor. "
                            "Refine the following Markdown text. "
                            "Fix reading order, semantic structure, and obvious OCR/parsing typos. "
                            "Return only the valid, clean Markdown. Do not add conversational filler."
                        ),
                    },
                    {
                        "role": "user",
                        "content": raw_markdown,
                    },
                ],
                temperature=0.1,
            )
            refined = response.choices[0].message.content
            return refined.strip() if refined else raw_markdown
        except Exception as e:
            logger.error(f"LLM refinement failed: {e}")
            return raw_markdown
