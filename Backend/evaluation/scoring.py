from __future__ import annotations

from .models import ClaimAssessment


VERDICT_WEIGHT = {
    "supported": 1.0,
    "partially_supported": 0.5,
    "contradicted": 0.0,
    "insufficient_evidence": 0.0,
    "not_religious_claim": 1.0,
}


def compute_accuracy_score(assessments: list[ClaimAssessment]) -> int:
    """Deterministic 0..30 score from verified claims.

    The LLM classifies each claim against retrieved evidence; arithmetic stays
    deterministic so the model cannot arbitrarily choose an overall score.
    """
    relevant = [a for a in assessments if a.verdict != "not_religious_claim"]
    if not relevant:
        # No factual Islamic claims made. Do not manufacture correctness; use a
        # neutral midpoint so conversation-only turns are not rewarded as perfect.
        return 15

    total = 0.0
    for assessment in relevant:
        weight = VERDICT_WEIGHT[assessment.verdict]
        if assessment.fabricated_or_misquoted_evidence:
            weight = 0.0
        total += weight
    raw = 30.0 * total / len(relevant)
    return max(0, min(30, round(raw)))


def critical_errors(assessments: list[ClaimAssessment]) -> list[str]:
    errors: list[str] = []
    for a in assessments:
        if a.severity == "critical" or a.fabricated_or_misquoted_evidence:
            errors.append(f"{a.claim_text}: {a.explanation_ar}")
    return errors
