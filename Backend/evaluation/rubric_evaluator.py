from __future__ import annotations

import json
from pydantic import BaseModel, Field

from .json_llm import StructuredLLM
from .models import ClaimAssessment, ConversationEvaluation, DialogueTurn, VoiceMetrics


class EvidenceUseEvaluation(BaseModel):
    score: int = Field(ge=0, le=20)
    strengths_ar: list[str] = Field(default_factory=list)
    weaknesses_ar: list[str] = Field(default_factory=list)


EVIDENCE_INSTRUCTIONS = """
أنت مقيم لاستخدام الأدلة في تدريب حواري للتعريف بالإسلام. قيّم فقط طريقة استخدام المتدرب للأدلة التي ذكرها بالفعل، بالاستناد إلى نتائج التحقق المرفقة.

الدرجة من 20 موزعة داخليًا:
- اختيار دليل مناسب عند الحاجة: 5
- صحة نقل/نسبة الدليل: 5
- ارتباط الدليل بالادعاء فعلًا: 5
- شرح الدليل بصورة طبيعية تخدم الحوار: 5

قواعد مهمة:
- لا تعاقب المتدرب لأنه لم يذكر آية أو حديثًا إذا كانت الإجابة الحوارية البسيطة لا تحتاج اقتباسًا صريحًا.
- لا تمنح نقاطًا لمجرد استعمال لغة دينية أو ذكر "قال الله" دون تحقق.
- الدليل المختلق أو المنسوب خطأ لا يأخذ نقاطًا في الصحة والارتباط.
- استخدم claim_assessments كمصدر للحكم على صحة الأدلة المنسوبة.
- اجعل strengths_ar و weaknesses_ar محددة وقصيرة.
""".strip()


CONVERSATION_INSTRUCTIONS = """
أنت مدرب حوار في مشروع محاور. قيّم مهارات المتدرب فقط من النص ومقاييس الصوت المرفقة، ولا تحكم على صحة المعلومات الدينية هنا.

المعايير، كل منها من 10:
1) clarity: وضوح اللغة، بساطتها، وقلة الالتباس.
2) listening_response: هل أجاب سؤال آدم واعتراضه مباشرة بدل تقديم كلام عام غير مرتبط؟
3) wisdom_attitude: الاحترام، الهدوء، عدم التوبيخ أو السخرية أو العدائية، وحسن التعامل مع الاعتراض.
4) answer_structure: تنظيم الجواب وتسلسله، بدء الجواب بالنقطة الأساسية ثم الشرح المناسب.
5) voice_delivery: قيّم فقط من metrics المرفقة: سرعة الكلام، التوقفات، الكلمات الحشوية، وقابلية الفهم الظاهرة. لا تخمن نبرة أو ثقة أو عاطفة غير مقاسة. إذا لم تتوفر مقاييس صوتية كافية فضع 5 كدرجة محايدة واذكر أن التقييم الصوتي محدود.

أعد total كمجموع المعايير الخمسة بالضبط.
استخدم أمثلة محددة من كلام المتدرب في نقاط القوة/الضعف، دون إطالة.
""".strip()


class RubricEvaluator:
    def __init__(self, llm: StructuredLLM):
        self.llm = llm

    def evaluate_evidence_use(
        self,
        turns: list[DialogueTurn],
        assessments: list[ClaimAssessment],
    ) -> EvidenceUseEvaluation:
        payload = {
            "transcript": [t.model_dump() for t in turns],
            "claim_assessments": [a.model_dump() for a in assessments],
        }
        return self.llm.parse(
            instructions=EVIDENCE_INSTRUCTIONS,
            input_text=json.dumps(payload, ensure_ascii=False),
            schema=EvidenceUseEvaluation,
        )

    def evaluate_conversation(self, turns: list[DialogueTurn]) -> ConversationEvaluation:
        payload = {"transcript": [t.model_dump() for t in turns]}
        result = self.llm.parse(
            instructions=CONVERSATION_INSTRUCTIONS,
            input_text=json.dumps(payload, ensure_ascii=False),
            schema=ConversationEvaluation,
        )
        result.total = (
            result.clarity
            + result.listening_response
            + result.wisdom_attitude
            + result.answer_structure
            + result.voice_delivery
        )
        return result
