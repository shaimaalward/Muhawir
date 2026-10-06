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
        "OPENAI_API_KEY is missing. "
        "Set OPENAI_API_KEY in the deployment environment."
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
# AUDIO HELPERS
# =========================================================

def _detect_audio_extension(
    audio_bytes: bytes,
    filename: str | None,
    content_type: str | None,
) -> str:
    """
    Determine the actual audio format as reliably as possible.

    This is important in browsers because MediaRecorder may create
    WebM, MP4, OGG, WAV, or MP3 depending on the browser/device.
    """

    # -----------------------------------------------------
    # Detect using the actual file bytes first
    # -----------------------------------------------------

    if len(audio_bytes) >= 12:

        # WAV
        if (
            audio_bytes[:4] == b"RIFF"
            and audio_bytes[8:12] == b"WAVE"
        ):
            return ".wav"

        # OGG
        if audio_bytes[:4] == b"OggS":
            return ".ogg"

        # MP4 / M4A
        if audio_bytes[4:8] == b"ftyp":
            return ".mp4"

        # WebM / Matroska
        if audio_bytes[:4] == b"\x1a\x45\xdf\xa3":
            return ".webm"

        # MP3 with ID3
        if audio_bytes[:3] == b"ID3":
            return ".mp3"

        # MP3 frame
        if (
            audio_bytes[0] == 0xFF
            and (audio_bytes[1] & 0xE0) == 0xE0
        ):
            return ".mp3"

    # -----------------------------------------------------
    # Fall back to browser MIME type
    # -----------------------------------------------------

    mime = (
        content_type or ""
    ).lower()

    if "webm" in mime:
        return ".webm"

    if "ogg" in mime:
        return ".ogg"

    if "wav" in mime:
        return ".wav"

    if "mp4" in mime:
        return ".mp4"

    if "m4a" in mime:
        return ".m4a"

    if "mpeg" in mime or "mp3" in mime:
        return ".mp3"

    # -----------------------------------------------------
    # Fall back to filename
    # -----------------------------------------------------

    if filename:
        extension = Path(
            filename
        ).suffix.lower()

        if extension in {
            ".webm",
            ".wav",
            ".mp3",
            ".mp4",
            ".m4a",
            ".ogg",
            ".mpeg",
            ".mpga",
        }:
            return extension

    # Browser default
    return ".webm"


def _voice_metrics_payload(
    voice_metrics,
) -> dict:

    if voice_metrics is None:
        return {}

    try:
        return voice_metrics.model_dump()

    except Exception:
        return {}


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

        # =================================================
        # PERSONA
        # =================================================

        persona_id = _normalize_persona_id(
            persona_id
        )

        # =================================================
        # SESSION CONTEXT
        # =================================================

        sessions.set_context(
            session_id,
            persona_id=persona_id,
            topic_id=topic_id,
            topic_title=topic_title,
        )

        # =================================================
        # SAVE OPENING QUESTION ONCE
        # =================================================

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

        # =================================================
        # READ UPLOADED AUDIO
        # =================================================

        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=422,
                detail="The uploaded audio recording is empty.",
            )

        print(
            "AUDIO RECEIVED:",
            f"bytes={len(audio_bytes)}",
            f"filename={audio.filename}",
            f"content_type={audio.content_type}",
            flush=True,
        )

        extension = _detect_audio_extension(
            audio_bytes=audio_bytes,
            filename=audio.filename,
            content_type=audio.content_type,
        )

        print(
            "AUDIO FORMAT:",
            extension,
            flush=True,
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_audio:

            temp_audio.write(
                audio_bytes
            )

            temp_audio.flush()

            temp_path = (
                temp_audio.name
            )

        print(
            "TEMP AUDIO:",
            temp_path,
            flush=True,
        )

        # =================================================
        # 1. SPEECH -> TEXT
        # =================================================

        try:

            print(
                "TRANSCRIPTION STARTING...",
                flush=True,
            )

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
                transcription.text or ""
            ).strip()

            print(
                "TRANSCRIPTION SUCCESS:",
                user_text,
                flush=True,
            )

        except Exception as exc:

            print(
                "TRANSCRIPTION ERROR:",
                type(exc).__name__,
                repr(exc),
                flush=True,
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Transcription failed: "
                    f"{type(exc).__name__}: {str(exc)}"
                ),
            ) from exc

        if not user_text:
            raise HTTPException(
                status_code=422,
                detail="No speech was transcribed.",
            )

        # =================================================
        # 2. VOICE DELIVERY ANALYSIS
        #
        # IMPORTANT:
        # Voice analysis is useful for evaluation, but it
        # must NEVER stop the actual conversation.
        #
        # If FFmpeg / audio decoding / librosa behaves
        # differently on the server, we skip this metric
        # rather than returning HTTP 500.
        # =================================================

        voice_metrics = None

        try:

            print(
                "VOICE ANALYSIS STARTING...",
                flush=True,
            )

            voice_metrics = analyze_voice(
                temp_path,
                user_text,
            )

            print(
                "VOICE ANALYSIS SUCCESS",
                flush=True,
            )

        except Exception as exc:

            print(
                "VOICE ANALYSIS SKIPPED:",
                type(exc).__name__,
                repr(exc),
                flush=True,
            )

            voice_metrics = None

        # =================================================
        # SAVE TRAINEE TURN
        # =================================================

        try:

            sessions.add_trainee(
                session_id,
                user_text,
                voice_metrics,
            )

        except Exception as first_exc:

            # Some SessionStore implementations may allow
            # a trainee turn without voice metrics.

            print(
                "SESSION VOICE METRICS FALLBACK:",
                repr(first_exc),
                flush=True,
            )

            try:

                sessions.add_trainee(
                    session_id,
                    user_text,
                )

            except TypeError:

                # If the method requires the third argument,
                # try explicitly passing None.

                sessions.add_trainee(
                    session_id,
                    user_text,
                    None,
                )

        # =================================================
        # 3. PERSONA RESPONSE
        # =================================================

        try:

            print(
                "PERSONA RESPONSE STARTING...",
                flush=True,
            )

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
                response.output_text or ""
            ).strip()

            if not persona_text:
                raise RuntimeError(
                    "OpenAI returned an empty persona response."
                )

            print(
                "PERSONA RESPONSE SUCCESS:",
                persona_text,
                flush=True,
            )

        except Exception as exc:

            print(
                "PERSONA RESPONSE ERROR:",
                type(exc).__name__,
                repr(exc),
                flush=True,
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Persona response failed: "
                    f"{type(exc).__name__}: {str(exc)}"
                ),
            ) from exc

        # =================================================
        # SAVE PERSONA TURN
        # =================================================

        sessions.add_adam(
            session_id,
            persona_text,
        )

        # =================================================
        # 4. PERSONA TEXT -> SPEECH
        #
        # TTS should also not destroy the whole conversation
        # if the audio generation fails.
        # =================================================

        persona_audio_base64 = ""

        try:

            print(
                "TTS STARTING...",
                flush=True,
            )

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

            speech_bytes = (
                speech_response.read()
            )

            persona_audio_base64 = (
                base64.b64encode(
                    speech_bytes
                ).decode(
                    "utf-8"
                )
            )

            print(
                "TTS SUCCESS",
                flush=True,
            )

        except Exception as exc:

            print(
                "TTS ERROR - CONTINUING WITHOUT AUDIO:",
                type(exc).__name__,
                repr(exc),
                flush=True,
            )

            persona_audio_base64 = ""

        # =================================================
        # RESPONSE TO FRONTEND
        #
        # adam_text / adam_audio names are intentionally
        # preserved because app.js already expects them.
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
                _voice_metrics_payload(
                    voice_metrics
                )
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            "UNEXPECTED TALK ERROR:",
            type(exc).__name__,
            repr(exc),
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Talk request failed: "
                f"{type(exc).__name__}: {str(exc)}"
            ),
        ) from exc

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

    # =====================================================
    # KNOWLEDGE BASE CHECK
    # =====================================================

    if kb_store.count() == 0:
        raise HTTPException(
            status_code=503,
            detail=(
                "Muhawir knowledge base is empty. "
                "Ingest approved source content before "
                "running evaluation."
            ),
        )

    # =====================================================
    # LOAD DIALOGUE
    # =====================================================

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

    # =====================================================
    # GET TOPIC
    # =====================================================

    context = sessions.get_context(
        session_id
    )

    # =====================================================
    # EVALUATE
    # =====================================================

    result = (
        evaluation_service.evaluate(
            turns,
            topic_id=context.topic_id,
        )
    )

    payload = (
        result.model_dump()
    )

    # =====================================================
    # REMOVE INTERNAL NUMERIC SCORES FROM PUBLIC RESULT
    # =====================================================

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
