from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from .models import RetrievalResult, RetrievedEvidence
from .registry import SourceRegistry
from .store import KnowledgeStore


class HybridRetriever:
    """Hybrid retrieval across the entire approved knowledge base.

    The caller does NOT need to know or specify a domain. Muhawir searches all
    approved sources, then ranks evidence by semantic similarity, lexical match,
    source authority, and source diversity.

    Source/domain metadata is still kept on every document so the evaluator can
    explain where evidence came from, but routing is not exposed to the user and
    is not required for evaluation.
    """

    def __init__(
        self,
        store: KnowledgeStore,
        registry: SourceRegistry,
        semantic_weight: float = 0.68,
        lexical_weight: float = 0.32,
        min_combined_score: float = 0.18,
    ):
        self.store = store
        self.registry = registry
        self.semantic_weight = semantic_weight
        self.lexical_weight = lexical_weight
        self.min_combined_score = min_combined_score

    def retrieve(self, query: str, top_k: int = 8) -> RetrievalResult:
        approved = [s for s in self.registry.sources.values() if s.approved]
        source_keys = [s.key for s in approved]

        candidate_limit = max(30, top_k * 6)
        lexical = self.store.lexical_search(
            query,
            limit=candidate_limit,
            source_keys=source_keys,
            source_types=None,
        )
        semantic = self.store.semantic_search(
            query,
            limit=candidate_limit,
            source_keys=source_keys,
            source_types=None,
        )

        ids = list(set(lexical) | set(semantic))
        docs = self.store.get_many(ids)
        ranked: list[RetrievedEvidence] = []

        for doc_id in ids:
            doc = docs.get(doc_id)
            if not doc:
                continue

            # Priority 1 is strongest. Keep the boost small enough that relevance
            # still dominates ranking.
            authority_boost = max(0.0, (6 - doc.authority_level) * 0.018)
            combined = (
                self.semantic_weight * max(0.0, semantic.get(doc_id, 0.0))
                + self.lexical_weight * lexical.get(doc_id, 0.0)
                + authority_boost
            )
            ranked.append(
                RetrievedEvidence(
                    document_id=doc.id,
                    source_key=doc.source_key,
                    source_name=doc.source_name,
                    source_url=doc.source_url,
                    source_type=doc.source_type,
                    title=doc.title,
                    text=doc.text,
                    citation_label=doc.citation_label,
                    lexical_score=lexical.get(doc_id, 0.0),
                    semantic_score=max(0.0, semantic.get(doc_id, 0.0)),
                    combined_score=combined,
                    authority_level=doc.authority_level,
                    metadata=doc.metadata,
                )
            )

        ranked.sort(key=lambda x: x.combined_score, reverse=True)
        selected = self._diversify(ranked, top_k=top_k)
        sufficient = bool(selected and selected[0].combined_score >= self.min_combined_score)

        return RetrievalResult(
            query=query,
            domain=None,
            evidence=selected,
            evidence_sufficient=sufficient,
            reason=None if sufficient else "No sufficiently relevant approved evidence was retrieved.",
        )


    def retrieve_topic_resources(self, topic_key: str | None, top_k: int = 3) -> list[RetrievedEvidence]:
        """Return resources explicitly assigned to the selected training topic.

        This is deliberately separate from claim verification retrieval.
        Claim verification searches the whole approved KB. The resources shown
        to the trainee at the end of the session must come only from the topic
        manifest selected for that training session.
        """
        if not topic_key or top_k <= 0:
            return []

        manifest_path = Path(__file__).resolve().parent / "topics" / f"{topic_key}.json"
        if not manifest_path.exists():
            # Better to show no resources than unrelated resources.
            return []

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        quran_ids = [
            f"{int(item['surah'])}:{int(item['ayah'])}"
            for item in manifest.get("quran_ayahs", [])
            if "surah" in item and "ayah" in item
        ]
        web_urls = [
            str(item.get("url", "")).strip()
            for item in manifest.get("web_pages", [])
            if str(item.get("url", "")).strip()
        ]

        docs = self.store.get_topic_documents(
            source_urls=web_urls,
            external_ids=quran_ids,
        )
        if not docs:
            return []

        by_external_id = {doc.external_id: doc for doc in docs if doc.external_id}
        by_url: dict[str, list] = defaultdict(list)
        for doc in docs:
            by_url[doc.source_url].append(doc)

        for url_docs in by_url.values():
            url_docs.sort(key=lambda d: int(d.metadata.get("chunk_index", 0)))

        ordered_docs = []

        # Prefer one Qur'anic source first when the topic manifest includes it.
        for external_id in quran_ids[:1]:
            doc = by_external_id.get(external_id)
            if doc:
                ordered_docs.append(doc)

        # Then add one representative chunk from each explicitly listed page.
        for url in web_urls:
            url_docs = by_url.get(url, [])
            if url_docs:
                ordered_docs.append(url_docs[0])

        # Finally add remaining Qur'anic sources if there is still room.
        for external_id in quran_ids[1:]:
            doc = by_external_id.get(external_id)
            if doc:
                ordered_docs.append(doc)

        selected: list[RetrievedEvidence] = []
        seen_urls: set[str] = set()
        seen_ids: set[str] = set()

        for doc in ordered_docs:
            if doc.id in seen_ids or doc.source_url in seen_urls:
                continue
            selected.append(
                RetrievedEvidence(
                    document_id=doc.id,
                    source_key=doc.source_key,
                    source_name=doc.source_name,
                    source_url=doc.source_url,
                    source_type=doc.source_type,
                    title=doc.title,
                    text=doc.text,
                    citation_label=doc.citation_label,
                    lexical_score=1.0,
                    semantic_score=1.0,
                    combined_score=1.0,
                    authority_level=doc.authority_level,
                    metadata=doc.metadata,
                )
            )
            seen_ids.add(doc.id)
            seen_urls.add(doc.source_url)
            if len(selected) >= top_k:
                break

        return selected

    @staticmethod
    def _diversify(ranked: list[RetrievedEvidence], top_k: int) -> list[RetrievedEvidence]:
        """Avoid filling the context with near-duplicate chunks from one page.

        First pass allows at most two chunks per URL and three per source key.
        A second pass fills any remaining slots from the global ranking.
        """
        selected: list[RetrievedEvidence] = []
        seen_ids: set[str] = set()
        per_url: defaultdict[str, int] = defaultdict(int)
        per_source: defaultdict[str, int] = defaultdict(int)

        for item in ranked:
            if len(selected) >= top_k:
                break
            if per_url[item.source_url] >= 2:
                continue
            if per_source[item.source_key] >= 3:
                continue
            selected.append(item)
            seen_ids.add(item.document_id)
            per_url[item.source_url] += 1
            per_source[item.source_key] += 1

        if len(selected) < top_k:
            for item in ranked:
                if len(selected) >= top_k:
                    break
                if item.document_id in seen_ids:
                    continue
                selected.append(item)
                seen_ids.add(item.document_id)

        return selected
