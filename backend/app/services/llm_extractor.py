import os
import time
import logging
import json
from typing import Dict, Any, List

from google import genai
from google.genai import types

from app.schemas.llm import (
    ConceptExtractionResponse,
    RelationshipExtractionResponse,
    MergedConceptCandidate,
    MergeJudgeOutput,
)

logger = logging.getLogger(__name__)


class LLMExtractor:
    """
    Interfaces with Gemini for concept and relationship extraction using structured outputs.
    Includes explicit rate limiting and retries for strict free-tier limits.
    """

    def __init__(self, model_name: str = None):
        from app.core.config import settings

        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-2.5-flash-lite"
        self.prompts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../prompts")
        )

    def _load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _resolve_refs(self, schema_dict: Any, defs: Any = None) -> Any:
        if defs is None and isinstance(schema_dict, dict):
            defs = schema_dict.pop("$defs", {})
        if isinstance(schema_dict, dict):
            schema_dict.pop("title", None)  # Gemini API does not support 'title'
            if "$ref" in schema_dict:
                ref_name = schema_dict["$ref"].split("/")[-1]
                resolved = defs[ref_name].copy()
                return self._resolve_refs(resolved, defs)
            return {k: self._resolve_refs(v, defs) for k, v in schema_dict.items()}
        elif isinstance(schema_dict, list):
            return [self._resolve_refs(item, defs) for item in schema_dict]
        return schema_dict

    def _call_with_retry(self, prompt: str, schema: Any) -> Any:
        """
        Executes the API call with a guaranteed delay to enforce rate limits,
        and exponential backoff for 429 Too Many Requests errors.
        """
        max_retries = 5
        base_delay = 5.0  # Guaranteed minimum delay per call to respect RPM

        # Bypass google-genai extra_forbidden on nested Pydantic schemas by inlining references
        schema_dict = self._resolve_refs(schema.model_json_schema())

        config = types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=schema_dict,
        )

        for attempt in range(max_retries):
            # Proactively sleep to avoid hitting the strict rate limit
            logger.info(
                f"Rate limiting: sleeping for {base_delay} seconds before calling Gemini..."
            )
            time.sleep(base_delay)

            try:
                response = self.client.models.generate_content(
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
                if "429" in err_str or "quota" in err_str.lower():
                    wait_time = 30 * (attempt + 1)
                    logger.warning(
                        f"Gemini quota exhausted (Attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s... Error: {e}"
                    )
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(wait_time)
                else:
                    wait_time = 10 * (attempt + 1)
                    logger.warning(
                        f"Gemini API error (Attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s... Error: {e}"
                    )
                    if attempt == max_retries - 1:
                        raise
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
        """Fetch embeddings using Gemini's text-embedding-004 model."""
        # Split into batches to avoid exceeding limits
        batch_size = 50
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.models.embed_content(
                model="text-embedding-004", contents=batch
            )
            for emb in response.embeddings:
                all_embeddings.append(emb.values)
        return all_embeddings

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
