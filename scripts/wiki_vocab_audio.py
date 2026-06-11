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
import difflib
import hashlib
import json
import os
import re
import subprocess
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


def tsumugu_repo() -> Path:
    env = os.environ.get("TSUMUGU_REPO")
    if env:
        return Path(env)
    sib = HERE.parent / "tsumugu"
    return sib if sib.exists() else Path("/Users/n1/Projects/tsumugu")


def ensure_runtime() -> None:
    try:
        import mlx_whisper  # noqa: F401
        return
    except Exception:
        pass
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


def _normalizer():
    try:
        import opencc
        conv = opencc.OpenCC("t2s").convert
    except Exception:
        conv = lambda s: s  # noqa: E731
    return lambda s: re.sub(r"[^一-鿿]", "", conv(s or ""))


def score(expect: str, heard: str, norm) -> float:
    return difflib.SequenceMatcher(None, norm(expect), norm(heard)).ratio()


def synth_batch(items: list[dict], temperature: float, tmp: Path) -> dict[int, dict]:
    worker = tsumugu_repo() / "scripts/gen/voice/synthesize_qwen3_mlx.py"
    if not worker.exists():
        sys.exit(f"TTS worker not found: {worker}")
    job = {"model": TTS_MODEL, "voice": "Serena", "language": "Chinese",
           "temperature": temperature, "items": items}
    jf = tmp / "job.json"
    jf.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
    out = subprocess.run([sys.executable, str(worker), "--job", str(jf)],
                         capture_output=True, text=True)
    m = re.search(r"<<<VOICE_NOTES_REPORT>>>\s*(\{.*\})\s*<<<END_VOICE_NOTES_REPORT>>>",
                  out.stdout, re.S)
    if not m:
        sys.stderr.write((out.stderr or "")[-2000:] + "\n")
        sys.exit("TTS worker produced no report.")
    return {it["index"]: it for it in json.loads(m.group(1))["items"]}


def wav_to_mp3(wav: Path, mp3: Path) -> None:
    mp3.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                    "-ac", "1", "-b:a", "96k", str(mp3)], check=True)


def cmd_render(args) -> None:
    ensure_runtime()
    entries = collect_entries(args.slug)
    pending = [e for e in entries if not e["mp3"].exists()]
    if not pending:
        print(f"render: all {len(entries)} clips exist")
        return
    print(f"render: synthesizing {len(pending)} missing clip(s)…")
    tmp = Path("/tmp/wiki_vocab_tts")
    tmp.mkdir(exist_ok=True)
    batch = [{"index": i, "text": e["say"], "instruct": None,
              "outWav": str(tmp / f"{e['slug']}-{e['index']}.wav")}
             for i, e in enumerate(pending)]
    rep = synth_batch(batch, 0.7, tmp)
    m = load_manifest()
    readings = m.setdefault("readings", {})
    for i, e in enumerate(pending):
        it = rep.get(i, {})
        if not it.get("ok"):
            print(f"  FAIL {e['slug']}/{e['clip']}: {it.get('error')}")
            continue
        wav_to_mp3(Path(it["outWav"]), e["mp3"])
        readings.setdefault(e["slug"], {})[e["clip"]] = {
            "say": e["say"], "verified": False, "ratio": None,
        }
        print(f"  ✓ {e['slug']}/{e['clip']}")
    save_manifest(m)


def cmd_audit(args) -> None:
    ensure_runtime()
    import mlx_whisper
    norm = _normalizer()

    def hear(f: Path) -> str:
        r = mlx_whisper.transcribe(str(f), path_or_hf_repo=ASR_MODEL,
                                   language="zh", initial_prompt=ASR_HINT, temperature=0.0)
        return r["text"].strip()

    entries = collect_entries(args.slug)
    m = load_manifest()
    readings = m.setdefault("readings", {})
    flagged = []
    rows = []
    for e in entries:
        if not e["mp3"].exists():
            flagged.append(e)
            rows.append((0.0, e, "<MISSING>"))
            continue
        heard = hear(e["mp3"])
        r = score(e["say"], heard, norm)
        rows.append((r, e, heard))
        rec = readings.setdefault(e["slug"], {}).setdefault(e["clip"], {"say": e["say"]})
        rec["ratio"] = round(r, 3)
        rec["verified"] = r >= OK
        if r < OK:
            flagged.append(e)
    save_manifest(m)
    rows.sort(key=lambda x: x[0])
    if not args.json:
        print(f"{'ratio':>6}  {'clip':<40} status")
    for r, e, heard in rows:
        status = "OK" if r >= OK else "BAD"
        if not args.json:
            print(f"{r:6.2f}  {e['slug']}/{e['clip']:<28} [{status}] {e['say']}")
            if r < 0.95:
                print(f"{'':>6}  {'':40} heard: {heard}")
    report = AUDIO_ROOT / "_qa_report.json"
    report.write_text(json.dumps({"flagged": [f"{e['slug']}/{e['clip']}" for e in flagged]},
                                 ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps({"flagged": [f"{e['slug']}/{e['clip']}" for e in flagged]}))
    else:
        print(f"\nFLAGGED: {len(flagged)} — run `fix` to regenerate")
        print(f"report: {report}")


def cmd_fix(args) -> None:
    ensure_runtime()
    import mlx_whisper
    norm = _normalizer()
    entries = {f"{e['slug']}/{e['clip']}": e for e in collect_entries(args.slug)}

    if args.clips:
        fix_keys = args.clips
    else:
        report = AUDIO_ROOT / "_qa_report.json"
        if not report.exists():
            sys.exit("No _qa_report.json — run audit first")
        fix_keys = json.loads(report.read_text())["flagged"]

    fix = [entries[k] for k in fix_keys if k in entries]
    if not fix:
        print("Nothing to fix.")
        return

    def hear(f: Path) -> str:
        r = mlx_whisper.transcribe(str(f), path_or_hf_repo=ASR_MODEL,
                                   language="zh", initial_prompt=ASR_HINT, temperature=0.0)
        return r["text"].strip()

    tmp = Path("/tmp/wiki_vocab_fix")
    tmp.mkdir(exist_ok=True)
    best = {}
    for e in fix:
        r0 = score(e["say"], hear(e["mp3"]), norm) if e["mp3"].exists() else 0.0
        best[f"{e['slug']}/{e['clip']}"] = {"ratio": r0, "orig": r0, "wav": None, "e": e}
        print(f"baseline {e['slug']}/{e['clip']}: {r0:.2f}")

    for rnd, temp in enumerate(TEMPS):
        pending = [k for k, b in best.items() if b["ratio"] < ACCEPT]
        if not pending:
            break
        print(f"\n-- round {rnd} (temp={temp}) — {len(pending)} pending --")
        idx = {i: k for i, k in enumerate(pending)}
        items = [{"index": i, "text": best[k]["e"]["say"], "instruct": None,
                  "outWav": str(tmp / f"r{rnd}-{i}.wav")} for i, k in idx.items()]
        rep = synth_batch(items, temp, tmp)
        for i, k in idx.items():
            it = rep.get(i, {})
            if not it.get("ok"):
                print(f"   {k}: gen failed: {it.get('error')}")
                continue
            r = score(best[k]["e"]["say"], hear(Path(it["outWav"])), norm)
            print(f"   {'✓' if r >= ACCEPT else ' '} {k}: {r:.2f}")
            if r > best[k]["ratio"]:
                best[k].update(ratio=r, wav=it["outWav"])

    m = load_manifest()
    readings = m.setdefault("readings", {})
    changed = []
    for k, b in best.items():
        e = b["e"]
        take = b["wav"] and (
            b["ratio"] >= ACCEPT
            or b["ratio"] >= b["orig"] + REPLACE_MARGIN
            or (b["ratio"] >= OK and b["ratio"] > b["orig"])
        )
        if take:
            wav_to_mp3(Path(b["wav"]), e["mp3"])
            rec = readings.setdefault(e["slug"], {}).setdefault(e["clip"], {"say": e["say"]})
            rec["ratio"] = round(b["ratio"], 3)
            rec["verified"] = b["ratio"] >= OK
            changed.append(k)
            print(f"  REPLACED {k}: {b['orig']:.2f} -> {b['ratio']:.2f}")
        else:
            print(f"  kept     {k}: {b['orig']:.2f} (best {b['ratio']:.2f})")
    save_manifest(m)
    print(f"changed: {len(changed)}")


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
        print(f"stamp: {vf.relative_to(HERE)} — {ok}/{len(entries)} clips (build-time VocabVoice)")


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


if __name__ == "__main__":
    main()