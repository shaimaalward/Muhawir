from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openai import OpenAI

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config
from knowledge.connectors import ApprovedWebPageConnector, QuranpediaConnector
from knowledge.models import KnowledgeDocument
from knowledge.registry import SourceRegistry
from knowledge.store import KnowledgeStore


def load_topic(topic_key: str) -> dict:
    path = BACKEND_DIR / "knowledge" / "topics" / f"{topic_key}.json"
    if not path.exists():
        raise SystemExit(f"Unknown topic '{topic_key}'. Expected: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Muhawir KB from approved sources.")
    parser.add_argument("--topic", default="kaaba_qiblah", help="Topic manifest key (default: kaaba_qiblah)")
    parser.add_argument("--reset", action="store_true", help="Delete the existing KB before ingesting")
    parser.add_argument("--skip-web", action="store_true", help="Only fetch structured/API content")
    parser.add_argument("--skip-quran", action="store_true", help="Skip Quranpedia ayahs")
    parser.add_argument("--dry-run", action="store_true", help="Fetch/extract but do not embed/store")
    args = parser.parse_args()

    if not config.OPENAI_API_KEY and not args.dry_run:
        raise SystemExit("OPENAI_API_KEY is required to create embeddings. Put it in backend/.env")

    topic = load_topic(args.topic)
    tags = list(topic.get("tags", []))
    registry = SourceRegistry()

    if args.reset and config.KB_PATH.exists() and not args.dry_run:
        config.KB_PATH.unlink()
        print(f"Deleted existing KB: {config.KB_PATH}")

    quran = QuranpediaConnector()
    web = ApprovedWebPageConnector(registry)
    documents: list[KnowledgeDocument] = []
    failures: list[str] = []

    if not args.skip_quran:
        for item in topic.get("quran_ayahs", []):
            try:
                doc = quran.fetch_ayah(int(item["surah"]), int(item["ayah"]), topics=tags)
                documents.append(doc)
                print(f"[OK] Quran {item['surah']}:{item['ayah']} — {len(doc.text)} chars")
            except Exception as exc:
                msg = f"Quran {item.get('surah')}:{item.get('ayah')}: {exc}"
                failures.append(msg)
                print(f"[FAIL] {msg}")

    if not args.skip_web:
        for item in topic.get("web_pages", []):
            url = item["url"]
            try:
                docs = web.fetch(
                    url=url,
                    source_type=item["source_type"],
                    topics=tags,
                    title_override=item.get("title"),
                    start_marker=item.get("start_marker"),
                    stop_markers=item.get("stop_markers"),
                    min_chars=int(item.get("min_chars", 120)),
                    max_chunk_chars=int(item.get("max_chunk_chars", 1500)),
                )
                documents.extend(docs)
                print(f"[OK] Web {url} — {len(docs)} chunks")
            except Exception as exc:
                msg = f"{url}: {exc}"
                failures.append(msg)
                print(f"[FAIL] {msg}")

    # Deduplicate by deterministic ID.
    documents = list({d.id: d for d in documents}.values())
    if not documents:
        raise SystemExit("No documents were successfully fetched; KB was not modified.")

    print(f"\nPrepared {len(documents)} approved KB documents/chunks.")
    if args.dry_run:
        print("Dry run: nothing was embedded or stored.")
    else:
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        store = KnowledgeStore(config.KB_PATH, client, config.EMBEDDING_MODEL)
        count = store.upsert(documents)
        print(f"Stored/updated {count} documents in: {config.KB_PATH}")
        print(f"Total KB documents: {store.count()}")

    if failures:
        print("\nWarnings (build continued with successful sources):")
        for f in failures:
            print(f" - {f}")


if __name__ == "__main__":
    main()
