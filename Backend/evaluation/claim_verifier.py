from __future__ import annotations

import json
from pydantic import BaseModel, Field

from knowledge.models import RetrievalResult
from .json_llm import StructuredLLM
from .models import ClaimAssessment, ExtractedClaim


class ClaimVerificationOutput(BaseModel):
    assessment: ClaimAssessment


VERIFY_INSTRUCTIONS = """
أنت مدقق معرفي في نظام محاور.

المصدر الوحيد للحكم على صحة الادعاء هو الأدلة المعتمدة المرفقة في الطلب. ممنوع استخدام معرفتك السابقة لإثبات الادعاء أو نفيه.

أحكام verdict:
- supported: الأدلة المرفقة تؤيد المعنى بوضوح.
- partially_supported: جزء مهم صحيح لكن الصياغة أوسع/أدق من الأدلة أو تحتوي جزءًا غير مثبت.
- contradicted: الأدلة المرفقة تناقض الادعاء بوضوح.
- insufficient_evidence: لا توجد أدلة كافية للحكم.

قواعد:
- مجرد التشابه الموضوعي ليس دعمًا.
- إذا ادعى المتدرب آية/حديثًا/مرجعًا ولم يوجد ما يثبت النص أو النسبة في الأدلة، لا تعامل النسبة كصحيحة.
- fabricated_or_misquoted_evidence=true فقط عند وجود نسبة محددة لمصدر لا تؤيدها الأدلة أو عند تحريف جوهري للنص المستشهد به.
- severity=critical إذا كان الخطأ يتضمن اختلاق آية/حديث أو تحريفًا جوهريًا لدليل منسوب.
- severity=major لخطأ عقدي/شرعي أساسي يغيّر المعنى بشكل مهم.
- evidence_ids يجب أن تحتوي فقط document_id من الأدلة المرفقة التي استندت إليها.
- explanation_ar موجز ومحدد.
""".strip()


class ClaimVerifier:
    def __init__(self, llm: StructuredLLM):
        self.llm = llm

    def verify(self, claim: ExtractedClaim, retrieval: RetrievalResult) -> ClaimAssessment:
        if not retrieval.evidence_sufficient or not retrieval.evidence:
            return ClaimAssessment(
                claim_id=claim.claim_id,
                claim_text=claim.text,
                verdict="insufficient_evidence",
                severity="none",
                explanation_ar="لم تتوفر أدلة معتمدة كافية في قاعدة المعرفة للتحقق من هذا الادعاء.",
                evidence_ids=[],
                fabricated_or_misquoted_evidence=False,
            )

        evidence_payload = [
            {
                "document_id": e.document_id,
                "source": e.source_name,
                "source_type": e.source_type,
                "title": e.title,
                "text": e.text,
                "citation_label": e.citation_label,
                "url": e.source_url,
            }
            for e in retrieval.evidence
        ]
        payload = {
            "claim": claim.model_dump(),
            "retrieval_evidence": evidence_payload,
        }
        result = self.llm.parse(
            instructions=VERIFY_INSTRUCTIONS,
            input_text=json.dumps(payload, ensure_ascii=False),
            schema=ClaimVerificationOutput,
        )
        assessment = result.assessment
        # Bind identity defensively even if the LLM drifted.
        assessment.claim_id = claim.claim_id
        assessment.claim_text = claim.text
        allowed = {e.document_id for e in retrieval.evidence}
        assessment.evidence_ids = [eid for eid in assessment.evidence_ids if eid in allowed]
        return assessment
