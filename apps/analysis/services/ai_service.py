import json
import logging
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Keep comment text under ~40k chars to stay fast and cheap
MAX_COMMENT_CHARS = 40_000

_SYSTEM_PROMPT = """\
You are an expert YouTube analytics assistant for content creators.

Analyze the provided YouTube comments and return a JSON object with this exact schema:

{
  "summary": "2-3 sentence overview of overall comment themes and audience mood",
  "sentiment": "positive" | "negative" | "mixed" | "neutral",
  "audience_type": "brief description of the audience (e.g. 'tech enthusiasts aged 18-30')",
  "topics": [
    { "topic": "topic name", "relevance_score": <float 0.0-1.0> }
  ],
  "suggestions": [
    { "suggestion": "actionable suggestion for the creator", "category": "content" | "engagement" | "growth" | "monetization" }
  ],
  "questions": [
    { "question": "a question commonly asked in comments", "answer": "suggested answer" }
  ]
}

Rules:
- Return valid JSON only — no markdown, no code fences, no extra text.
- Provide 3-6 topics ordered by relevance_score descending.
- Provide 3-5 suggestions varied across categories.
- Provide 3-5 questions that real viewers asked.
- All relevance_score values must be between 0.01 and 1.00.\
"""


def analyze_comments(comments: list[str], channel_info: dict) -> dict:
    """Send comments to DeepSeek and return a validated result dict."""
    if not comments:
        return _empty_result()

    comment_block = _trim_comments(comments)
    channel_name = channel_info.get("title", "Unknown Channel")

    user_message = (
        f"Channel: {channel_name}\n\n"
        f"Total comments in dataset: {len(comments)}\n\n"
        f"Comment sample:\n{comment_block}"
    )

    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=2048,
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    logger.debug("DeepSeek raw response for %r: %s", channel_name, raw[:200])

    return _parse_and_validate(raw)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _trim_comments(comments: list[str]) -> str:
    lines = [f"- {c.strip()}" for c in comments if c.strip()]
    joined = "\n".join(lines)
    if len(joined) > MAX_COMMENT_CHARS:
        joined = joined[:MAX_COMMENT_CHARS]
        last_newline = joined.rfind("\n")
        if last_newline > 0:
            joined = joined[:last_newline]
        joined += "\n[...truncated for length]"
    return joined


def _parse_and_validate(raw: str) -> dict:
    text = raw
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]

    try:
        data = json.loads(text.strip())
    except json.JSONDecodeError as exc:
        logger.error("DeepSeek returned non-JSON: %s", raw[:500])
        raise ValueError(f"AI returned non-JSON response: {exc}") from exc

    return {
        "summary": str(data.get("summary", "")),
        "sentiment": _valid_sentiment(data.get("sentiment", "neutral")),
        "audience_type": str(data.get("audience_type", "")),
        "topics": _valid_topics(data.get("topics", [])),
        "suggestions": _valid_suggestions(data.get("suggestions", [])),
        "questions": _valid_questions(data.get("questions", [])),
    }


def _valid_sentiment(value: str) -> str:
    from apps.analysis.models.enums import SentimentChoices
    allowed = {c.value for c in SentimentChoices}
    return value if value in allowed else SentimentChoices.NEUTRAL


def _valid_topics(raw: list) -> list[dict]:
    result = []
    for item in raw:
        if not isinstance(item, dict) or not item.get("topic"):
            continue
        try:
            score = round(float(item["relevance_score"]), 2)
            score = max(0.01, min(1.0, score))
        except (KeyError, TypeError, ValueError):
            score = 0.50
        result.append({"topic": str(item["topic"])[:255], "relevance_score": score})
    return sorted(result, key=lambda x: x["relevance_score"], reverse=True)


def _valid_suggestions(raw: list) -> list[dict]:
    from apps.analysis.models.enums import CategoryChoices
    allowed = {c.value for c in CategoryChoices}
    result = []
    for item in raw:
        if not isinstance(item, dict) or not item.get("suggestion"):
            continue
        category = item.get("category", "content")
        result.append({
            "suggestion": str(item["suggestion"]),
            "category": category if category in allowed else CategoryChoices.CONTENT,
        })
    return result


def _valid_questions(raw: list) -> list[dict]:
    from apps.analysis.models.enums import CategoryChoices
    result = []
    for item in raw:
        if not isinstance(item, dict) or not item.get("question"):
            continue
        result.append({
            "question": str(item["question"])[:500],
            "answer": str(item.get("answer", "")),
            "category": CategoryChoices.CUSTOM,
        })
    return result


def _empty_result() -> dict:
    from apps.analysis.models.enums import SentimentChoices
    return {
        "summary": "No comments were available for analysis.",
        "sentiment": SentimentChoices.NEUTRAL,
        "audience_type": "",
        "topics": [],
        "suggestions": [],
        "questions": [],
    }
