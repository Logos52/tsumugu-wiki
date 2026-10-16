#!/usr/bin/env python3
"""One-shot: flat *-{summary,vocab}.md → sources/videos/{slug}/ bundles.

Restores **例句 / example:** markdown (strips stamped HTML), rewrites links per
ARCHITECTURE.md D1, normalizes frontmatter `source:` to slug.
"""
from __future__ import annotations

import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate_video_pages import READINGS, source_index, sources_moc, videos_moc

ROOT = Path(__file__).resolve().parent.parent
ZH = ROOT / "content" / "zh-Hant"
VIDEOS = ZH / "sources" / "videos"
MANIFEST = ZH / "audio" / "vocab" / "manifest.json"

VOCAB_SENT = re.compile(
    r'<div class="vocab-sent">.*?</div>\s*',
    re.S,
)
VOCAB_TAIL = re.compile(
    r'<div class="vocab-wavebox">.*?</div>\s*</div>\s*',
    re.S,
)
VOCAB_ORPHAN = re.compile(r"</div>\s*(?=\n## )", re.M)
OLD_LINK = re.compile(
    r"\[\[(?P<slug>[a-z0-9-]+)-(summary|vocab)(?:\|(?P<alias>[^\]]+))?\]\]"
)
SOURCE_URL = re.compile(r"^source:\s*https?://[^\n]+\n", re.M)



def unstamp(text: str) -> str:
    """Drop stamped HTML; keep existing **例句 / example:** markdown lines."""
    text = VOCAB_SENT.sub("", text)
    text = VOCAB_TAIL.sub("", text)
    text = VOCAB_ORPHAN.sub("", text)
    return text


def path_link(slug: str, role: str, alias: str | None = None) -> str:
    base = f"zh-Hant/sources/videos/{slug}/{role}"
    return f"[[{base}|{alias}]]" if alias else f"[[{base}]]"


def rewrite_links(text: str, slug: str) -> str:
    def repl(m: re.Match) -> str:
        other = m.group("slug")
        role = m.group(2)
        alias = m.group("alias")
        return path_link(other, role, alias)
    return OLD_LINK.sub(repl, text)


def normalize_source_fm(text: str, slug: str) -> str:
    if SOURCE_URL.search(text):
        return SOURCE_URL.sub(f"source: {slug}\n", text, count=1)
    return text




def fix_ios27_url() -> None:
    """Read real URL from existing summary frontmatter if placeholder."""
    sm = ZH / "ios27-epic-update-summary.md"
    if not sm.exists():
        sm = VIDEOS / "ios27-epic-update" / "summary.md"
    if sm.exists():
        m = re.search(r"source:\s*(https?://[^\n]+)", sm.read_text(encoding="utf-8"))
        if m:
            for r in READINGS:
                if r["slug"] == "ios27-epic-update":
                    r["source_url"] = m.group(1).strip()


def main() -> None:
    fix_ios27_url()
    (ZH / "sources").mkdir(parents=True, exist_ok=True)
    VIDEOS.mkdir(parents=True, exist_ok=True)
    (ZH / "sources" / "index.md").write_text(sources_moc(), encoding="utf-8")
    (VIDEOS / "index.md").write_text(videos_moc(), encoding="utf-8")

    for meta in READINGS:
        slug = meta["slug"]
        bundle = VIDEOS / slug
        bundle.mkdir(parents=True, exist_ok=True)

        for role in ("summary", "vocab"):
            flat = ZH / f"{slug}-{role}.md"
            dest = bundle / f"{role}.md"
            if flat.exists():
                text = flat.read_text(encoding="utf-8")
            elif dest.exists():
                text = dest.read_text(encoding="utf-8")
            else:
                emit(f"SKIP missing {slug}-{role}")
                continue
            text = unstamp(text)
            text = rewrite_links(text, slug)
            text = normalize_source_fm(text, slug)
            dest.write_text(text, encoding="utf-8")
            if flat.exists() and flat != dest:
                flat.unlink()
                emit(f"mv {flat.name} → {dest.relative_to(ROOT)}")

        idx = bundle / "index.md"
        if not idx.exists() or "--" not in idx.read_text(encoding="utf-8")[:200]:
            idx.write_text(source_index(meta), encoding="utf-8")
            emit(f"wrote {idx.relative_to(ROOT)}")

    emit("done — video bundles under content/zh-Hant/sources/videos/")


if __name__ == "__main__":
    main()

def emit(text: str) -> None:
    import sys
    sys.stdout.write(f"{text}\n")

import zlib
