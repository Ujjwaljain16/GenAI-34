from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class BookProgressDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    bookId: str = Field(alias="bookId")
    title: str
    author: Optional[str] = None
    status: str
    totalConcepts: int = Field(alias="totalConcepts")
    masteredConcepts: int = Field(alias="masteredConcepts")
    percentMastered: float = Field(alias="percentMastered")
    percentRevealed: float = Field(alias="percentRevealed")
    dueToday: int = Field(alias="dueToday")


class WeakSpotDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    title: str
    bookTitle: str = Field(alias="bookTitle")
    mastery: float


class DashboardDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    conceptsMastered: int = Field(alias="conceptsMastered")
    conceptsTracked: int = Field(alias="conceptsTracked")
    avgMastery: float = Field(alias="avgMastery")
    totalDue: int = Field(alias="totalDue")
    globalStreak: int = Field(alias="globalStreak")
    studiedToday: bool = Field(alias="studiedToday")
    books: List[BookProgressDTO]
    weakSpots: List[WeakSpotDTO] = Field(alias="weakSpots")


class NotificationDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    type: str
    message: str
    read: bool = False
    link: Optional[str] = None
