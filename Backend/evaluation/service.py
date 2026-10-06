from __future__ import annotations

import re

from knowledge.retriever import HybridRetriever
from .claim_extractor import ClaimExtractor
from .claim_verifier import ClaimVerifier
from .coach import Coach
from .models import (
    DialogueTurn,
    EvaluationResult,
    InternalScores,
    KnowledgeEvaluation,
)
from .rubric_evaluator import RubricEvaluator
from .scoring import compute_accuracy_score, critical_errors


class EvaluationService:
    # These are display-time safeguards. Ingestion should already be clean, but
    # the coaching UI should never show raw reviewer/navigation junk even if an
    # older dirty chunk still exists in knowledge.db.
    DISPLAY_NOISE = [
        "المشرف العام",
        "نائب المشرف العام",
        "الأستاذ بجامعة",
        "أستاذ بجامعة",
        "قاضي بمحكمة",
        "باحث في التاريخ",
        "مشرف تربوي",
        "تم تحكيم",
        "جامعة أم القرى",
        "جامعة الملك خالد",
        "تسجيل الدخول",
        "إنشاء حساب",
        "جميع الحقوق محفوظة",
        "سياسة الخصوصية",
        "شارك المادة",
        "نسخ الرابط",
        "روابط مهمة",
        "مواضيع ذات صلة",
        "مواد ذات صلة",
    ]

    def __init__(
        self,
        retriever: HybridRetriever,
        claim_extractor: ClaimExtractor,
        claim_verifier: ClaimVerifier,
        rubric_evaluator: RubricEvaluator,
        coach: Coach,
    ):
        self.retriever = retriever
        self.claim_extractor = claim_extractor
        self.claim_verifier = claim_verifier
        self.rubric_evaluator = rubric_evaluator
        self.coach = coach

    @classmethod
    def _evidence_quality_ok(cls, evidence) -> bool:
        text = (evidence.text or "").strip()
        if len(text.split()) < 8:
            return False

        hits = sum(phrase in text for phrase in cls.DISPLAY_NOISE)
        if hits >= 1:
            return False

        # Staff/reviewer lists often contain several honorific + name patterns.
        title_hits = len(
            re.findall(
                r"(?:الشيخ|الدكتور|الأستاذ)\s+[\w\u0600-\u06FF]+",
                text,
            )
        )
        if title_hits >= 3:
            return False

        return True

    @classmethod
    def _clean_display_text(cls, text: str, max_chars: int = 500) -> str:
        """Return a short clean excerpt for the coaching UI.

        We intentionally do not expose a full raw RAG chunk to the learner.
        This keeps the feedback readable and prevents residual site chrome or
        reviewer metadata from appearing in the interface.
        """
        if not text:
            return ""

        # Remove known noisy lines/fragments.
        parts = re.split(r"\n+", text)
        clean_parts = []
        seen = set()
        for part in parts:
            part = re.sub(r"\s+", " ", part).strip()
            if not part:
                continue
            if any(phrase in part for phrase in cls.DISPLAY_NOISE):
                continue
            key = part.casefold()
            if key in seen:
                continue
            seen.add(key)
            clean_parts.append(part)

        cleaned = " ".join(clean_parts).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)

        if len(cleaned) <= max_chars:
            return cleaned

        # Prefer a sentence boundary so the UI excerpt does not end abruptly.
        candidate = cleaned[:max_chars]
        boundaries = [candidate.rfind(x) for x in [". ", "؟ ", "! ", "؛ ", "، "]]
        cut = max(boundaries)
        if cut >= int(max_chars * 0.55):
            candidate = candidate[: cut + 1]
        else:
            candidate = candidate.rsplit(" ", 1)[0]

        return candidate.rstrip("،؛: ") + "…"

    @classmethod
    def _prepare_for_display(cls, evidence):
        """Clone RetrievedEvidence with a short, cleaned `text` field."""
        excerpt = cls._clean_display_text(evidence.text)
        if not excerpt:
            return None

        # Pydantic v2: model_copy keeps the same model/schema so no frontend or
        # API contract changes are required.
        return evidence.model_copy(update={"text": excerpt})

    @classmethod
    def _select_helpful_sources(cls, assessments, evidence_by_id, limit: int = 3):
        """Return 2–3 useful, clean and traceable coaching sources.

        Priority:
        1) evidence explicitly used by claim verification;
        2) strongest remaining retrieved evidence;
        3) source diversity when possible.

        Raw dirty chunks are filtered out and displayed as concise excerpts.
        """
        ordered_ids: list[str] = []

        # Evidence actually used by the verifier should always be considered
        # before generic top retrieval results.
        for assessment in assessments:
            for evidence_id in assessment.evidence_ids:
                if evidence_id not in ordered_ids:
                    ordered_ids.append(evidence_id)

        remaining = sorted(
            (
                e
                for e in evidence_by_id.values()
                if cls._evidence_quality_ok(e)
            ),
            key=lambda e: e.combined_score,
            reverse=True,
        )

        for e in remaining:
            if e.document_id not in ordered_ids:
                ordered_ids.append(e.document_id)

        chosen = []
        seen_urls = set()
        seen_sources = set()

        # First pass: favor source diversity.
        for evidence_id in ordered_ids:
            e = evidence_by_id.get(evidence_id)
            if not e:
                continue
            if not cls._evidence_quality_ok(e):
                continue
            if e.source_url in seen_urls or e.source_key in seen_sources:
                continue

            display_evidence = cls._prepare_for_display(e)
            if display_evidence is None:
                continue

            chosen.append(display_evidence)
            seen_urls.add(e.source_url)
            seen_sources.add(e.source_key)
            if len(chosen) >= limit:
                return chosen

        # Second pass: allow another page from the same source family if needed.
        for evidence_id in ordered_ids:
            e = evidence_by_id.get(evidence_id)
            if not e:
                continue
            if not cls._evidence_quality_ok(e):
                continue
            if e.source_url in seen_urls:
                continue

            display_evidence = cls._prepare_for_display(e)
            if display_evidence is None:
                continue

            chosen.append(display_evidence)
            seen_urls.add(e.source_url)
            if len(chosen) >= limit:
                break

        return chosen

    def evaluate(self,
    turns: list[DialogueTurn],
    topic_id: str | None = None,
    ) -> EvaluationResult:
        claims = self.claim_extractor.extract(turns)

        assessments = []
        retrieval_by_claim = {}
        suggested = {}

        for claim in claims:
            retrieval = self.retriever.retrieve(
                claim.normalized_query or claim.text,
                top_k=8,
            )
            retrieval_by_claim[claim.claim_id] = retrieval
            assessment = self.claim_verifier.verify(claim, retrieval)
            assessments.append(assessment)

            # Keep all retrieved evidence internally. Display-time quality
            # filtering happens in _select_helpful_sources so verification is
            # not silently altered by UI concerns.
            for e in retrieval.evidence:
                suggested[e.document_id] = e

        accuracy = compute_accuracy_score(assessments)
        evidence_eval = self.rubric_evaluator.evaluate_evidence_use(turns, assessments)
        knowledge_total = accuracy + evidence_eval.score

        knowledge = KnowledgeEvaluation(
            accuracy_score=accuracy,
            evidence_score=evidence_eval.score,
            total=knowledge_total,
            claim_assessments=assessments,
            strengths_ar=evidence_eval.strengths_ar,
            weaknesses_ar=evidence_eval.weaknesses_ar,
            suggested_evidence=self._select_helpful_sources(
                assessments,
                suggested,
                limit=3,
            ),
        )

        conversation = self.rubric_evaluator.evaluate_conversation(turns)
        errors = critical_errors(assessments)
        internal = InternalScores(
            knowledge=knowledge.total,
            conversation=conversation.total,
            total=knowledge.total + conversation.total,
        )
        coaching = self.coach.generate(knowledge, conversation, errors)

        return EvaluationResult(
            knowledge=knowledge,
            conversation=conversation,
            internal_scores=internal,
            coaching=coaching,
            critical_errors=errors,
        )
