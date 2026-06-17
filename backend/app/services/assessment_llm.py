"""
Gemini wrapper for the assessment engine.

Implements three prompts from docs/prompts/pls1.md against the runtime prompt
files in app/prompts/:
  - assessment_question_generator  -> AssessmentQuestionOutput
  - assessment_evaluator           -> AssessmentEvalOutput  (free-text only)
  - learning_dna_generator         -> LearningDNAOutput

The underlying google-genai client is synchronous, so each call is run in a
thread (asyncio.to_thread) to avoid blocking the FastAPI event loop. The LLM
only generates/grades language; placement decisions stay in assessment_walk.
"""

from __future__ import annotations

import os
import json
import time
import asyncio
import logging
from typing import Any

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.llm_pool import gemini_pool
from app.schemas.llm import (
    AssessmentQuestionOutput,
    AssessmentEvalOutput,
    LearningDNAOutput,
)

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v1"


class AssessmentLLM:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-2.5-flash-lite"
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../prompts")
        )

    def _load_prompt(self, filename: str) -> str:
        with open(os.path.join(self.prompts_dir, filename), "r", encoding="utf-8") as f:
            return f.read()

    def _call_sync(self, prompt: str, schema: Any, temperature: float, max_retries: int = 5) -> Any:
        """Blocking Gemini call with rotation and backoff."""
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=schema,
        )
        for attempt in range(max_retries):
            try:
                client = gemini_pool.get_client()
                response = client.models.generate_content(
                    model=self.model_name, contents=prompt, config=config
                )
                if response.parsed is None:
                    raise ValueError(f"Empty structured output. Raw: {response.text}")
                return response.parsed
            except Exception as e:
                is_quota = "429" in str(e) or "quota" in str(e).lower()
                if attempt == max_retries - 1:
                    logger.error("Gemini call failed after %d attempts: %s", max_retries, e)
                    raise
                
                if is_quota and len(gemini_pool.clients) > 1:
                    gemini_pool.rotate()
                    continue
                
                wait = (20 if is_quota else 4) * (attempt + 1)
                logger.warning(
                    "Gemini error (attempt %d/%d), retrying in %ds: %s",
                    attempt + 1,
                    max_retries,
                    wait,
                    err,
                )
                time.sleep(wait)

    async def _call(self, prompt: str, schema: Any, temperature: float) -> Any:
        return await asyncio.to_thread(self._call_sync, prompt, schema, temperature)

    async def generate_question(
        self,
        concept_name: str,
        concept_summary: str,
        difficulty: str,
        bloom_level: str,
        question_type: str,
    ) -> AssessmentQuestionOutput:
        prompt = (
            self._load_prompt("assessment_question_generator.md")
            .replace("{{CONCEPT_NAME}}", concept_name)
            .replace("{{CONCEPT_SUMMARY}}", concept_summary or "")
            .replace("{{DIFFICULTY}}", difficulty)
            .replace("{{BLOOM_LEVEL}}", bloom_level)
            .replace("{{QUESTION_TYPE}}", question_type)
        )
        return await self._call(prompt, AssessmentQuestionOutput, temperature=0.3)

    async def evaluate_answer(
        self,
        concept_name: str,
        question: str,
        expected_answer: str,
        student_answer: str,
    ) -> AssessmentEvalOutput:
        prompt = (
            self._load_prompt("assessment_evaluator.md")
            .replace("{{CONCEPT_NAME}}", concept_name)
            .replace("{{QUESTION}}", question)
            .replace("{{EXPECTED_ANSWER}}", expected_answer or "")
            .replace("{{STUDENT_ANSWER}}", student_answer or "")
        )
        return await self._call(prompt, AssessmentEvalOutput, temperature=0.1)

    async def generate_dna(
        self, book_title: str, assessment_results: list[dict], confidence_summary: str
    ) -> LearningDNAOutput:
        prompt = (
            self._load_prompt("learning_dna_generator.md")
            .replace("{{BOOK_TITLE}}", book_title)
            .replace("{{ASSESSMENT_RESULTS}}", json.dumps(assessment_results, indent=2))
            .replace("{{CONFIDENCE_SUMMARY}}", confidence_summary)
        )
        return await self._call(prompt, LearningDNAOutput, temperature=0.3)
