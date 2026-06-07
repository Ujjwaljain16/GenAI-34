from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class DueItemDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    conceptId: str = Field(alias="conceptId")
    title: str
    nextDue: Optional[str] = Field(alias="nextDue", default=None)
    retrievability: float = 0.0


class DueListDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    bookId: str = Field(alias="bookId")
    count: int
    due: List[DueItemDTO]


class ReviewRequest(BaseModel):
    grade: int = Field(ge=1, le=4)   # 1=Again 2=Hard 3=Good 4=Easy


class ReviewResultDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    conceptId: str = Field(alias="conceptId")
    grade: int
    mastery: float
    intervalDays: int = Field(alias="intervalDays")
    stability: float
    difficulty: float
