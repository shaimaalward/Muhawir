from __future__ import annotations

import json
import re
from typing import TypeVar, Type

from openai import OpenAI
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class StructuredLLM:
    """Portable structured-output wrapper around the Responses API.

    We validate every model response with Pydantic and retry once with the
    validation error. This keeps the evaluator usable even if SDK structured
    parsing helpers change.
    """

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    @staticmethod
    def _extract_json(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        first_obj = text.find("{")
        first_arr = text.find("[")
        starts = [x for x in [first_obj, first_arr] if x != -1]
        if starts:
            text = text[min(starts):]
        return text

    def parse(self, *, instructions: str, input_text: str, schema: Type[T]) -> T:
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        base = (
            input_text
            + "\n\nOUTPUT CONTRACT:\nReturn ONLY valid JSON matching this JSON Schema exactly:\n"
            + schema_json
        )
        last_error: Exception | None = None
        for attempt in range(2):
            retry_note = ""
            if attempt and last_error:
                retry_note = f"\n\nYour previous output failed validation: {last_error}. Fix it and output JSON only."
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=base + retry_note,
            )
            try:
                raw = self._extract_json(response.output_text)
                return schema.model_validate(json.loads(raw))
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                last_error = exc
        raise RuntimeError(f"Structured LLM output failed validation: {last_error}")
