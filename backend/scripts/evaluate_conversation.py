from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from evaluation.claim_extractor import ClaimExtractor
from evaluation.claim_verifier import ClaimVerifier
from evaluation.coach import Coach
from evaluation.json_llm import StructuredLLM
from evaluation.models import DialogueTurn
from evaluation.rubric_evaluator import RubricEvaluator
from evaluation.service import EvaluationService
from knowledge.registry import SourceRegistry
from knowledge.retriever import HybridRetriever
from knowledge.store import KnowledgeStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Muhawir's full real evaluation pipeline on a conversation JSON file.")
    parser.add_argument("conversation", help="Path to JSON file containing {'turns': [...]}.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    if not config.OPENAI_API_KEY:
        raise SystemExit("OPENAI_API_KEY is missing from backend/.env")

    path = Path(args.conversation)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    turns = [DialogueTurn(**item) for item in payload.get("turns", [])]
    if not turns:
        raise SystemExit("Conversation file contains no turns.")

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    registry = SourceRegistry()
    store = KnowledgeStore(config.KB_PATH, client, config.EMBEDDING_MODEL)
    if store.count() == 0:
        raise SystemExit("Knowledge base is empty. Build it first with scripts/build_kb.py.")

    retriever = HybridRetriever(store, registry)
    llm = StructuredLLM(client, config.EVALUATOR_MODEL)
    service = EvaluationService(
        retriever=retriever,
        claim_extractor=ClaimExtractor(llm),
        claim_verifier=ClaimVerifier(llm),
        rubric_evaluator=RubricEvaluator(llm),
        coach=Coach(llm),
    )

    result = service.evaluate(turns)
    indent = 2 if args.pretty else None
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
