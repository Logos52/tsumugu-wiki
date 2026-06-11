#!/usr/bin/env python3
"""One-shot: flat *-{summary,vocab}.md → sources/videos/{slug}/ bundles.

Restores **例句 / example:** markdown (strips stamped HTML), rewrites links per
ARCHITECTURE.md D1, normalizes frontmatter `source:` to slug.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

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

READINGS = [
    {
        "slug": "why-friendship-differs",
        "channel": "Mandarin Corner",
        "source_url": "https://www.youtube.com/watch?v=2idX7w0gs4k",
        "zh_title": "外國人與中國人的友誼觀",
        "en_title": "Why Chinese and Foreigners View Friendship Differently",
    },
    {
        "slug": "steam-controller-review",
        "channel": "小寧子 XNZ",
        "source_url": "https://www.youtube.com/watch?v=2_FpQj_f69g",
        "zh_title": "Steam 手柄評測",
        "en_title": "Steam Controller review",
    },
    {
        "slug": "life-as-open-world-rpg",
        "channel": "小寧子 XNZ",
        "source_url": "https://www.youtube.com/watch?v=p-iL1LoN2To",
        "zh_title": "把生活變成開放世界 RPG",
        "en_title": "Turning Life Into an Open-World RPG",
    },
    {
        "slug": "2025-top-ten-gadgets",
        "channel": "小寧子 XNZ",
        "source_url": "https://www.youtube.com/watch?v=yz6utkYbq_E",
        "zh_title": "2025 年度十大科技產品",
        "en_title": "Top 10 tech products of 2025",
    },
    {
        "slug": "ios27-epic-update",
        "channel": "小寧子 XNZ",
        "source_url": "https://www.youtube.com/watch?v=E5ShFx9unEQ",
        "zh_title": "iOS 27 上手體驗",
        "en_title": "iOS 27 hands-on",
    },
    {
        "slug": "iphone-18-lineup-preview",
        "channel": "小寧子 XNZ",
        "source_url": "https://www.youtube.com/watch?v=4Lhkx1wnEDE",
        "zh_title": "今年的 iPhone，你需要知道的一切",
        "en_title": "This year's iPhones preview",
    },
    {
        "slug": "ai-replaced-my-thinking",
        "channel": "小寧子 XNZ",
        "source_url": "https://www.youtube.com/watch?v=_EmMwEIqAwo",
        "zh_title": "讓 AI 代替我思考七天",
        "en_title": "I let AI think for me for 7 days",
    },
]


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


def source_index(meta: dict) -> str:
    slug = meta["slug"]
    ch = meta["channel"]
    tag = "mandarin-corner" if ch == "Mandarin Corner" else "xiaoningzi"
    return f"""---
title: "{meta['zh_title']}"
english_title: "{meta['en_title']}"
type: source
lang: zh-Hant
slug: {slug}
source_url: {meta['source_url']}
channel: {ch}
transcript: private
tags: [source, zh-Hant, {tag}, youtube]
---

# {meta['zh_title']}

> YouTube reading bundle — [[zh-Hant/sources/videos/{slug}/summary|摘要]] (95%-CI summary) · [[zh-Hant/sources/videos/{slug}/vocab|深入詞彙]] (vocab encoder). Raw transcript stays private.

- **Channel:** {ch}
- **Source:** [{meta['source_url']}]({meta['source_url']})
"""


def videos_moc() -> str:
    rows = []
    for r in READINGS:
        s = r["slug"]
        rows.append(
            f"| **{r['zh_title']}** | {r['channel']} | "
            f"[[zh-Hant/sources/videos/{s}/summary\\|read]] · "
            f"[[zh-Hant/sources/videos/{s}/vocab\\|encode]] |"
        )
    table = "\n".join(rows)
    return f"""---
title: "Video readings"
type: moc
lang: zh-Hant
tags: [moc, sources, videos]
---

# Video readings

| Reading | Channel | Pages |
|---------|---------|-------|
{table}
"""


def sources_moc() -> str:
    return """---
title: "Sources"
type: moc
lang: zh-Hant
tags: [moc, sources]
---

# Sources

- [[zh-Hant/sources/videos/index|Video readings]] — YouTube transcript / podcast bundles
- [[zh-Hant/gsm1/index|GSM Part 1]] · [[zh-Hant/gsm2/index|GSM Part 2]] — course vocab (pending bundle move)
"""


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
                print(f"SKIP missing {slug}-{role}")
                continue
            text = unstamp(text)
            text = rewrite_links(text, slug)
            text = normalize_source_fm(text, slug)
            dest.write_text(text, encoding="utf-8")
            if flat.exists() and flat != dest:
                flat.unlink()
                print(f"mv {flat.name} → {dest.relative_to(ROOT)}")

        idx = bundle / "index.md"
        if not idx.exists() or "--" not in idx.read_text(encoding="utf-8")[:200]:
            idx.write_text(source_index(meta), encoding="utf-8")
            print(f"wrote {idx.relative_to(ROOT)}")

    print("done — video bundles under content/zh-Hant/sources/videos/")


if __name__ == "__main__":
    main()