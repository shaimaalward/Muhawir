from __future__ import annotations

import json
from .json_llm import StructuredLLM
from .models import CoachingFeedback, ConversationEvaluation, KnowledgeEvaluation


COACH_INSTRUCTIONS = """
أنت مدرب شخصي في مشروع محاور. حوّل نتيجة التقييم إلى تغذية راجعة عربية عملية ومحترمة.

لا تعرض أي أرقام أو درجات للمستخدم.
لا تقل "حصلت على" أو "من 100".
وازن التشخيص بين الجانب المعرفي ومهارات الحوار بناءً على النتائج المرفقة.
اذكر نقاط قوة حقيقية فقط، ونقاط تحسين قابلة للتطبيق في المحاولة التالية.
إذا وُجدت أدلة مقترحة، اذكر أفضل ما كان يمكن الاستفادة منه دون اختلاق أي نص أو مرجع جديد.
لا تضف حقائق دينية من ذاكرتك؛ استخدم فقط المعلومات الموجودة في بيانات التقييم.
next_attempt_ar يجب أن يكون توجيهًا محددًا لما يفعله المتدرب في المحاولة القادمة.
""".strip()


class Coach:
    def __init__(self, llm: StructuredLLM):
        self.llm = llm

    def generate(
        self,
        knowledge: KnowledgeEvaluation,
        conversation: ConversationEvaluation,
        critical_errors: list[str],
    ) -> CoachingFeedback:
        payload = {
            "knowledge": knowledge.model_dump(),
            "conversation": conversation.model_dump(),
            "critical_errors": critical_errors,
        }
        return self.llm.parse(
            instructions=COACH_INSTRUCTIONS,
            input_text=json.dumps(payload, ensure_ascii=False),
            schema=CoachingFeedback,
        )
