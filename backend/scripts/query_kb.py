from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from knowledge.registry import SourceRegistry
from knowledge.retriever import HybridRetriever
from knowledge.store import KnowledgeStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the entire approved Muhawir knowledge base.")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=8)
    # Kept only so old commands do not fail. It is intentionally ignored.
    parser.add_argument("--domain", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if not config.OPENAI_API_KEY:
        raise SystemExit("OPENAI_API_KEY is missing from backend/.env")

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    store = KnowledgeStore(config.KB_PATH, client, config.EMBEDDING_MODEL)
    registry = SourceRegistry()
    retriever = HybridRetriever(store, registry)
    result = retriever.retrieve(args.query, top_k=args.top_k)

    print(f"Evidence sufficient: {result.evidence_sufficient}\n")
    for i, item in enumerate(result.evidence, start=1):
        print(f"[{i}] {item.title}")
        print(f"    source={item.source_name} type={item.source_type} score={item.combined_score:.3f}")
        print(f"    {item.source_url}")
        print(f"    {item.text[:700]}\n")


if __name__ == "__main__":
    main()
