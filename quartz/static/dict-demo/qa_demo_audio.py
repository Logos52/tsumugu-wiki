#!/usr/bin/env python3
"""Audio QA + self-healing for the Tsumugu Encoding Dictionary demo.

WHAT THIS IS
------------
The demo's Chinese audio is pre-baked with Qwen3-TTS (voice "Serena"). That model
occasionally hallucinates — a clip comes out garbled, stuttered, or with the wrong
word — even though the file exists and plays. This tool catches those automatically
by *transcribing every clip back* (whisper) and comparing to the intended text, then
re-synthesises the bad ones until they transcribe correctly.

It is the verify/repair half of the demo audio pipeline:

    render_demo_audio.py   generate any missing clips   (creates audio/*.mp3)
    qa_demo_audio.py audit transcribe + score every clip (finds wrong/garbled ones)
    qa_demo_audio.py fix    regenerate the flagged clips until they verify

HOW TO RUN  (agent-agnostic — no editing, no hardcoded paths)
-------------------------------------------------------------
From anywhere, with plain system python3 — the script re-execs itself into the
Tsumugu voice venv automatically if the ML deps aren't importable:

    python3 qa_demo_audio.py audit          # report card for all clips
    python3 qa_demo_audio.py fix            # regenerate everything audit flagged
    python3 qa_demo_audio.py fix she-ex-2 gao-ex-2   # or name specific clips
    python3 qa_demo_audio.py audit --json   # machine-readable, no model needed for layout

Env overrides (all optional, sensible defaults derived from this file's location):
    TSUMUGU_REPO          path to the tsumugu engine repo (has the TTS worker)
    TSUMUGU_VOICE_PYTHON  python that can import mlx_audio / mlx_whisper / opencc

WHAT COUNTS AS "BAD"
--------------------
Each clip's intended text is read from the demo HTML (the data-say next to its
data-audio). Both intended and heard text are normalised (OpenCC -> Simplified,
CJK chars only) and compared with difflib ratio:
  ratio >= 0.80  -> OK
  ratio <  0.80  -> BAD (regenerate)        [for real sentences]
  <= 2 chars     -> "chr": single glyphs / 2-char headwords are unreliable to
                    transcribe in isolation; reported but never auto-flagged.
Long teacher narrations (字源/釋義/expert) can sit ~0.78-0.85 purely from rare-char
ASR noise (彳 辵 金文 …) on perfectly good audio — `fix` keeps a regen only if it
actually beats the original, so good audio is never churned.

DEPENDENCIES (all already present in the Tsumugu voice venv)
    mlx_whisper, mlx_audio, opencc, soundfile, numpy ; ffmpeg on PATH.
    Models (cached on first use): whisper-large-v3-turbo (~1.5GB),
    Qwen3-TTS-12Hz-1.7B-CustomVoice (~3.5GB).
"""
from __future__ import annotations
import argparse, difflib, json, os, re, subprocess, sys, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../tsumugu-wiki/quartz/static/dict-demo
AUDIO = HERE / "audio"
TTS_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"
ASR_MODEL = "mlx-community/whisper-large-v3-turbo"
ASR_HINT = "以下是繁體中文的句子："      # nudges whisper toward Traditional, fewer homophone slips
OK = 0.80                                 # >= this transcribes "correctly enough"
ACCEPT = 0.88                             # a regen this good is taken immediately
REPLACE_MARGIN = 0.06                     # else only overwrite if it beats the original by this
TEMPS = [0.7, 0.6, 0.75, 0.55, 0.8, 0.65]  # regen rounds; lower temp = fewer hallucinations
REPORT = HERE / "_qa_report.json"


def tsumugu_repo() -> Path:
    env = os.environ.get("TSUMUGU_REPO")
    if env and Path(env).exists():
        return Path(env)
    # demo lives at <repo-parent>/tsumugu-wiki/quartz/static/dict-demo; engine is a sibling
    sibling = HERE.parents[3] / "tsumugu"
    if (sibling / "scripts/gen/voice/synthesize_qwen3_mlx.py").exists():
        return sibling
    return sibling  # best guess; callers that need the worker will error clearly


def ensure_runtime() -> None:
    """Re-exec into the voice venv if the ML deps aren't importable here.

    Compares literal (un-resolved) paths: a venv's bin/python is usually a symlink
    to the base interpreter, so realpath() would wrongly equate them and refuse to
    switch. A QA_DEMO_REEXEC sentinel guards against an exec loop if the chosen
    venv still can't import the deps.
    """
    try:
        import mlx_whisper  # noqa: F401
        return
    except Exception:
        pass
    if os.environ.get("QA_DEMO_REEXEC"):
        sys.exit("Re-exec'd into a voice venv but it still cannot `import mlx_whisper`. "
                 "Fix the venv or point TSUMUGU_VOICE_PYTHON at a working one.")
    repo = tsumugu_repo()
    me = os.path.abspath(sys.executable)
    cands = [os.environ.get("TSUMUGU_VOICE_PYTHON"),
             str(repo / "personal/research/bakeoff/.venv/bin/python"),
             str(repo / "personal/voice/.venv/bin/python")]
    for c in cands:
        if c and Path(c).exists() and os.path.abspath(c) != me:
            os.execve(c, [c, str(Path(__file__).resolve()), *sys.argv[1:]],
                      {**os.environ, "QA_DEMO_REEXEC": "1"})
    sys.exit("No voice venv with mlx_whisper found. Set TSUMUGU_VOICE_PYTHON to a python "
             "that can `import mlx_whisper` (see render_demo_audio.py for venv discovery).")


# ---- clip -> intended text, parsed from the demo HTML (no bs4 needed) ----
_TAG = re.compile(r'<[^>]*\bdata-audio="([^"]+)"[^>]*>')

def clip_map() -> dict[str, str]:
    m: dict[str, str] = {}
    for html in sorted(HERE.glob("*.html")):
        text = html.read_text(encoding="utf-8")
        for tag in _TAG.finditer(text):
            src = tag.group(1)
            if not src.startswith("audio/"):
                continue
            say = re.search(r'data-say="([^"]*)"', tag.group(0))
            if say and say.group(1).strip():
                m[src.split("/")[-1]] = say.group(1).strip()
    return m


# ---- scoring ----
def _normalizer():
    try:
        import opencc
        conv = opencc.OpenCC("t2s").convert
    except Exception:
        conv = lambda s: s  # noqa: E731 — opencc absent: looser compare, still useful
        sys.stderr.write("[warn] opencc not importable; comparison is Traditional-sensitive.\n")
    return lambda s: re.sub(r"[^一-鿿]", "", conv(s or ""))

def score(expect: str, heard: str, norm) -> float:
    return difflib.SequenceMatcher(None, norm(expect), norm(heard)).ratio()


# ---- transcription ----
def make_transcriber():
    import mlx_whisper
    def t(path: Path) -> str:
        r = mlx_whisper.transcribe(str(path), path_or_hf_repo=ASR_MODEL,
                                   language="zh", initial_prompt=ASR_HINT, temperature=0.0)
        return r["text"].strip()
    return t


# ---- TTS worker (one subprocess call per round; model loads once per call) ----
def synth(items: list[dict], temperature: float, tmp: Path) -> dict[int, dict]:
    worker = tsumugu_repo() / "scripts/gen/voice/synthesize_qwen3_mlx.py"
    if not worker.exists():
        sys.exit(f"TTS worker not found: {worker} (set TSUMUGU_REPO).")
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


def cmd_audit(args) -> None:
    cm = clip_map()
    only = set(a if a.endswith(".mp3") else a + ".mp3" for a in args.clips)
    if args.json and args.layout_only:
        print(json.dumps(cm, ensure_ascii=False, indent=2)); return
    norm = _normalizer()
    transcribe = make_transcriber()
    rows = []
    for name in sorted(cm):
        if only and name not in only:
            continue
        f = AUDIO / name
        if not f.exists():
            rows.append((0.0, name, cm[name], "<MISSING>")); continue
        heard = transcribe(f)
        rows.append((score(cm[name], heard, norm), name, cm[name], heard))
    rows.sort()
    flagged = []
    if not args.json:
        print(f"{'ratio':>6}  {'clip':<18} status / intended")
    for r, name, expect, heard in rows:
        is_char = len(norm(expect)) <= 2
        status = "OK " if r >= OK else ("chr" if is_char else "BAD")
        if status == "BAD":
            flagged.append(name)
        if not args.json:
            print(f"{r:6.2f}  {name:<18} [{status}] {expect}")
            if r < 0.95:
                print(f"{'':>6}  {'':<18}       heard: {heard}")
    REPORT.write_text(json.dumps({"flagged": flagged,
                                  "scores": {n: round(r, 3) for r, n, _, _ in rows}},
                                 ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps({"flagged": flagged}, ensure_ascii=False))
    else:
        print("\nFLAGGED (regenerate with: qa_demo_audio.py fix):",
              " ".join(flagged) if flagged else "none — all clips verify")
        print(f"report written to {REPORT.name}")


def cmd_fix(args) -> None:
    cm = clip_map()
    if args.clips:
        fix = [c if c.endswith(".mp3") else c + ".mp3" for c in args.clips]
    elif REPORT.exists():
        fix = json.loads(REPORT.read_text())["flagged"]
    else:
        sys.exit("No clips given and no _qa_report.json — run `audit` first or name clips.")
    fix = [f for f in fix if f in cm]
    if not fix:
        print("Nothing to fix."); return
    norm = _normalizer()
    transcribe = make_transcriber()
    tmp = Path("/tmp/qa_demo_regen"); tmp.mkdir(exist_ok=True)
    backup = tmp / "backup"; backup.mkdir(exist_ok=True)
    best = {}
    for n in fix:
        f = AUDIO / n
        r0 = score(cm[n], transcribe(f), norm) if f.exists() else 0.0
        best[n] = {"ratio": r0, "orig": r0, "wav": None}
        print(f"baseline {n}: {r0:.2f}")
    for rnd, temp in enumerate(TEMPS):
        pending = [n for n in fix if best[n]["ratio"] < ACCEPT]
        if not pending:
            break
        print(f"\n-- round {rnd} (temp={temp}) — {len(pending)} pending --")
        idx = {i: n for i, n in enumerate(pending)}
        items = [{"index": i, "text": cm[n], "instruct": None,
                  "outWav": str(tmp / f"{n}.r{rnd}.wav")} for i, n in idx.items()]
        rep = synth(items, temp, tmp)
        for i, n in idx.items():
            it = rep.get(i, {})
            if not it.get("ok"):
                print(f"   {n}: gen failed: {it.get('error')}"); continue
            r = score(cm[n], transcribe(Path(it["outWav"])), norm)
            print(f"   {'✓' if r >= ACCEPT else ' '} {n}: {r:.2f}")
            if r > best[n]["ratio"]:
                best[n].update(ratio=r, wav=it["outWav"])
    print("\n=== results ===")
    changed = []
    for n in fix:
        b = best[n]
        take = b["wav"] and (b["ratio"] >= ACCEPT or b["ratio"] >= b["orig"] + REPLACE_MARGIN)
        if take:
            if (AUDIO / n).exists():
                shutil.copy(AUDIO / n, backup / n)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", b["wav"],
                            "-ac", "1", "-b:a", "96k", str(AUDIO / n)], check=True)
            changed.append(n)
            print(f"  REPLACED {n}: {b['orig']:.2f} -> {b['ratio']:.2f}  (backup: {backup/n})")
        else:
            print(f"  kept     {n}: {b['orig']:.2f} (best regen {b['ratio']:.2f}; "
                  f"likely rare-char ASR noise on good audio)")
    print("\nchanged:", " ".join(changed) if changed else "none")
    print("Re-run `qa_demo_audio.py audit` to confirm.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Audio QA + self-healing for the Encoding Dictionary demo.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="transcribe every clip and score it against its intended text")
    a.add_argument("clips", nargs="*", help="limit to these clip names (default: all)")
    a.add_argument("--json", action="store_true", help="print machine-readable flagged list")
    a.add_argument("--layout-only", action="store_true", help="with --json: dump clip->text map, skip transcription")
    a.set_defaults(func=cmd_audit)
    fx = sub.add_parser("fix", help="regenerate flagged (or named) clips until they verify")
    fx.add_argument("clips", nargs="*", help="clip names to fix (default: the last audit's flagged list)")
    fx.set_defaults(func=cmd_fix)
    args = ap.parse_args()
    if not (args.cmd == "audit" and args.json and args.layout_only):
        ensure_runtime()
    args.func(args)


if __name__ == "__main__":
    main()
