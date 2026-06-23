import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Matches opening fences: ```json, ```JSON, ``` etc.
_FENCE_OPEN = re.compile(r"^```[a-zA-Z]*\s*", re.MULTILINE)
_FENCE_CLOSE = re.compile(r"```\s*$", re.MULTILINE)


def parse_llm_response(raw: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse a raw LLM string response to a dict.

    Strips markdown code fences (```json ... ``` or ``` ... ```) before
    attempting JSON parsing. Used by every agent to clean LLM output.

    Args:
        raw: The raw string returned by the LLM.

    Returns:
        A parsed dict if successful, or None if parsing fails.
    """
    cleaned = _strip_code_fences(raw)
    cleaned = _escape_unescaped_newlines(cleaned)
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
        logger.warning(
            "json_validator: parsed JSON is not a dict (got %s), returning None.",
            type(result).__name__,
        )
        return None
    except json.JSONDecodeError as exc:
        logger.error(
            "json_validator: JSON parse error — %s | cleaned input: %.200s",
            exc,
            cleaned,
        )
        return None


def _strip_code_fences(text: str) -> str:
    """
    Remove markdown code fences from LLM output.

    Handles all of:
      - ```json\\n{...}\\n```
      - ```\\n{...}\\n```
      - {... raw JSON without fences ...}

    Args:
        text: Raw LLM response string, possibly wrapped in markdown fences.

    Returns:
        The inner content with fences stripped and whitespace trimmed.
    """
    text = text.strip()

    # Fast path: no fence present
    if not text.startswith("```"):
        return text

    # Remove the opening fence line (e.g. ```json or ```)
    text = _FENCE_OPEN.sub("", text, count=1)
    # Remove the closing fence
    text = _FENCE_CLOSE.sub("", text)

    return text.strip()


def _escape_unescaped_newlines(text: str) -> str:
    """
    Escapes literal newlines and control characters inside JSON strings.
    The LLM often writes literal newlines inside 'email_body' strings, which breaks json.loads.
    """
    in_string = False
    escaped = False
    result = []
    for char in text:
        if in_string:
            if char == '"' and not escaped:
                in_string = False
            elif char == '\\' and not escaped:
                escaped = True
            else:
                escaped = False
            
            if char == '\n':
                result.append('\\n')
                continue
            elif char == '\r':
                result.append('\\r')
                continue
            elif char == '\t':
                result.append('\\t')
                continue
        else:
            if char == '"':
                in_string = True
        result.append(char)
    return "".join(result)
