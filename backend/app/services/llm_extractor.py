import os
import time
import logging
import json
from typing import Dict, Any, List

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.llm_pool import gemini_pool
from app.schemas.llm import (
    ConceptExtractionResponse,
    RelationshipExtractionResponse,
    MergedConceptCandidate,
    MergeJudgeOutput,
)

logger = logging.getLogger(__name__)


class LLMExtractor:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-2.5-flash-lite"
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../prompts")
        )

    def _load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _call_with_retry(self, prompt: str, schema: Any, max_retries: int = 5) -> Any:
        config = types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=schema,
        )

        for attempt in range(max_retries):
            try:
                client = gemini_pool.get_client()
                response = client.models.generate_content(
                    model=self.model_name, contents=prompt, config=config
                )
                try:
                    import json
                    raw_text = response.text.strip()
                    if raw_text.startswith("```"):
                        raw_text = raw_text.strip("`").strip()
                        if raw_text.lower().startswith("json"):
                            raw_text = raw_text[4:].strip()
                    parsed_json = json.loads(raw_text)
                    return schema.model_validate(parsed_json)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse JSON into model. Raw text: {response.text}\nError: {e}"
                    )
                    raise ValueError("Failed to parse structured output from model.")
            except Exception as e:
                err_str = str(e)
                is_quota = "429" in err_str or "quota" in err_str.lower()
                
                if attempt == max_retries - 1:
                    logger.error("Gemini call failed after %d attempts: %s", max_retries, e)
                    raise
                
                if is_quota and len(gemini_pool.clients) > 1:
                    gemini_pool.rotate()
                    continue
                
                wait_time = (30 if is_quota else 10) * (attempt + 1)
                logger.warning(
                    f"Gemini error (Attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s... Error: {e}"
                )
                time.sleep(wait_time)

    def extract_concepts(self, text_chunk: str) -> ConceptExtractionResponse:
        prompt_template = self._load_prompt("concept_extraction.md")
        prompt = prompt_template.replace("{{TEXT_CHUNK}}", text_chunk)
        return self._call_with_retry(prompt, ConceptExtractionResponse)

    @staticmethod
    def _concept_field(concept: Dict[str, Any], field: str) -> str:
        # Canonical concepts use canonical_name/canonical_summary; raw candidates
        # use name/summary. Accept either so edge inference always gets context.
        return str(concept.get(field) or concept.get(f"canonical_{field}") or "")

    def extract_relationship(
        self, text_chunk: str, concept_a: Dict[str, Any], concept_b: Dict[str, Any]
    ) -> RelationshipExtractionResponse:
        prompt_template = self._load_prompt("relationship_extraction.md")
        prompt = (
            prompt_template.replace("{{TEXT_CHUNK}}", text_chunk)
            .replace("{{CONCEPT_A_NAME}}", self._concept_field(concept_a, "name"))
            .replace("{{CONCEPT_A_SUMMARY}}", self._concept_field(concept_a, "summary"))
            .replace("{{CONCEPT_B_NAME}}", self._concept_field(concept_b, "name"))
            .replace("{{CONCEPT_B_SUMMARY}}", self._concept_field(concept_b, "summary"))
        )
        return self._call_with_retry(prompt, RelationshipExtractionResponse)

    def resolve_merge(self, candidates: List[Dict[str, Any]]) -> MergedConceptCandidate:
        prompt_template = self._load_prompt("merge_resolution.md")
        prompt = prompt_template.replace(
            "{{CANDIDATES_JSON}}", json.dumps(candidates, indent=2)
        )
        return self._call_with_retry(prompt, MergedConceptCandidate)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Fetch embeddings using local all-MiniLM-L6-v2 model."""
        if not hasattr(self, "_embedding_model"):
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            
        embeddings = self._embedding_model.encode(texts)
        return embeddings.tolist()

    def judge_merge(
        self, concept_a: Dict[str, Any], concept_b: Dict[str, Any]
    ) -> bool:
        """Use Gemini to judge if two candidates are functionally identical."""
        prompt_template = self._load_prompt("merge_judge.md")
        prompt = (
            prompt_template.replace("{{CONCEPT_A_NAME}}", self._concept_field(concept_a, "name"))
            .replace("{{CONCEPT_A_SUMMARY}}", self._concept_field(concept_a, "summary"))
            .replace("{{CONCEPT_B_NAME}}", self._concept_field(concept_b, "name"))
            .replace("{{CONCEPT_B_SUMMARY}}", self._concept_field(concept_b, "summary"))
        )
        result: MergeJudgeOutput = self._call_with_retry(prompt, MergeJudgeOutput)
        return result.decision.upper() == "MERGE"
