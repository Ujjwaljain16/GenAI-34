from pydantic import BaseModel, Field
from typing import List, Optional

class ConceptCandidate(BaseModel):
    name: str = Field(description="The canonical name of the concept.")
    summary: str = Field(description="A concise definition or explanation of the concept based ONLY on the provided text.")
    difficulty: int = Field(description="Difficulty rating from 1 to 5.")

class ConceptExtractionResponse(BaseModel):
    concepts: List[ConceptCandidate]

class RelationshipExtractionResponse(BaseModel):
    relationship_type: str = Field(description="Must be one of: PREREQUISITE, RELATED, NO_RELATIONSHIP")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: Optional[str] = Field(description="Brief quote or reasoning supporting the relationship.")

class MergedConceptCandidate(BaseModel):
    canonical_name: str
    canonical_summary: str
    difficulty: int = Field(description="Difficulty rating from 1 to 5.")
