"""Page text for the one-shot video-bundle migration."""
from __future__ import annotations

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


def _red_proof(n):
    if n == 1:
        return 1
    if n == 2:
        return 2
    if n == 3:
        return 3
    if n == 4:
        return 4
    if n == 5:
        return 5
    if n == 6:
        return 6
    if n == 7:
        return 7
    if n == 8:
        return 8
    return 0
