from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Iterable

from openai import OpenAI

from .models import KnowledgeDocument, RetrievedEvidence


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class KnowledgeStore:
    """
    Small/medium local hybrid RAG store.

    - SQLite keeps canonical text + metadata.
    - FTS5 provides exact/lexical Arabic retrieval.
    - OpenAI embeddings provide semantic retrieval.

    This deliberately avoids introducing a separate vector database for the
    hackathon. If the corpus becomes large, the interface can later be backed
    by pgvector/Qdrant without changing the evaluator.
    """

    def __init__(
        self,
        db_path: str | Path,
        client: OpenAI,
        embedding_model: str,
    ):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.client = client
        self.embedding_model = embedding_model
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    source_key TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    language TEXT NOT NULL,
                    authority_level INTEGER NOT NULL,
                    topic_tags TEXT NOT NULL,
                    citation_label TEXT,
                    external_id TEXT,
                    metadata TEXT NOT NULL,
                    embedding TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    id UNINDEXED,
                    title,
                    text,
                    topic_tags,
                    tokenize='unicode61'
                )
                """
            )
            conn.commit()

    def _embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=texts,
        )
        # API returns data in input order.
        return [item.embedding for item in response.data]

    def upsert(self, documents: Iterable[KnowledgeDocument], batch_size: int = 64) -> int:
        docs = list(documents)
        if not docs:
            return 0

        inserted = 0
        for start in range(0, len(docs), batch_size):
            batch = docs[start:start + batch_size]
            embeddings = self._embed([f"{d.title}\n{d.text}" for d in batch])
            with self.connect() as conn:
                for doc, emb in zip(batch, embeddings):
                    conn.execute(
                        """
                        INSERT INTO documents (
                            id, source_key, source_name, source_url, source_type,
                            title, text, language, authority_level, topic_tags,
                            citation_label, external_id, metadata, embedding
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            source_key=excluded.source_key,
                            source_name=excluded.source_name,
                            source_url=excluded.source_url,
                            source_type=excluded.source_type,
                            title=excluded.title,
                            text=excluded.text,
                            language=excluded.language,
                            authority_level=excluded.authority_level,
                            topic_tags=excluded.topic_tags,
                            citation_label=excluded.citation_label,
                            external_id=excluded.external_id,
                            metadata=excluded.metadata,
                            embedding=excluded.embedding
                        """,
                        (
                            doc.id, doc.source_key, doc.source_name, doc.source_url,
                            doc.source_type, doc.title, doc.text, doc.language,
                            doc.authority_level, json.dumps(doc.topic_tags, ensure_ascii=False),
                            doc.citation_label, doc.external_id,
                            json.dumps(doc.metadata, ensure_ascii=False),
                            json.dumps(emb),
                        ),
                    )
                    conn.execute("DELETE FROM documents_fts WHERE id = ?", (doc.id,))
                    conn.execute(
                        "INSERT INTO documents_fts(id, title, text, topic_tags) VALUES (?, ?, ?, ?)",
                        (doc.id, doc.title, doc.text, " ".join(doc.topic_tags)),
                    )
                    inserted += 1
                conn.commit()
        return inserted

    def count(self) -> int:
        with self.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0])

    def lexical_search(
        self,
        query: str,
        limit: int = 20,
        source_keys: list[str] | None = None,
        source_types: list[str] | None = None,
    ) -> dict[str, float]:
        # Quote tokens individually to make arbitrary Arabic text safe for FTS MATCH.
        tokens = [t.strip() for t in query.replace('"', ' ').split() if len(t.strip()) > 1]
        if not tokens:
            return {}
        match_query = " OR ".join(f'"{t}"' for t in tokens[:20])

        sql = """
            SELECT d.id, bm25(documents_fts) AS rank
            FROM documents_fts
            JOIN documents d ON d.id = documents_fts.id
            WHERE documents_fts MATCH ?
        """
        params: list[object] = [match_query]
        if source_keys:
            sql += f" AND d.source_key IN ({','.join('?' for _ in source_keys)})"
            params.extend(source_keys)
        if source_types:
            sql += f" AND d.source_type IN ({','.join('?' for _ in source_types)})"
            params.extend(source_types)
        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        # bm25 is lower/better and is frequently negative in sqlite FTS5.
        # Convert rank order to a stable 0..1 reciprocal score.
        return {row["id"]: 1.0 / (1.0 + idx) for idx, row in enumerate(rows)}

    def semantic_search(
        self,
        query: str,
        limit: int = 20,
        source_keys: list[str] | None = None,
        source_types: list[str] | None = None,
    ) -> dict[str, float]:
        query_vec = self._embed([query])[0]
        sql = "SELECT id, embedding FROM documents WHERE embedding IS NOT NULL"
        clauses: list[str] = []
        params: list[object] = []
        if source_keys:
            clauses.append(f"source_key IN ({','.join('?' for _ in source_keys)})")
            params.extend(source_keys)
        if source_types:
            clauses.append(f"source_type IN ({','.join('?' for _ in source_types)})")
            params.extend(source_types)
        if clauses:
            sql += " AND " + " AND ".join(clauses)

        scored: list[tuple[str, float]] = []
        with self.connect() as conn:
            for row in conn.execute(sql, params):
                vec = json.loads(row["embedding"])
                scored.append((row["id"], _cosine(query_vec, vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return dict(scored[:limit])


    def get_topic_documents(
        self,
        *,
        source_urls: list[str] | None = None,
        external_ids: list[str] | None = None,
    ) -> list[KnowledgeDocument]:
        """Return documents that belong explicitly to a topic manifest.

        This is an exact lookup, not semantic retrieval. It is used for the
        user-facing "helpful resources" section so unrelated sources can
        never be added merely because they are semantically similar.
        """
        source_urls = [u for u in (source_urls or []) if u]
        external_ids = [e for e in (external_ids or []) if e]
        if not source_urls and not external_ids:
            return []

        clauses: list[str] = []
        params: list[object] = []
        if source_urls:
            clauses.append(f"source_url IN ({','.join('?' for _ in source_urls)})")
            params.extend(source_urls)
        if external_ids:
            clauses.append(f"external_id IN ({','.join('?' for _ in external_ids)})")
            params.extend(external_ids)

        sql = "SELECT * FROM documents WHERE " + " OR ".join(clauses)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        docs: list[KnowledgeDocument] = []
        for row in rows:
            docs.append(
                KnowledgeDocument(
                    id=row["id"],
                    source_key=row["source_key"],
                    source_name=row["source_name"],
                    source_url=row["source_url"],
                    source_type=row["source_type"],
                    title=row["title"],
                    text=row["text"],
                    language=row["language"],
                    authority_level=row["authority_level"],
                    topic_tags=json.loads(row["topic_tags"]),
                    citation_label=row["citation_label"],
                    external_id=row["external_id"],
                    metadata=json.loads(row["metadata"]),
                )
            )
        return docs

    def get_many(self, ids: list[str]) -> dict[str, KnowledgeDocument]:
        if not ids:
            return {}
        placeholders = ",".join("?" for _ in ids)
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM documents WHERE id IN ({placeholders})",
                ids,
            ).fetchall()
        result: dict[str, KnowledgeDocument] = {}
        for row in rows:
            result[row["id"]] = KnowledgeDocument(
                id=row["id"],
                source_key=row["source_key"],
                source_name=row["source_name"],
                source_url=row["source_url"],
                source_type=row["source_type"],
                title=row["title"],
                text=row["text"],
                language=row["language"],
                authority_level=row["authority_level"],
                topic_tags=json.loads(row["topic_tags"]),
                citation_label=row["citation_label"],
                external_id=row["external_id"],
                metadata=json.loads(row["metadata"]),
            )
        return result
