"""
Phase 4 LLM Engine: Groq API client.
"""

import logging
from typing import Optional

from groq import Groq

from .config import get_groq_api_key
from .prompt_builder import SYSTEM_PROMPT

try:
    from observability.llm_monitor import monitored_llm_call
except ImportError:
    def monitored_llm_call(f):
        return f


logger = logging.getLogger(__name__)

MODEL = "mixtral-8x7b-32768"
TEMPERATURE = 0.3


@monitored_llm_call
def call_groq_llm(prompt: str) -> str:
    """
    Call Groq LLM with the given prompt.

    Args:
        prompt: User prompt content (context for recommendation).

    Returns:
        Raw LLM response text.

    Raises:
        ValueError: If API key is missing.
        Exception: On API errors after retry.
    """
    api_key = get_groq_api_key()
    client = Groq(api_key=api_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    for attempt in range(2):
        try:
            logger.info("Calling Groq API (attempt %d)", attempt + 1)
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            logger.info("Groq API call successful")
            return content
        except Exception as e:
            logger.warning("Groq API attempt %d failed: %s", attempt + 1, str(e))
            if attempt == 1:
                raise

    return ""
