from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field

from knowledge.models import RetrievedEvidence, SourceType


ClaimVerdict = Literal[
    "supported", "partially_supported", "contradicted", "insufficient_evidence", "not_religious_claim"
]
Severity = Literal["none", "minor", "major", "critical"]


class DialogueTurn(BaseModel):
    speaker: Literal["adam", "trainee"]
    text: str
    turn_index: int
    audio_metrics: Optional["VoiceMetrics"] = None


class ExtractedClaim(BaseModel):
    claim_id: str
    turn_index: int
    text: str
    normalized_query: str
    domain: SourceType | None = None
    requires_evidence: bool = True
    cited_reference: Optional[str] = None


class ClaimAssessment(BaseModel):
    claim_id: str
    claim_text: str
    verdict: ClaimVerdict
    severity: Severity = "none"
    explanation_ar: str
    evidence_ids: list[str] = Field(default_factory=list)
    fabricated_or_misquoted_evidence: bool = False


class KnowledgeEvaluation(BaseModel):
    accuracy_score: int = Field(ge=0, le=30)
    evidence_score: int = Field(ge=0, le=20)
    total: int = Field(ge=0, le=50)
    claim_assessments: list[ClaimAssessment]
    strengths_ar: list[str] = Field(default_factory=list)
    weaknesses_ar: list[str] = Field(default_factory=list)
    suggested_evidence: list[RetrievedEvidence] = Field(default_factory=list)


class VoiceMetrics(BaseModel):
    duration_seconds: Optional[float] = None
    word_count: Optional[int] = None
    words_per_minute: Optional[float] = None
    filler_count: Optional[int] = None
    filler_words: dict[str, int] = Field(default_factory=dict)
    pause_count: Optional[int] = None
    long_pause_count: Optional[int] = None
    # Keep this explicitly observable. Do not infer tone/emotion from it.
    transcript_available: bool = True


class ConversationEvaluation(BaseModel):
    clarity: int = Field(ge=0, le=10)
    listening_response: int = Field(ge=0, le=10)
    wisdom_attitude: int = Field(ge=0, le=10)
    answer_structure: int = Field(ge=0, le=10)
    voice_delivery: int = Field(ge=0, le=10)
    total: int = Field(ge=0, le=50)
    strengths_ar: list[str] = Field(default_factory=list)
    weaknesses_ar: list[str] = Field(default_factory=list)


class InternalScores(BaseModel):
    knowledge: int = Field(ge=0, le=50)
    conversation: int = Field(ge=0, le=50)
    total: int = Field(ge=0, le=100)


class CoachingFeedback(BaseModel):
    diagnosis_ar: str
    strengths_ar: list[str]
    improvements_ar: list[str]
    evidence_you_could_use: list[str] = Field(default_factory=list)
    next_attempt_ar: str


class EvaluationResult(BaseModel):
    knowledge: KnowledgeEvaluation
    conversation: ConversationEvaluation
    internal_scores: InternalScores
    coaching: CoachingFeedback
    critical_errors: list[str] = Field(default_factory=list)


DialogueTurn.model_rebuild()
