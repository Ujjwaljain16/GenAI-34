"""
LLM-as-a-judge for eval metrics that can't be measured deterministically
(PEOS section 17). Kept in the eval harness, separate from production code.

Used as a *fallback* for concept purity: a question that doesn't mention the
concept name verbatim may still be entirely about it (good pedagogy often avoids
naming the term). The judge decides relevance. Temperature 0 for stability.
"""
from __future__ import annotations

import logging
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)


class RelevanceVerdict(BaseModel):
    relevant: bool = Field(description="True if the question genuinely tests the given concept.")
    reason: str = Field(default="")


_JUDGE_PROMPT = """You are an impartial evaluator.

Decide whether the QUESTION genuinely tests understanding of the CONCEPT
(it does not need to mention the concept's name verbatim).

CONCEPT: {name}
CONCEPT SUMMARY: {summary}

QUESTION: {question}

Return JSON: {{"relevant": true|false, "reason": "..."}}"""


def judge_concept_purity(concept_name: str, concept_summary: str, question: str) -> bool:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model = settings.GEMINI_MODEL or "gemini-2.5-flash-lite"
    prompt = _JUDGE_PROMPT.format(name=concept_name, summary=concept_summary, question=question)
    try:
        resp = client.models.generate_content(
            model=model, contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0, response_mime_type="application/json",
                response_schema=RelevanceVerdict),
        )
        return bool(resp.parsed and resp.parsed.relevant)
    except Exception as e:  # noqa: BLE001
        logger.warning("Judge failed, treating as not-relevant: %s", e)
        return False
