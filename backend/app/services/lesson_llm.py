"""
Gemini wrapper for the learning layer: lesson generation, Socratic tutoring,
and progressive hints (pls2 #7, pls3 #10/#11). Async-friendly (runs the
synchronous google-genai client in a thread).
"""

from __future__ import annotations

import os
import json
import time
import asyncio
import logging
from typing import Any, List

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.llm_pool import gemini_pool
from app.schemas.llm import LessonOutput, TutorOutput, HintOutput, SubtopicsOutput

logger = logging.getLogger(__name__)
PROMPT_VERSION = "v1"


class LessonLLM:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-2.5-flash-lite"
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../prompts")
        )

    def _load(self, filename: str) -> str:
        with open(os.path.join(self.prompts_dir, filename), "r", encoding="utf-8") as f:
            return f.read()

    def _call_sync(self, prompt: str, schema: Any, temperature: float) -> Any:
        # The new google.genai SDK crashes on nested Pydantic models with $defs
        # So we remove response_schema from config and append it to the prompt.
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        )
        
        import json
        prompt_with_schema = (
            f"{prompt}\n\n"
            f"You MUST output valid JSON that strictly conforms to this JSON Schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}"
        )

        for attempt in range(5):
            try:
                client = gemini_pool.get_client()
                resp = client.models.generate_content(
                    model=self.model_name, contents=prompt_with_schema, config=config
                )
                
                try:
                    raw_text = resp.text.strip()
                    if raw_text.startswith("```"):
                        raw_text = raw_text.strip("`").strip()
                        if raw_text.lower().startswith("json"):
                            raw_text = raw_text[4:].strip()
                    parsed_json = json.loads(raw_text)
                    return schema.model_validate(parsed_json)
                except Exception as parse_e:
                    logger.warning(f"Failed to parse JSON. Error: {parse_e}\nRaw text: {resp.text}")
                    raise ValueError(f"Failed to parse structured output: {parse_e}")

            except Exception as e:  # noqa: BLE001
                is_quota = "429" in str(e) or "quota" in str(e).lower()
                
                # If we've exhausted all attempts
                if attempt == 4:
                    if is_quota:
                        logger.error("LessonLLM fully rate limited on all keys: %s", e)
                        raise RuntimeError("LLM_RATE_LIMIT") from e
                    logger.error("LessonLLM call failed: %s", e)
                    raise

                # If rate limit and we have multiple keys, rotate and instantly retry
                if is_quota and len(gemini_pool.clients) > 1:
                    gemini_pool.rotate()
                    continue

                # If rate limit but we only have 1 key, fail fast to avoid DB timeouts
                if is_quota:
                    logger.error("LessonLLM rate limited, failing fast: %s", e)
                    raise RuntimeError("LLM_RATE_LIMIT") from e
                    
                time.sleep(2)

    async def _call(self, prompt: str, schema: Any, temperature: float) -> Any:
        return await asyncio.to_thread(self._call_sync, prompt, schema, temperature)

    async def generate_lesson(
        self,
        concept_name: str,
        concept_summary: str,
        source_text: str,
        mastery: float,
        misconceptions: List[str],
        target_bloom: str,
    ) -> LessonOutput:
        prompt = (
            self._load("lesson_generator.md")
            .replace("{{CONCEPT_NAME}}", concept_name)
            .replace("{{CONCEPT_SUMMARY}}", concept_summary or "")
            .replace("{{SOURCE_TEXT}}", source_text or "(no source text available)")
            .replace("{{MASTERY}}", f"{mastery:.2f}")
            .replace("{{MISCONCEPTIONS}}", json.dumps(misconceptions or []))
            .replace("{{TARGET_BLOOM}}", target_bloom)
        )
        return await self._call(prompt, LessonOutput, temperature=0.5)

    async def tutor_turn(
        self,
        concept_name: str,
        concept_summary: str,
        source_text: str,
        mastery: float,
        conversation_history: str,
        hint_level: int,
        student_message: str,
    ) -> TutorOutput:
        prompt = (
            self._load("socratic_tutor.md")
            .replace("{{CONCEPT_NAME}}", concept_name)
            .replace("{{CONCEPT_SUMMARY}}", concept_summary or "")
            .replace("{{SOURCE_TEXT}}", source_text or "(no source text available)")
            .replace("{{MASTERY}}", f"{mastery:.2f}")
            .replace(
                "{{CONVERSATION_HISTORY}}",
                conversation_history or "(start of conversation)",
            )
            .replace("{{HINT_LEVEL}}", str(hint_level))
            .replace("{{STUDENT_MESSAGE}}", student_message)
        )
        return await self._call(prompt, TutorOutput, temperature=0.6)

    async def generate_subtopics(
        self, concept_name: str, concept_summary: str
    ) -> SubtopicsOutput:
        prompt = (
            "List 3 to 5 concise sub-topics (each 2-5 words) that make up the concept below. "
            "These are the specific things a learner studies within it. Return JSON only.\n\n"
            f"Concept: {concept_name}\nSummary: {concept_summary or ''}\n"
        )
        return await self._call(prompt, SubtopicsOutput, temperature=0.2)

    async def generate_hint(
        self,
        concept_name: str,
        question: str,
        hint_level: int,
        previous_hints: List[str],
    ) -> HintOutput:
        prompt = (
            self._load("hint_generator.md")
            .replace("{{CONCEPT_NAME}}", concept_name)
            .replace("{{QUESTION}}", question)
            .replace("{{HINT_LEVEL}}", str(hint_level))
            .replace("{{PREVIOUS_HINTS}}", json.dumps(previous_hints or []))
        )
        return await self._call(prompt, HintOutput, temperature=0.4)
