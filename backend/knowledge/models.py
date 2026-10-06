from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


SourceType = Literal[
    "quran", "hadith", "tafsir", "aqeedah", "fiqh", "sirah",
    "dawah", "terminology", "qa", "history", "general"
]


class SourceRecord(BaseModel):
    key: str
    name_ar: str
    name_en: str
    base_url: str
    domains: list[str]
    content_types: list[SourceType]
    priority: int = Field(ge=1, le=5)
    approved: bool = True
    notes: Optional[str] = None


class KnowledgeDocument(BaseModel):
    id: str
    source_key: str
    source_name: str
    source_url: str
    source_type: SourceType
    title: str
    text: str
    language: str = "ar"
    authority_level: int = Field(default=3, ge=1, le=5)
    topic_tags: list[str] = Field(default_factory=list)
    citation_label: Optional[str] = None
    external_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class RetrievedEvidence(BaseModel):
    document_id: str
    source_key: str
    source_name: str
    source_url: str
    source_type: SourceType
    title: str
    text: str
    citation_label: Optional[str] = None
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    combined_score: float = 0.0
    authority_level: int = 3
    metadata: dict = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    query: str
    domain: Optional[SourceType] = None
    evidence: list[RetrievedEvidence] = Field(default_factory=list)
    evidence_sufficient: bool = False
    reason: Optional[str] = None
