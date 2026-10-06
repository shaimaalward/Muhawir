from __future__ import annotations

from collections import defaultdict
from threading import Lock

from pydantic import BaseModel

from evaluation.models import DialogueTurn, VoiceMetrics


class SessionContext(BaseModel):
    persona_id: str = "adam"
    topic_id: str | None = None
    topic_title: str | None = None


class SessionStore:
    def __init__(self):
        self._turns: dict[str, list[DialogueTurn]] = defaultdict(list)
        self._contexts: dict[str, SessionContext] = {}
        self._lock = Lock()

    def set_context(
        self,
        session_id: str,
        *,
        persona_id: str = "adam",
        topic_id: str | None = None,
        topic_title: str | None = None,
    ) -> None:
        """Save the training context selected by the frontend for this session."""
        with self._lock:
            existing = self._contexts.get(session_id, SessionContext())
            self._contexts[session_id] = SessionContext(
                persona_id=persona_id or existing.persona_id,
                topic_id=topic_id or existing.topic_id,
                topic_title=topic_title or existing.topic_title,
            )

    def get_context(self, session_id: str) -> SessionContext:
        with self._lock:
            context = self._contexts.get(session_id, SessionContext())
            return SessionContext.model_validate(context.model_dump())

    def add_trainee(self, session_id: str, text: str, metrics: VoiceMetrics | None = None) -> None:
        with self._lock:
            idx = len(self._turns[session_id])
            self._turns[session_id].append(
                DialogueTurn(speaker="trainee", text=text, turn_index=idx, audio_metrics=metrics)
            )

    def add_adam(self, session_id: str, text: str) -> None:
        with self._lock:
            idx = len(self._turns[session_id])
            self._turns[session_id].append(
                DialogueTurn(speaker="adam", text=text, turn_index=idx)
            )

    def get(self, session_id: str) -> list[DialogueTurn]:
        with self._lock:
            return [
                DialogueTurn.model_validate(t.model_dump())
                for t in self._turns.get(session_id, [])
            ]

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._turns.pop(session_id, None)
            self._contexts.pop(session_id, None)
