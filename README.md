<p align="center">
  <img src="backend/static/assets/muhawir-logo.png" alt="Muhawir Logo" width="220">
</p>

# Muhawir | محاور

**Muhawir** is an AI-powered Islamic dialogue training platform. It lets a learner practice explaining Islamic concepts in a natural conversation, then evaluates the learner's answers against an approved knowledge base and provides evidence-grounded coaching.

The project was built for the **AI Challenge Serving Islamic Content 2026**.

## What Muhawir does

A learner has a conversation with an AI dialogue partner about Islamic topics. At the end of the session, Muhawir:

- extracts the learner's factual/religious claims,
- retrieves relevant evidence from the approved knowledge base,
- checks whether each claim is supported, partially supported, contradicted, or lacks sufficient evidence,
- evaluates conversation quality,
- generates practical coaching and suggested references,
- shows the feedback directly in the web interface.

Muhawir is designed as a **training and evaluation tool**, not as an independent fatwa system.

## Main features

- Natural AI dialogue practice
- Arabic-focused Islamic knowledge base
- Retrieval-Augmented Generation (RAG)
- Hybrid lexical + semantic retrieval
- Evidence-based claim verification
- Topic-based knowledge organization
- End-of-conversation evaluation
- Coaching feedback and suggested references
- Source traceability
- Safety-aware handling of unsupported or sensitive claims

## Knowledge sources

The knowledge base is built only from approved source families used by the project, including:

- Quranpedia — Qur'an text and references
- Dorar — Hadith, Tafsir and Aqeedah resources
- Dawa Center — Islamic educational resources
- Islamic Content — Islamic educational material

Topic manifests are stored in:

```text
backend/knowledge/topics/
```

The built SQLite knowledge base is stored in:

```text
backend/knowledge/data/knowledge.db
```

## Project structure

```text
Muhawir/
├── README.md
├── LICENSE
├── .gitignore
└── backend/
    ├── main.py
    ├── config.py
    ├── session_store.py
    ├── requirements.txt
    ├── .env.example
    ├── evaluation/
    ├── knowledge/
    │   ├── connectors/
    │   ├── data/
    │   └── topics/
    ├── prompts/
    ├── scripts/
    └── static/
```

## Requirements

- Python 3.11+ recommended
- OpenAI API key
- Internet connection for AI calls and for rebuilding web-based knowledge sources

## Local setup

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Muhawir/backend
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the application

```bash
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Knowledge base workflow

The repository includes a prebuilt `knowledge.db` for easier testing and deployment.

To rebuild a topic:

```bash
python scripts/build_kb.py --topic prayer
```

To rebuild the KB from scratch, use `--reset` only for the first topic, then add the remaining topics without it.

Example:

```bash
python scripts/build_kb.py --topic kaaba_qiblah --reset
python scripts/build_kb.py --topic prophets
python scripts/build_kb.py --topic quran_preservation
```

## Evaluation pipeline

```text
Conversation
    ↓
Claim extraction
    ↓
Knowledge-base retrieval
    ↓
Claim verification
    ↓
Knowledge scoring
    ↓
Conversation-skill evaluation
    ↓
Coaching feedback + references
```

Religious claims are evaluated against retrieved evidence rather than treated as correct solely from model memory. When the knowledge base does not contain sufficient evidence, the system can return an insufficient-evidence result instead of inventing support.

## Important design principles

- Trace religious claims back to approved sources.
- Distinguish source evidence from AI-generated explanation.
- Do not fabricate Qur'anic, Hadith, or scholarly attribution.
- Prefer caution when evidence is insufficient.
- Do not provide independent personalized fatwas.
- Keep internal numeric evaluation scores separate from learner-facing coaching where appropriate.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

