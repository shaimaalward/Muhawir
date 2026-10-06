from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from .models import SourceRecord, SourceType


class SourceRegistry:
    def __init__(self, path: str | Path | None = None):
        path = Path(path or Path(__file__).parent / "data" / "sources.json")
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self.sources = {item["key"]: SourceRecord(**item) for item in raw}

    def get(self, key: str) -> SourceRecord:
        return self.sources[key]

    def allowed_for(self, domain: SourceType | None) -> list[SourceRecord]:
        values = [s for s in self.sources.values() if s.approved]
        if domain is None:
            return sorted(values, key=lambda s: s.priority)
        if domain == "general":
            values = [s for s in values if "general" in s.content_types]
        else:
            values = [s for s in values if domain in s.content_types]
        return sorted(values, key=lambda s: s.priority)

    def is_url_approved(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        for source in self.sources.values():
            if not source.approved:
                continue
            for domain in source.domains:
                d = domain.lower().lstrip(".")
                if host == d or host.endswith("." + d):
                    return True
        return False

    def source_for_url(self, url: str) -> SourceRecord | None:
        """Resolve a URL to the most specific approved source record.

        Several approved Dorar products share the same hostname, so hostname-only
        matching is insufficient. We prefer the record whose base_url path is the
        longest prefix of the requested path (e.g. /aqeeda over /).
        """
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        request_path = (parsed.path or "/").rstrip("/") or "/"
        matches: list[tuple[int, int, SourceRecord]] = []
        for source in self.sources.values():
            if not source.approved:
                continue
            domain_match = False
            for domain in source.domains:
                d = domain.lower().lstrip(".")
                if host == d or host.endswith("." + d):
                    domain_match = True
                    break
            if not domain_match:
                continue

            base = urlparse(source.base_url)
            base_path = (base.path or "/").rstrip("/") or "/"
            path_score = len(base_path) if (base_path == "/" or request_path == base_path or request_path.startswith(base_path + "/")) else -1
            if path_score >= 0:
                matches.append((path_score, -source.priority, source))

        if not matches:
            return None
        matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return matches[0][2]
