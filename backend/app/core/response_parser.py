"""
Response Parser

Extracts and validates JSON from LLM output. Implements the confidence
fallback strategy (ADR-4): if parsing fails or output is ambiguous,
return {"harmful": false, "articles": []} to avoid the "zero marks" trap.

Priority: Never cite a wrong article. It's better to miss a violation
than to guess incorrectly.
"""

import json
import logging
import re

logger = logging.getLogger(__name__)

# Default safe response — returned when parsing fails
SAFE_DEFAULT = {"harmful": False, "articles": []}


def parse_response(raw_output: str) -> dict:
    """
    Parse LLM output into a validated response dict.

    Extraction strategy (in order):
    1. Direct JSON parse
    2. Extract from markdown code fence
    3. Regex extract {...} pattern

    Validation rules:
    - harmful must be bool
    - articles must be list of strings
    - If harmful=false, articles must be []
    - If harmful=true, articles must be non-empty (else fallback)

    Args:
        raw_output: Raw text from the LLM.

    Returns:
        Validated dict: {"harmful": bool, "articles": list[str]}
        Never raises — always returns valid output.
    """
    try:
        data = _extract_json(raw_output)
        if data is None:
            logger.warning("Could not extract JSON from LLM output")
            return SAFE_DEFAULT.copy()

        return _validate_and_normalize(data)

    except Exception as e:
        logger.error(f"Response parsing failed: {e}")
        return SAFE_DEFAULT.copy()


def _extract_json(text: str) -> dict | None:
    """Try multiple strategies to extract JSON from text."""
    text = text.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 2: Extract from markdown code fence
    fence_match = re.search(
        r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL
    )
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 3: Find first {...} pattern
    brace_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 4: Find nested {...} with inner braces (for complex JSON)
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def _validate_and_normalize(data: dict) -> dict:
    """Validate structure and normalize article format."""
    if not isinstance(data, dict):
        logger.warning(f"Expected dict, got {type(data)}")
        return SAFE_DEFAULT.copy()

    # Extract harmful flag
    harmful = data.get("harmful")
    if isinstance(harmful, str):
        harmful = harmful.lower() in ("true", "yes", "1")
    elif not isinstance(harmful, bool):
        logger.warning(f"Invalid 'harmful' value: {harmful}")
        return SAFE_DEFAULT.copy()

    # Extract articles
    articles = data.get("articles", [])
    if not isinstance(articles, list):
        logger.warning(f"Invalid 'articles' type: {type(articles)}")
        return SAFE_DEFAULT.copy()

    # Normalize article format
    normalized_articles = []
    for article in articles:
        if not isinstance(article, str):
            continue
        normalized = _normalize_article(article)
        if normalized:
            normalized_articles.append(normalized)

    # ADR-4: Confidence fallback
    # If harmful=true but no valid articles → fallback to safe
    if harmful and not normalized_articles:
        logger.warning(
            "harmful=true but no valid articles — "
            "falling back to safe default (ADR-4)"
        )
        return SAFE_DEFAULT.copy()

    # If harmful=false, ensure articles is empty
    if not harmful:
        normalized_articles = []

    return {
        "harmful": harmful,
        "articles": normalized_articles,
    }


def _normalize_article(article: str) -> str | None:
    """
    Normalize an article reference to 'Section 1798.xxx' format.

    Handles:
    - "1798.120" → "Section 1798.120"
    - "Section 1798.120(a)" → "Section 1798.120(a)"
    - "Article 1798.120" → "Section 1798.120"
    - "§1798.120" → "Section 1798.120"
    """
    article = article.strip()

    # Extract the section number pattern
    match = re.search(r"(1798\.\d+(?:\.\d+)?(?:\([a-z0-9]+\))*)", article)
    if not match:
        logger.warning(f"Could not parse article reference: {article}")
        return None

    section_num = match.group(1)
    return f"Section {section_num}"
