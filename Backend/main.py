from __future__ import annotations

import base64
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

import config
from evaluation.claim_extractor import ClaimExtractor
from evaluation.claim_verifier import ClaimVerifier
from evaluation.coach import Coach
from evaluation.json_llm import StructuredLLM
from evaluation.rubric_evaluator import RubricEvaluator
from evaluation.service import EvaluationService
from evaluation.voice_analysis import analyze_voice
from knowledge.registry import SourceRegistry
from knowledge.retriever import HybridRetriever
from knowledge.store import KnowledgeStore
from session_store import SessionStore


# =========================================================
# SETUP
# =========================================================

if not config.OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Create backend/.env from .env.example."
    )


client = OpenAI(
    api_key=config.OPENAI_API_KEY
)

app = FastAPI(
    title="Muhawir"
)

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# LOAD PERSONA PROMPTS
# =========================================================

with (
    BASE_DIR / "prompts" / "adam.txt"
).open(
    "r",
    encoding="utf-8",
) as file:
    adam_prompt = file.read()


with (
    BASE_DIR / "prompts" / "maya.txt"
).open(
    "r",
    encoding="utf-8",
) as file:
    maya_prompt = file.read()


# =========================================================
# SERVICES
# =========================================================

sessions = SessionStore()

registry = SourceRegistry()

kb_store = KnowledgeStore(
    db_path=config.KB_PATH,
    client=client,
    embedding_model=config.EMBEDDING_MODEL,
)

retriever = HybridRetriever(
    kb_store,
    registry,
)

structured_llm = StructuredLLM(
    client=client,
    model=config.EVALUATOR_MODEL,
)

evaluation_service = EvaluationService(
    retriever=retriever,
    claim_extractor=ClaimExtractor(
        structured_llm
    ),
    claim_verifier=ClaimVerifier(
        structured_llm
    ),
    rubric_evaluator=RubricEvaluator(
        structured_llm
    ),
    coach=Coach(
        structured_llm
    ),
)


# =========================================================
# PERSONA HELPERS
# =========================================================

def _normalize_persona_id(
    persona_id: str | None,
) -> str:
    value = (
        persona_id or "adam"
    ).strip().lower()

    if value not in {
        "adam",
        "maya",
    }:
        return "adam"

    return value


def _persona_name(
    persona_id: str,
) -> str:
    if persona_id == "maya":
        return "مايا"

    return "آدم"


def _persona_prompt(
    persona_id: str,
) -> str:
    if persona_id == "maya":
        return maya_prompt

    return adam_prompt


def _persona_instructions(
    persona_id: str,
    topic_title: str | None,
) -> str:
    """
    Combine the persona's permanent prompt with
    the selected training topic.

    The persona should know which topic the trainee
    selected without receiving religious answers
    from the application itself.
    """

    prompt = _persona_prompt(
        persona_id
    )

    topic_context = (
        topic_title.strip()
        if topic_title
        and topic_title.strip()
        else "الموضوع المحدد للجلسة"
    )

    return f"""
{prompt}

==================================================
CURRENT TRAINING SESSION
==================================================

Selected topic:
{topic_context}

Stay centered on this topic.

Respond to what the trainee actually says.

Do not restart the conversation.
Do not introduce yourself again.
Do not suddenly move to an unrelated Islamic topic.

The opening question may already appear earlier in
the conversation history.

Continue naturally from the existing conversation.
""".strip()


def _persona_voice(
    persona_id: str,
) -> str:
    """
    Adam keeps the existing configured voice.
    Maya uses a separate voice.
    """

    if persona_id == "maya":
        return "coral"

    return config.TTS_VOICE


def _persona_tts_instructions(
    persona_id: str,
) -> str:

    if persona_id == "maya":
        return """
Speak in natural Arabic.

You are Maya, a young Arabic-speaking woman in her mid twenties.

Your speaking style should be:
- feminine
- calm
- thoughtful
- intelligent
- confident
- analytical
- conversational

You are speaking directly to another person in a real conversation.

Do not sound like:
- a narrator
- a news presenter
- an automated assistant
- someone reading a script

Use natural Arabic pronunciation and intonation.

When you question something, sound genuinely curious and thoughtful,
not aggressive or confrontational.

When something makes sense, react naturally.

When you disagree or remain unconvinced, sound polite and composed.

Do not make every sentence sound like a question.

Speak at a comfortable conversational speed.

Do not sound robotic or overly formal.
""".strip()

    return """
Speak in natural Arabic.

You are Adam, a friendly young Arabic-speaking man in his early twenties.

Your speaking style should be:
- warm
- relaxed
- friendly
- curious
- approachable
- natural

You are speaking directly to another person in a real conversation.

Do not sound like:
- a narrator
- a news presenter
- an automated assistant
- someone reading a script

Use natural Arabic pronunciation and intonation.

React naturally to what the other person says.

Some responses should sound like genuine reactions or acknowledgements,
not questions.

Do not make every sentence sound like a question.

Do not repeatedly sound as if you are interviewing the trainee.

Speak at a comfortable conversational speed.

Do not sound robotic or overly formal.
""".strip()


# =========================================================
# OPENAI CONVERSATION
# =========================================================

def _openai_conversation(
    session_id: str,
) -> list[dict]:

    messages: list[dict] = []

    for turn in sessions.get(
        session_id
    ):

        messages.append(
            {
                "role": (
                    "user"
                    if turn.speaker
                    == "trainee"
                    else "assistant"
                ),
                "content": turn.text,
            }
        )

    return messages


# =========================================================
# TALK
# =========================================================

@app.post("/talk")
async def talk(
    audio: UploadFile = File(...),
    session_id: str = Form("default"),
    persona_id: str = Form("adam"),
    topic_id: str | None = Form(None),
    topic_title: str | None = Form(None),
    opening: str | None = Form(None),
):
    temp_path: str | None = None

    try:
        # -------------------------------------------------
        # Normalize selected persona
        # -------------------------------------------------

        persona_id = _normalize_persona_id(
            persona_id
        )

        # -------------------------------------------------
        # Save session context
        # -------------------------------------------------

        sessions.set_context(
            session_id,
            persona_id=persona_id,
            topic_id=topic_id,
            topic_title=topic_title,
        )

        # -------------------------------------------------
        # Save the opening question once
        #
        # The frontend already displays the persona's
        # opening question before the trainee speaks.
        #
        # Previously this opening existed only in the UI.
        # Now the backend session also knows about it.
        # -------------------------------------------------

        existing_turns = sessions.get(
            session_id
        )

        if (
            not existing_turns
            and opening
            and opening.strip()
        ):
            sessions.add_adam(
                session_id,
                opening.strip(),
            )

        # -------------------------------------------------
        # Read uploaded audio
        # -------------------------------------------------

        audio_bytes = await audio.read()

        original_filename = (
            audio.filename
            or "recording.webm"
        )

        extension = (
            os.path.splitext(
                original_filename
            )[1]
            or ".webm"
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_audio:

            temp_audio.write(
                audio_bytes
            )

            temp_path = (
                temp_audio.name
            )

        # =================================================
        # 1. SPEECH -> TEXT
        # =================================================

        with open(
            temp_path,
            "rb",
        ) as audio_file:

            transcription = (
                client.audio.transcriptions.create(
                    model=config.TRANSCRIPTION_MODEL,
                    file=audio_file,
                    language="ar",
                )
            )

        user_text = (
            transcription.text.strip()
        )

        if not user_text:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No speech was transcribed."
                ),
            )

        # =================================================
        # 2. VOICE DELIVERY ANALYSIS
        # =================================================

        voice_metrics = analyze_voice(
            temp_path,
            user_text,
        )

        sessions.add_trainee(
            session_id,
            user_text,
            voice_metrics,
        )

        # =================================================
        # 3. PERSONA RESPONSE
        # =================================================

        response = client.responses.create(
            model=config.ADAM_MODEL,
            instructions=_persona_instructions(
                persona_id,
                topic_title,
            ),
            input=_openai_conversation(
                session_id
            ),
        )

        persona_text = (
            response.output_text.strip()
        )

        # We keep using add_adam internally because the
        # evaluator treats this as the conversation-partner
        # side of the dialogue.
        sessions.add_adam(
            session_id,
            persona_text,
        )

        # =================================================
        # 4. PERSONA VOICE
        # =================================================

        speech_response = (
            client.audio.speech.create(
                model=config.TTS_MODEL,
                voice=_persona_voice(
                    persona_id
                ),
                input=persona_text,
                instructions=(
                    _persona_tts_instructions(
                        persona_id
                    )
                ),
            )
        )

        persona_audio_base64 = (
            base64.b64encode(
                speech_response.read()
            ).decode(
                "utf-8"
            )
        )

        # =================================================
        # RESPONSE TO FRONTEND
        #
        # adam_text and adam_audio are intentionally kept
        # for compatibility with the existing app.js.
        #
        # They contain Maya's response/audio when Maya
        # is selected.
        # =================================================

        return {
            "session_id": session_id,

            "persona_id": persona_id,

            "persona_name": (
                _persona_name(
                    persona_id
                )
            ),

            "user_text": user_text,

            "adam_text": persona_text,

            "adam_audio": (
                persona_audio_base64
            ),

            "voice_metrics": (
                voice_metrics.model_dump()
            ),
        }

    finally:
        if (
            temp_path
            and os.path.exists(
                temp_path
            )
        ):
            try:
                os.remove(
                    temp_path
                )

            except OSError:
                pass


# =========================================================
# REAL EVALUATION PIPELINE
#
# transcript
# -> claims
# -> approved RAG
# -> verification
# -> rubric
# -> coaching
# =========================================================

@app.post("/evaluate")
async def evaluate_session(
    session_id: str = "default",
    include_internal: bool = False,
):
    # -----------------------------------------------------
    # Knowledge base must contain approved material
    # -----------------------------------------------------

    if kb_store.count() == 0:
        raise HTTPException(
            status_code=503,
            detail=(
                "Muhawir knowledge base is empty. "
                "Ingest approved source content before "
                "running evaluation."
            ),
        )

    # -----------------------------------------------------
    # Load dialogue
    # -----------------------------------------------------

    turns = sessions.get(
        session_id
    )

    trainee_turns = [
        turn
        for turn in turns
        if turn.speaker
        == "trainee"
    ]

    if not trainee_turns:
        raise HTTPException(
            status_code=400,
            detail=(
                "No trainee dialogue exists "
                "for this session."
            ),
        )

    # -----------------------------------------------------
    # Get selected topic
    # -----------------------------------------------------

    context = sessions.get_context(
        session_id
    )

    # -----------------------------------------------------
    # Evaluate
    # -----------------------------------------------------

    result = (
        evaluation_service.evaluate(
            turns,
            topic_id=context.topic_id,
        )
    )

    payload = (
        result.model_dump()
    )

    # -----------------------------------------------------
    # Public/user-facing evaluation
    #
    # Internal numerical scores can be hidden in production.
    # -----------------------------------------------------

    if not include_internal:

        payload.pop(
            "internal_scores",
            None,
        )

        payload[
            "knowledge"
        ].pop(
            "accuracy_score",
            None,
        )

        payload[
            "knowledge"
        ].pop(
            "evidence_score",
            None,
        )

        payload[
            "knowledge"
        ].pop(
            "total",
            None,
        )

        payload[
            "conversation"
        ].pop(
            "clarity",
            None,
        )

        payload[
            "conversation"
        ].pop(
            "listening_response",
            None,
        )

        payload[
            "conversation"
        ].pop(
            "wisdom_attitude",
            None,
        )

        payload[
            "conversation"
        ].pop(
            "answer_structure",
            None,
        )

        payload[
            "conversation"
        ].pop(
            "voice_delivery",
            None,
        )

        payload[
            "conversation"
        ].pop(
            "total",
            None,
        )

    return payload


# =========================================================
# KNOWLEDGE BASE STATUS
# =========================================================

@app.get("/kb/status")
async def kb_status():

    return {
        "documents": (
            kb_store.count()
        ),

        "database": str(
            config.KB_PATH
        ),

        "approved_sources": len(
            registry.sources
        ),
    }


# =========================================================
# RESET SESSION
# =========================================================

@app.post("/session/reset")
async def reset_session(
    session_id: str = "default",
):

    sessions.reset(
        session_id
    )

    return {
        "ok": True,
        "session_id": session_id,
    }


# =========================================================
# MANUAL EVALUATION
# =========================================================

class ManualEvaluationRequest(
    BaseModel
):
    turns: list[dict] = Field(
        min_length=1
    )

    topic_id: str | None = None

    topic_title: str | None = None


@app.post("/evaluate/manual")
async def evaluate_manual(
    request: ManualEvaluationRequest,
):
    """
    Development endpoint.

    Evaluate a supplied full conversation directly.

    This bypasses the microphone/UI but uses the
    same claim extraction, RAG, verification,
    conversation rubric and coaching pipeline.
    """

    from evaluation.models import (
        DialogueTurn,
    )

    if kb_store.count() == 0:
        raise HTTPException(
            status_code=503,
            detail=(
                "Muhawir knowledge base is empty."
            ),
        )

    try:
        turns = [
            DialogueTurn(
                **turn
            )
            for turn
            in request.turns
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid conversation payload: "
                f"{exc}"
            ),
        ) from exc

    if not any(
        turn.speaker
        == "trainee"
        for turn
        in turns
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "No trainee dialogue exists "
                "in payload."
            ),
        )

    return (
        evaluation_service.evaluate(
            turns,
            topic_id=request.topic_id,
        ).model_dump()
    )


# =========================================================
# WEBSITE
# =========================================================

app.mount(
    "/",
    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        ),
        html=True,
    ),
    name="static",
)
