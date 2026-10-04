import os
import tempfile
import base64

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from openai import OpenAI


# =========================================================
# SETUP
# =========================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()


# =========================================================
# LOAD ADAM
# =========================================================

with open("prompts/adam.txt", "r", encoding="utf-8") as file:
    adam_prompt = file.read()


# Temporary conversation memory for MVP
conversation = []


# =========================================================
# TALK
# =========================================================

@app.post("/talk")
async def talk(audio: UploadFile = File(...)):

    temp_path = None

    try:

        # -------------------------------------------------
        # 1. RECEIVE USER AUDIO
        # -------------------------------------------------

        audio_bytes = await audio.read()

        print("\n----------------------------")
        print("Received audio:", audio.filename)
        print("Content type:", audio.content_type)
        print("Audio size:", len(audio_bytes), "bytes")
        print("----------------------------")


        # -------------------------------------------------
        # 2. DETECT AUDIO EXTENSION
        # -------------------------------------------------

        original_filename = audio.filename or "recording.webm"

        extension = os.path.splitext(original_filename)[1]

        if not extension:
            extension = ".webm"


        # -------------------------------------------------
        # 3. SAVE TEMPORARY RECORDING
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_audio:

            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name


        # -------------------------------------------------
        # 4. ARABIC SPEECH → TEXT
        # -------------------------------------------------

        with open(temp_path, "rb") as audio_file:

            transcription = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file,
                language="ar"
            )


        user_text = transcription.text

        print("\nUSER:")
        print(user_text)


        # -------------------------------------------------
        # 5. SAVE USER MESSAGE
        # -------------------------------------------------

        conversation.append({
            "role": "user",
            "content": user_text
        })


        # -------------------------------------------------
        # 6. ADAM THINKS AND RESPONDS
        # -------------------------------------------------

        response = client.responses.create(
            model="gpt-5.4-mini",
            instructions=adam_prompt,
            input=conversation
        )


        adam_text = response.output_text

        print("\nADAM:")
        print(adam_text)


        # -------------------------------------------------
        # 7. SAVE ADAM MESSAGE
        # -------------------------------------------------

        conversation.append({
            "role": "assistant",
            "content": adam_text
        })


        # -------------------------------------------------
        # 8. ADAM TEXT → NATURAL VOICE
        # -------------------------------------------------

        speech_response = client.audio.speech.create(
            model="gpt-4o-mini-tts",

            voice="cedar",

            input=adam_text,

            instructions="""
Speak in natural Arabic.

You are Adam, a friendly young Arabic-speaking man
in his early twenties.

Sound curious, relaxed, warm, and conversational.

You are talking directly to another person,
not reading a script or narrating.

Use natural Arabic pronunciation and intonation.

Do not sound like a news presenter.

Do not sound overly formal.

Do not sound robotic.

Speak at a comfortable conversational speed.
"""
        )


        # -------------------------------------------------
        # 9. CONVERT AUDIO TO BASE64
        # -------------------------------------------------

        adam_audio_bytes = speech_response.read()

        adam_audio_base64 = base64.b64encode(
            adam_audio_bytes
        ).decode("utf-8")


        # -------------------------------------------------
        # 10. SEND EVERYTHING TO WEBSITE
        # -------------------------------------------------

        return {
            "user_text": user_text,
            "adam_text": adam_text,
            "adam_audio": adam_audio_base64
        }


    except Exception as error:

        print("\nERROR:")
        print(error)

        raise error


    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)

            except:
                pass


# =========================================================
# WEBSITE
# =========================================================

app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True
    ),
    name="static"
)
