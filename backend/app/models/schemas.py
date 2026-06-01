"""Pydantic request/response schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """POST /api/v1/auth/register"""

    name: str = Field(..., min_length=1, max_length=100)
    languagePreference: str = Field(default="en", pattern="^(en|ur)$")


class UserOut(BaseModel):
    id: int
    name: str
    languagePreference: str
    totalSessions: int
    createdAt: datetime

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    userId: int
    sessionNo: int
    status: str
    stressLevel: int
    createdAt: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """POST /api/v1/chat/message"""

    userId: int
    sessionId: int
    message: str = Field(..., min_length=1)


class RecommendationOut(BaseModel):
    type: str
    title: str
    content: str
    assignedAt: Optional[datetime] = None


class ChatResponse(BaseModel):
    aiResponse: str
    mhClassification: str
    mhConfidence: float
    emotionLabel: str
    riskLevel: str
    isCrisis: bool
    helplineNumbers: List[dict]
    recommendations: List[RecommendationOut]
    chatLogId: int


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    mhClassification: Optional[str] = None
    timestamp: datetime


class MoodSummaryItem(BaseModel):
    sessionNo: int
    dominantEmotion: str
    date: str


class MoodSummaryResponse(BaseModel):
    summary: List[MoodSummaryItem]
    trend: str
