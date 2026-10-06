from __future__ import annotations

from typing import Any
import requests

from knowledge.models import KnowledgeDocument
from .base import stable_id


class QuranpediaConnector:
    """Fetches Quran text from Quranpedia's official JSON API.

    This connector intentionally retrieves only the ayahs requested by a topic
    manifest. It does not mirror Quranpedia's corpus.
    """

    API_BASE = "https://api.quranpedia.net/v1"

    def __init__(self, timeout: int = 30, user_agent: str = "Muhawir/1.0 (knowledge ingestion)"):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept": "application/json"})

    def _get_json(self, path: str) -> Any:
        url = f"{self.API_BASE}{path}"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _extract_ayah_text(self, payload: Any, ayah: int) -> str:
        """Tolerates the documented API shape and small schema changes."""
        candidates: list[Any] = []
        if isinstance(payload, list):
            candidates = payload
        elif isinstance(payload, dict):
            for key in ("ayahs", "data", "items", "results"):
                if isinstance(payload.get(key), list):
                    candidates = payload[key]
                    break
            if not candidates:
                candidates = [payload]

        for item in candidates:
            if not isinstance(item, dict):
                continue
            number = item.get("ayah_number") or item.get("ayah") or item.get("aya") or item.get("number")
            if number is not None and int(number) != int(ayah):
                continue
            for key in ("text", "ayah_text", "content", "uthmani", "text_uthmani", "aya_text"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            # Sometimes text is nested.
            for nested_key in ("ayah", "verse"):
                nested = item.get(nested_key)
                if isinstance(nested, dict):
                    for key in ("text", "ayah_text", "content", "uthmani"):
                        value = nested.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()

        raise ValueError(f"Could not extract Quran text for ayah {ayah} from Quranpedia response.")

    def fetch_ayah(self, surah: int, ayah: int, topics: list[str] | None = None) -> KnowledgeDocument:
        # Documented endpoint: /mushafs/1/{surah}/{ayah}. Mushaf 1 = Hafs.
        # Fetching a single ayah avoids unnecessary API traffic.
        payload = self._get_json(f"/mushafs/1/{surah}/{ayah}")
        text = self._extract_ayah_text(payload, ayah)
        public_url = f"https://quranpedia.net/surah/1/{surah}?ayah_id={ayah}"
        return KnowledgeDocument(
            id=f"quranpedia:{surah}:{ayah}",
            source_key="quranpedia",
            source_name="الموسوعة القرآنية",
            source_url=public_url,
            source_type="quran",
            title=f"القرآن الكريم — سورة {surah}، الآية {ayah}",
            text=text,
            language="ar",
            authority_level=1,
            topic_tags=topics or [],
            citation_label=f"القرآن الكريم {surah}:{ayah}",
            external_id=f"{surah}:{ayah}",
            metadata={"surah": surah, "ayah": ayah, "mushaf_id": 1, "provider": "Quranpedia"},
        )
