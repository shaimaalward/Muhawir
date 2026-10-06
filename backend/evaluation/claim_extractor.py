from __future__ import annotations

from pydantic import BaseModel, Field

from .json_llm import StructuredLLM
from .models import DialogueTurn, ExtractedClaim


class ClaimExtractionOutput(BaseModel):
    claims: list[ExtractedClaim] = Field(default_factory=list)


CLAIM_EXTRACTION_INSTRUCTIONS = """
أنت محلل ادعاءات لمشروع محاور. مهمتك استخراج الادعاءات الإسلامية القابلة للتحقق من كلام المتدرب فقط.

قواعد صارمة:
- لا تستخرج كلام آدم على أنه ادعاء للمتدرب.
- استخرج كل ادعاء ديني/تاريخي/شرعي مستقل يحتاج إلى تحقق منفصل.
- لا تعتبر المجاملات والآراء الشخصية والعبارات الحوارية العامة ادعاءات معرفية.
- إذا ذكر المتدرب آية أو حديثًا أو نسب قولًا إلى مصدر، ضع المرجع المنسوب في cited_reference.
- normalized_query يجب أن يكون استعلامًا عربيًا قصيرًا صالحًا للاسترجاع، لا حكمًا على صحة الادعاء.
- domain تصنيف وصفي فقط للتقارير، وليس قيدًا على الاسترجاع. استخدم واحدًا من: quran, hadith, tafsir, aqeedah, fiqh, sirah, dawah, terminology, qa, history, general أو null.
- requires_evidence=false فقط عندما لا يحتاج الكلام إلى دليل معرفي أصلًا.
- claim_id يجب أن يكون فريدًا مثل c1, c2...
- لا تتحقق من صحة الادعاء هنا ولا تعتمد على معرفتك.
""".strip()


class ClaimExtractor:
    def __init__(self, llm: StructuredLLM):
        self.llm = llm

    def extract(self, turns: list[DialogueTurn]) -> list[ExtractedClaim]:
        lines = []
        for turn in turns:
            if turn.speaker == "trainee":
                lines.append(f"[turn={turn.turn_index}] المتدرب: {turn.text}")
        if not lines:
            return []
        result = self.llm.parse(
            instructions=CLAIM_EXTRACTION_INSTRUCTIONS,
            input_text="\n".join(lines),
            schema=ClaimExtractionOutput,
        )
        return result.claims
