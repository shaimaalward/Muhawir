from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from knowledge.models import KnowledgeDocument, SourceType
from knowledge.registry import SourceRegistry
from .base import chunk_text, normalize_space, stable_id


ARABIC_DIACRITICS_RE = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


def canonical_arabic(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("ـ", "")
    text = ARABIC_DIACRITICS_RE.sub("", text)
    return normalize_space(text).casefold()


class ApprovedWebPageConnector:
    """Fetch reviewed pages from approved sources.

    Important behavior:
    - This connector does NOT crawl a site. It only fetches URLs listed in a
      reviewed topic manifest.
    - It removes page chrome/navigation aggressively before chunking.
    - It applies block-level and chunk-level quality filters so editor names,
      login text, navigation sections, reviewer metadata, and similar noise do
      not become RAG evidence.
    - The raw page URL and source metadata are preserved for traceability.
    """

    DROP_SELECTORS = [
        "script", "style", "noscript", "svg", "form", "button", "nav",
        "footer", "header", "aside", "iframe", "dialog", "template",
        ".navbar", ".nav", ".footer", ".header", ".sidebar",
        ".breadcrumb", ".breadcrumbs", ".share", ".social",
        ".advertisement", ".advertisements", ".ads", ".cookie",
        ".login", ".register", ".account", ".auth", ".menu",
        ".comments", ".related", ".related-posts", ".related-content",
        ".newsletter", ".subscribe", ".pagination", ".pager",
        ".authors", ".author", ".reviewers", ".reviewer",
        ".team", ".contributors", ".contributor",
        "[role='navigation']", "[role='banner']", "[role='contentinfo']",
        "[aria-label*='breadcrumb']", "[class*='breadcrumb']",
        "[class*='social']", "[class*='share']", "[class*='cookie']",
    ]

    # More specific selectors are placed before generic ones. This reduces the
    # chance of choosing a broad wrapper that also contains menus/metadata.
    PREFERRED_SELECTORS = [
        "article .article-content",
        "article .entry-content",
        "article .post-content",
        ".article-content",
        ".entry-content",
        ".post-content",
        ".article-body",
        ".post-body",
        "article",
        "main",
        "[role='main']",
        ".main-content",
        "#content",
        ".content",
    ]

    NOISE_PHRASES = [
        "تسجيل الدخول", "إنشاء حساب جديد", "ليس لديك حساب", "لديك حساب",
        "نسيت كلمة المرور", "أو يمكنك التسجيل", "المشرف العام",
        "نائب المشرف العام", "روابط مهمة", "محتويات الصفحة",
        "الرابط المختصر", "سياسة الخصوصية", "جميع الحقوق محفوظة",
        "تواصل معنا", "اشترك معنا", "عن الموسوعة", "منهج العمل في الموسوعة",
        "المراجع المعتمدة", "اعتماد منهجية الموسوعة", "شارك المادة",
        "نسخ الرابط", "طباعة", "تحميل", "إبلاغ عن خطأ", "أضف تعليق",
        "البحث في الموقع", "القائمة الرئيسية", "الرئيسية", "فهرس المحتويات",
        "المزيد من", "مواد ذات صلة", "مواضيع ذات صلة",
        "تم تحكيم موسوعة", "تم تحكيم الموسوعة", "فريق العمل",
        "المشرف العلمي", "المشرف على", "هيئة التحرير", "لجنة الإشراف",
    ]

    # These phrases are especially characteristic of credential/reviewer blocks
    # that were appearing in Dorar chunks.
    CREDENTIAL_PHRASES = [
        "الأستاذ بجامعة", "أستاذ بجامعة", "الأستاذ في جامعة", "أستاذ في جامعة",
        "قاضي بمحكمة", "قاضي في محكمة", "باحث في التاريخ", "باحث في",
        "مشرف تربوي", "أستاذ التاريخ الإسلامي", "الدكتور", "الشيخ الدكتور",
        "تم تحكيم", "جامعة أم القرى", "جامعة الملك خالد",
        "جامعة الإمام عبدالرحمن", "معهد البحوث والاستشارات",
    ]

    DEFAULT_STOP_MARKERS = [
        "انظر أيضا", "انظر أيضًا", "مواضيع ذات صلة", "مواد ذات صلة",
        "التعليقات", "المراجع", "المصادر والمراجع", "فهرس المحتويات",
        "شارك المادة", "روابط مهمة",
    ]

    def __init__(
        self,
        registry: SourceRegistry,
        timeout: int = 30,
        user_agent: str = "Muhawir/1.0 (knowledge ingestion)",
    ):
        self.registry = registry
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept-Language": "ar,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml",
        })

    def fetch(
        self,
        url: str,
        source_type: SourceType,
        topics: list[str] | None = None,
        title_override: str | None = None,
        min_chars: int = 120,
        max_chunk_chars: int = 1500,
        start_marker: str | None = None,
        stop_markers: list[str] | None = None,
    ) -> list[KnowledgeDocument]:
        source = self.registry.source_for_url(url)
        if source is None or not source.approved:
            raise ValueError(f"URL is not from an approved source: {url}")
        if source_type not in source.content_types and "general" not in source.content_types:
            raise ValueError(
                f"Source {source.key} is not approved for content type '{source_type}'."
            )

        r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or r.encoding
        final_url = r.url

        final_source = self.registry.source_for_url(final_url)
        if final_source is None or final_source.key != source.key:
            raise ValueError(f"Redirect left the approved source product: {final_url}")

        soup = BeautifulSoup(r.text, "html.parser")
        self._remove_noise_nodes(soup)

        title = title_override or self._title(soup, final_url)
        root = self._choose_root(soup, min_chars=min_chars)

        blocks = self._extract_blocks(root)

        # An explicit marker in the manifest is preferred. Otherwise use the
        # page title as an approximate article-start marker.
        marker = start_marker or title
        blocks = self._crop_blocks(
            blocks,
            marker,
            stop_markers or self.DEFAULT_STOP_MARKERS,
        )

        # Final de-noising pass after crop, because some sites put reviewer
        # metadata inside the same content wrapper as the article itself.
        blocks = [self._clean_block_text(x) for x in blocks]
        blocks = [x for x in blocks if x and not self._is_noise(x)]
        text = "\n\n".join(blocks)

        if len(text) < min_chars:
            raise ValueError(
                f"Extracted text is too short ({len(text)} chars) from {final_url}"
            )

        documents: list[KnowledgeDocument] = []
        clean_chunks = []
        for chunk in chunk_text(text, max_chars=max_chunk_chars):
            chunk_text_value = self._clean_chunk_text(chunk.text)
            if not chunk_text_value:
                continue
            if self._is_low_quality_chunk(chunk_text_value):
                continue
            clean_chunks.append((chunk.index, chunk_text_value))

        if not clean_chunks:
            raise ValueError(f"No clean evidence chunks remained after filtering: {final_url}")

        for output_index, (_, clean_text) in enumerate(clean_chunks):
            doc_id = f"{source.key}:{stable_id(final_url, source_type, str(output_index), clean_text)}"
            documents.append(KnowledgeDocument(
                id=doc_id,
                source_key=source.key,
                source_name=source.name_ar,
                source_url=final_url,
                source_type=source_type,
                title=title if output_index == 0 else f"{title} — جزء {output_index + 1}",
                text=clean_text,
                language="ar",
                authority_level=source.priority,
                topic_tags=topics or [],
                citation_label=title,
                external_id=None,
                metadata={
                    "chunk_index": output_index,
                    "page_title": title,
                    "final_url": final_url,
                    "source_key": source.key,
                    "cleaned": True,
                },
            ))

        return documents

    @classmethod
    def _remove_noise_nodes(cls, soup: BeautifulSoup) -> None:
        for selector in cls.DROP_SELECTORS:
            for node in soup.select(selector):
                node.decompose()

        # Remove elements by semantic id/class names too. This catches sites
        # whose CSS class names are not covered by the static selectors above.
        semantic_noise = re.compile(
            r"(nav|menu|footer|header|sidebar|breadcrumb|share|social|cookie|"
            r"login|register|account|comment|related|author|review|team|"
            r"contributor|newsletter|subscribe|advert|promo)",
            re.I,
        )
        # Work on a snapshot of nodes. Decomposing a parent invalidates some
        # descendants in BeautifulSoup (their ``attrs`` becomes None), so every
        # node must be checked before calling ``.get``.
        for node in list(soup.find_all(True)):
            if getattr(node, "attrs", None) is None:
                continue

            node_id = node.attrs.get("id", "") or ""
            node_classes = node.attrs.get("class", []) or []
            if not isinstance(node_classes, (list, tuple)):
                node_classes = [str(node_classes)]

            attrs = " ".join([
                str(node_id),
                " ".join(str(value) for value in node_classes),
            ])
            if attrs and semantic_noise.search(attrs):
                # Do not delete the actual article/main root just because one
                # broad class contains e.g. "content"; only semantic noise terms
                # above are matched.
                node.decompose()

    @classmethod
    def _choose_root(cls, soup: BeautifulSoup, min_chars: int):
        candidates = []
        for selector in cls.PREFERRED_SELECTORS:
            for node in soup.select(selector):
                text = normalize_space(node.get_text(" ", strip=True))
                if len(text) >= min_chars:
                    candidates.append((selector, node, len(text)))
            if candidates:
                # Prefer the first selector family that produced valid nodes,
                # then choose the richest node within that family.
                break

        if candidates:
            candidates.sort(key=lambda x: x[2], reverse=True)
            return candidates[0][1]

        return soup.body or soup

    @staticmethod
    def _title(soup: BeautifulSoup, url: str) -> str:
        h1 = soup.find("h1")
        if h1:
            value = normalize_space(h1.get_text(" ", strip=True))
            if value:
                return value

        if soup.title:
            value = normalize_space(soup.title.get_text(" ", strip=True))
            if value:
                for sep in [
                    " - الدرر السنية",
                    " | الدرر السنية",
                    " - مركز الدعوة",
                    " | مركز الدعوة",
                ]:
                    if sep in value:
                        value = value.split(sep, 1)[0].strip()
                return value

        return urlparse(url).path.rstrip("/").split("/")[-1] or url

    @classmethod
    def _clean_block_text(cls, text: str) -> str:
        text = normalize_space(text)
        if not text:
            return ""

        # Remove obvious UI labels when they are embedded at the beginning/end
        # of otherwise useful text.
        edge_noise = [
            "شارك المادة", "نسخ الرابط", "طباعة", "تحميل", "إبلاغ عن خطأ",
            "تسجيل الدخول", "إنشاء حساب", "الرابط المختصر",
        ]
        for phrase in edge_noise:
            text = re.sub(rf"^(?:{re.escape(phrase)}\s*)+", "", text, flags=re.I)
            text = re.sub(rf"(?:\s*{re.escape(phrase)})+$", "", text, flags=re.I)

        # Remove repeated whitespace/punctuation artifacts.
        text = re.sub(r"\s+([،؛:,.!?؟])", r"\1", text)
        text = re.sub(r"([،؛:,.!?؟])\1{2,}", r"\1", text)
        return normalize_space(text)

    @classmethod
    def _is_noise(cls, text: str) -> bool:
        normalized = normalize_space(text)
        if not normalized:
            return True

        c = canonical_arabic(normalized)
        words = normalized.split()

        # Exact/common UI phrases.
        if any(canonical_arabic(phrase) in c for phrase in cls.NOISE_PHRASES):
            return True

        # Tiny labels/headings are rarely useful as standalone RAG evidence.
        if len(words) <= 3 and len(normalized) < 25:
            return True

        # Reviewer/editor/credential blocks. We intentionally require multiple
        # signals for longer text so a legitimate scholarly quotation mentioning
        # "الدكتور" is not discarded solely because of one word.
        credential_hits = sum(
            canonical_arabic(k) in c for k in cls.CREDENTIAL_PHRASES
        )
        if credential_hits >= 2:
            return True
        if credential_hits >= 1 and len(words) < 80:
            return True

        # Blocks containing many person-title patterns are almost always staff or
        # reviewer lists rather than the religious content itself.
        title_hits = len(re.findall(r"(?:الشيخ|الدكتور|الأستاذ)\s+[\w\u0600-\u06FF]+", normalized))
        if title_hits >= 3:
            return True

        # Navigation-heavy text frequently has lots of short colon-separated or
        # pipe-separated fragments.
        if normalized.count("|") >= 3:
            return True

        return False

    @classmethod
    def _extract_blocks(cls, root) -> list[str]:
        blocks: list[str] = []
        seen: set[str] = set()

        # p/blockquote are preferred evidence. Headings are retained because
        # they help preserve context. List items are included only when they are
        # sufficiently substantive.
        for node in root.find_all([
            "h1", "h2", "h3", "h4", "h5", "h6",
            "p", "blockquote", "li",
        ]):
            text = cls._clean_block_text(node.get_text(" ", strip=True))
            if not text:
                continue

            if node.name == "li" and len(text.split()) < 8:
                continue

            key = canonical_arabic(text)
            if not key or key in seen or cls._is_noise(text):
                continue

            seen.add(key)
            blocks.append(text)

        if blocks:
            return blocks

        fallback = cls._clean_block_text(root.get_text("\n", strip=True))
        return [] if cls._is_noise(fallback) else [fallback]

    @classmethod
    def _crop_blocks(
        cls,
        blocks: list[str],
        start_marker: str | None,
        stop_markers: list[str],
    ) -> list[str]:
        if not blocks:
            return blocks

        start = 0
        if start_marker:
            target = canonical_arabic(start_marker)
            for i, block in enumerate(blocks):
                b = canonical_arabic(block)
                # Exact-ish heading match. Avoid matching a random long body
                # paragraph that happens to mention the page title.
                if target and (
                    b == target
                    or (
                        len(target) >= 18
                        and target in b
                        and len(b) <= len(target) + 80
                    )
                ):
                    start = i
                    break

        cropped = blocks[start:]
        stop_targets = [canonical_arabic(x) for x in stop_markers]

        out: list[str] = []
        for block in cropped:
            b = canonical_arabic(block)
            if any(t and (b == t or b.startswith(t + " ")) for t in stop_targets):
                break
            out.append(block)

        return out

    @classmethod
    def _clean_chunk_text(cls, text: str) -> str:
        # Rebuild a chunk line-by-line so a single staff/reviewer paragraph does
        # not poison an otherwise useful chunk.
        lines = []
        seen = set()
        for raw in re.split(r"\n+", text or ""):
            line = cls._clean_block_text(raw)
            if not line or cls._is_noise(line):
                continue
            key = canonical_arabic(line)
            if key in seen:
                continue
            seen.add(key)
            lines.append(line)

        return normalize_space("\n".join(lines))

    @classmethod
    def _is_low_quality_chunk(cls, text: str) -> bool:
        text = normalize_space(text)
        words = text.split()
        if len(words) < 12:
            return True

        c = canonical_arabic(text)

        # Reject chunks dominated by metadata/credentials.
        credential_hits = sum(
            canonical_arabic(k) in c for k in cls.CREDENTIAL_PHRASES
        )
        noise_hits = sum(
            canonical_arabic(k) in c for k in cls.NOISE_PHRASES
        )
        if credential_hits >= 2 or noise_hits >= 2:
            return True

        # Too many named-title patterns strongly indicates contributor/reviewer
        # lists rather than source content.
        title_hits = len(re.findall(r"(?:الشيخ|الدكتور|الأستاذ)\s+[\w\u0600-\u06FF]+", text))
        if title_hits >= 3:
            return True

        return False
