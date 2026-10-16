"""Shared paths and vocab-page reads for the wiki audio scripts."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CONTENT = HERE / "content" / "zh-Hant"
VIDEO_VOCAB = CONTENT / "sources" / "videos"
AUDIO_ROOT = CONTENT / "audio" / "vocab"
MANIFEST = AUDIO_ROOT / "manifest.json"
TTS_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"
ASR_MODEL = "mlx-community/whisper-large-v3-turbo"
ASR_HINT = "以下是繁體中文的句子："
OK = 0.80
ACCEPT = 0.88
REPLACE_MARGIN = 0.06
TEMPS = [0.7, 0.6, 0.75, 0.55, 0.8, 0.65]

EX_LINE = re.compile(r"^\*\*例句 / example:\*\*\s*(.+?)\s*$", re.M)
BOLD = re.compile(r"\*\*([^*]+)\*\*")


def emit(text: str) -> None:
    sys.stdout.write(f"{text}\n")

def tsumugu_repo() -> Path:
    env = os.environ.get("TSUMUGU_REPO")
    if env:
        return Path(env)
    sib = HERE.parent / "tsumugu"
    return sib if sib.exists() else Path("/Users/n1/Projects/tsumugu")

def slug_from_file(path: Path) -> str:
    if path.name == "vocab.md" and path.parent.parent.name == "videos":
        return path.parent.name
    name = path.stem
    return name[:-6] if name.endswith("-vocab") else name


def say_text(raw: str) -> str:
    t = BOLD.sub(r"\1", raw)
    return re.sub(r"\s+", " ", t).strip()


def display_html(raw: str) -> str:
    """Keep **bold** as <strong> for headword emphasis."""
    out, i = [], 0
    for m in BOLD.finditer(raw):
        out.append(raw[i:m.start()])
        out.append(f"<strong>{m.group(1)}</strong>")
        i = m.end()
    out.append(raw[i:])
    return "".join(out).strip()


def vocab_files(slug: str | None = None) -> list[Path]:
    files = sorted(VIDEO_VOCAB.glob("*/vocab.md"))
    files += sorted(CONTENT.glob("*-vocab.md"))
    if slug:
        files = [f for f in files if slug_from_file(f) == slug]
    return files


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"schema": "tsumugu/wiki-vocab-audio@1", "voice": "Serena", "readings": {}}


def save_manifest(m: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def collect_entries(slug_filter: str | None = None) -> list[dict]:
    entries = []
    m = load_manifest()
    readings = m.get("readings", {})
    for vf in vocab_files(slug_filter):
        slug = slug_from_file(vf)
        text = vf.read_text(encoding="utf-8")
        raw_examples = EX_LINE.findall(text)
        if raw_examples:
            for i, raw in enumerate(raw_examples):
                say = say_text(raw)
                clip = f"ex-{i:02d}.mp3"
                rel = f"audio/vocab/{slug}/{clip}"
                entries.append({
                    "slug": slug, "index": i, "say": say, "display": raw.strip(),
                    "clip": clip, "rel": rel,
                    "mp3": AUDIO_ROOT / slug / clip,
                    "vocab_md": vf,
                })
        elif slug in readings:
            for clip, meta in sorted(readings[slug].items()):
                say = meta.get("say") or ""
                idx = int(clip.replace("ex-", "").replace(".mp3", ""))
                rel = f"audio/vocab/{slug}/{clip}"
                entries.append({
                    "slug": slug, "index": idx, "say": say, "display": say,
                    "clip": clip, "rel": rel,
                    "mp3": AUDIO_ROOT / slug / clip,
                    "vocab_md": vf,
                })
    return entries
