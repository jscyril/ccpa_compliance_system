"""
API Schemas

Pydantic models for request/response validation on the CCPA
compliance analysis endpoints.
"""

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""

    prompt: str


class AnalyzeResponse(BaseModel):
    """Response body for POST /analyze."""

    harmful: bool
    articles: list[str]
    explanation: str
    referenced_articles: list[str]
