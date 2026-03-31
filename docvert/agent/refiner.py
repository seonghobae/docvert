"""LLM-powered markdown refinement module."""

import os
from typing import Optional
from loguru import logger

try:
    from litellm import completion
    import litellm
except ImportError:
    completion = None


class LLMRefiner:
    """An LLM-powered agent to refine and fix markdown structure.

    Attributes:
        model (str): The model to use for refinement.
        api_key (str, optional): The API key for the provider.
        base_url (str, optional): Custom base URL.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
    ):
        """Initializes the LLMRefiner.

        Args:
            api_key (str, optional): The API key. Defaults to environment variable.
            model (str, optional): The model name (litellm format). Defaults to "gpt-4o-mini".
            base_url (str, optional): Custom base URL for compatible APIs. Defaults to relevant env var.

        Raises:
            ImportError: If litellm package is not installed.
        """
        if completion is None:
            raise ImportError(
                "The 'litellm' package is required for the agent. Run `pip install litellm`."
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model

        # Suppress verbose litellm logging if desired
        litellm.suppress_debug_info = True

    def refine_markdown(self, raw_markdown: str) -> str:
        """Refines raw markdown by fixing structural and OCR errors via LLM.

        Args:
            raw_markdown (str): The raw markdown string to refine.

        Returns:
            str: The refined markdown string.
        """
        logger.info(f"Refining markdown using {self.model}...")
        try:
            kwargs = {
                "model": self.model,
                "messages": [
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
                "temperature": 0.1,
            }
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url

            response = completion(**kwargs)
            refined = response.choices[0].message.content
            return refined.strip() if refined else raw_markdown
        except Exception as e:
            logger.error(f"LLM refinement failed: {e}")
            return raw_markdown
