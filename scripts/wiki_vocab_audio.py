#!/usr/bin/env python3
"""Serena audio + transcribe-back QA for wiki reading vocab pages (例句).

Contract (PRD-Entry-Authoring §6, dict-demo README):
  - Qwen3-TTS voice Serena, batch via synthesize_qwen3_mlx.py
  - whisper transcribe-back; ratio >= 0.80 passes; auto-regen below
  - Markdown gains voiced HTML blocks with 🌊 A/B-loop waveforms

Usage (from anywhere; re-execs into voice venv when needed):
  python3 scripts/wiki_vocab_audio.py render          # synth missing clips
  python3 scripts/wiki_vocab_audio.py audit           # transcribe-back QA
  python3 scripts/wiki_vocab_audio.py fix             # regen flagged clips
  python3 scripts/wiki_vocab_audio.py stamp           # no-op (VocabVoice plugin at build)
  python3 scripts/wiki_vocab_audio.py all             # render → audit → fix
  python3 scripts/wiki_vocab_audio.py all --slug ai-replaced-my-thinking
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from wiki_vocab_audit import run_audit
from wiki_vocab_data import collect_entries, emit, load_manifest, save_manifest, slug_from_file, tsumugu_repo, vocab_files
from wiki_vocab_data import display_html
from wiki_vocab_fix import run_fix
from wiki_vocab_speech import synth_batch, wav_to_mp3


def ensure_runtime() -> None:
    if _imports("mlx_whisper"):
        return
    if os.environ.get("WIKI_VOCAB_REEXEC"):
        sys.exit("Voice venv still cannot import mlx_whisper.")
    repo = tsumugu_repo()
    me = os.path.abspath(sys.executable)
    for c in [os.environ.get("TSUMUGU_VOICE_PYTHON"),
              str(repo / "personal/research/bakeoff/.venv/bin/python"),
              str(repo / "personal/voice/.venv/bin/python")]:
        if c and Path(c).exists() and os.path.abspath(c) != me:
            os.execve(c, [c, str(Path(__file__).resolve()), *sys.argv[1:]],
                      {**os.environ, "WIKI_VOCAB_REEXEC": "1"})


def _normalizer():
    try:
        import opencc
        convert = opencc.OpenCC("t2s").convert
    except ImportError:
        convert = _same_text
    return lambda s: re.sub(r"[^一-鿿]", "", convert(s or ""))


def cmd_render(args) -> None:
    ensure_runtime()
    entries = collect_entries(args.slug)
    pending = [e for e in entries if not e["mp3"].exists()]
    if not pending:
        emit(f"render: all {len(entries)} clips exist")
        return
    emit(f"render: synthesizing {len(pending)} missing clip(s)…")
    tmp = Path("/tmp/wiki_vocab_tts")
    tmp.mkdir(exist_ok=True)
    batch = [{"index": i, "text": e["say"], "instruct": None,
              "outWav": str(tmp / f"{e['slug']}-{e['index']}.wav")}
             for i, e in enumerate(pending)]
    rep = synth_batch(batch, 0.7, tmp)
    _store_rendered(pending, rep)


def _store_rendered(pending, rep) -> None:
    manifest = load_manifest()
    readings = manifest.setdefault("readings", {})
    for i, entry in enumerate(pending):
        item = rep.get(i, {})
        if not item.get("ok"):
            emit(f"  FAIL {entry['slug']}/{entry['clip']}: {item.get('error')}")
            continue
        wav_to_mp3(Path(item["outWav"]), entry["mp3"])
        readings.setdefault(entry["slug"], {})[entry["clip"]] = {
            "say": entry["say"], "verified": False, "ratio": None,
        }
        emit(f"  ✓ {entry['slug']}/{entry['clip']}")
    save_manifest(manifest)


def cmd_audit(args) -> None:
    ensure_runtime()
    import mlx_whisper
    run_audit(args, mlx_whisper, _normalizer())


def cmd_fix(args) -> None:
    ensure_runtime()
    import mlx_whisper
    run_fix(args, mlx_whisper, _normalizer())


def voiced_block(e: dict) -> str:
    rel = e["rel"]
    disp = display_html(e["display"])
    say = e["say"].replace('"', "&quot;")
    return (
        f'<div class="vocab-sent">\n'
        f'<span class="zh-t" data-audio="{rel}" data-say="{say}">{disp}</span>\n'
        f'<div class="vocab-tools">'
        f'<button type="button" class="btn vocab-play" aria-label="Play sentence">▶</button>'
        f'<button type="button" class="btn vocab-swave" aria-label="A/B loop waveform">🌊</button>'
        f'</div>\n'
        f'<div class="vocab-wavebox">'
        f'<div class="wv"></div>'
        f'<div class="vocab-wave-ctrls">'
        f'<button type="button" class="btn vocab-wplay">▶</button>'
        f'<button type="button" class="btn vocab-wloop">🔁</button>'
        f'<button type="button" class="btn vocab-wspeed">1×</button>'
        f'</div>'
        f'<div class="vocab-hint">Drag on the waveform to select a slice, then 🔁 to drill it.</div>'
        f'</div>\n'
        f'</div>'
    )


def cmd_stamp(args) -> None:
    """Audio UI is injected at build time by quartz/plugins/transformers/vocabVoice.ts."""
    for vf in vocab_files(args.slug):
        slug = slug_from_file(vf)
        entries = [e for e in collect_entries(slug) if e["vocab_md"] == vf]
        ok = sum(1 for e in entries if e["mp3"].exists())
        emit(f"stamp: {vf.relative_to(_repo())} — {ok}/{len(entries)} clips (build-time VocabVoice)")


def _repo() -> Path:
    from wiki_vocab_data import HERE
    return HERE


def cmd_all(args) -> None:
    cmd_render(args)
    cmd_audit(argparse.Namespace(slug=args.slug, json=False))
    cmd_fix(argparse.Namespace(slug=args.slug, clips=[]))
    cmd_stamp(argparse.Namespace(slug=args.slug, force=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("render", "stamp", "all"):
        p = sub.add_parser(name)
        p.add_argument("--slug", help="limit to one reading slug")
        if name == "stamp":
            p.add_argument("--force", action="store_true")
        p.set_defaults(func=globals()[f"cmd_{name}"])
    aud = sub.add_parser("audit")
    aud.add_argument("--slug")
    aud.add_argument("--json", action="store_true")
    aud.set_defaults(func=cmd_audit)
    fx = sub.add_parser("fix")
    fx.add_argument("clips", nargs="*", help="slug/ex-NN.mp3 keys")
    fx.add_argument("--slug")
    fx.set_defaults(func=cmd_fix)
    args = ap.parse_args()
    if args.cmd != "stamp":
        ensure_runtime()
    args.func(args)


def _same_text(text: str) -> str:
    return text


def _imports(name: str) -> bool:
    try:
        __import__(name)
    except ImportError:
        return False
    return True


if __name__ == "__main__":
    main()
