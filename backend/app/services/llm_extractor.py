import os
import time
import logging
import json
from typing import Dict, Any, List

from google import genai
from google.genai import types

from app.schemas.llm import ConceptExtractionResponse, RelationshipExtractionResponse, MergedConceptCandidate

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
        self.prompts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../prompts"))

    def _load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _call_with_retry(self, prompt: str, schema: Any) -> Any:
        """
        Executes the API call with a guaranteed delay to enforce rate limits,
        and exponential backoff for 429 Too Many Requests errors.
        """
        max_retries = 5
        base_delay = 5.0 # Guaranteed minimum delay per call to respect RPM
        
        config = types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=schema,
        )
        
        for attempt in range(max_retries):
            # Proactively sleep to avoid hitting the strict rate limit
            logger.info(f"Rate limiting: sleeping for {base_delay} seconds before calling Gemini...")
            time.sleep(base_delay)
            
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                if response.parsed is None:
                    # In case parsing fails but response is valid
                    logger.warning(f"Parsed response is None. Raw text: {response.text}")
                    raise ValueError("Failed to parse structured output from model.")
                return response.parsed
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                    wait_time = 30 * (attempt + 1)
                    logger.warning(f"Gemini quota exhausted (Attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s... Error: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(wait_time)
                else:
                    wait_time = 10 * (attempt + 1)
                    logger.warning(f"Gemini API error (Attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s... Error: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(wait_time)

    def extract_concepts(self, text_chunk: str) -> ConceptExtractionResponse:
        prompt_template = self._load_prompt("concept_extraction.md")
        prompt = prompt_template.replace("{{TEXT_CHUNK}}", text_chunk)
        return self._call_with_retry(prompt, ConceptExtractionResponse)

    def extract_relationship(self, text_chunk: str, concept_a: Dict[str, Any], concept_b: Dict[str, Any]) -> RelationshipExtractionResponse:
        prompt_template = self._load_prompt("relationship_extraction.md")
        prompt = prompt_template.replace("{{TEXT_CHUNK}}", text_chunk)
        prompt = prompt.replace("{{CONCEPT_A}}", concept_a.get("name", ""))
        prompt = prompt.replace("{{CONCEPT_B}}", concept_b.get("name", ""))
        return self._call_with_retry(prompt, RelationshipExtractionResponse)

    def resolve_merge(self, candidates: List[Dict[str, Any]]) -> MergedConceptCandidate:
        prompt_template = self._load_prompt("merge_resolution.md")
        prompt = prompt_template.replace("{{CANDIDATES_JSON}}", json.dumps(candidates, indent=2))
        return self._call_with_retry(prompt, MergedConceptCandidate)
