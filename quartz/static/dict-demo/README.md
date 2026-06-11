# Tsumugu Encoding Dictionary — demo audio pipeline & QA

Static prototype under `quartz/static/dict-demo/` (served verbatim by Quartz, no build
step). Every Chinese line is pre-voiced with **Qwen3-TTS, voice "Serena"** (local,
Apple-Silicon, mlx-audio). This doc is the contract + the tooling for keeping that
audio **present, correct, and waveform-enabled**. It is written to be run by any agent.

## The markup convention (source of truth for audio)

A playable Chinese line carries two attributes:

- `data-audio="audio/<clip>.mp3"` — the pre-baked Serena clip
- `data-say="…"` — the **intended text**; this is what the clip is supposed to say and
  what QA checks against. (`data-say` also feeds the browser-voice fallback.)

This appears on three kinds of element:

| element | example | clip naming |
|---|---|---|
| example sentence | `.sent > .zh-t[data-audio]` | `<term>-ex-<n>.mp3` |
| narration section | `.sec[data-audio]` (字源/故事/釋義/EVOLUTION) | `<term>-origin/story/meanings/evolution.mp3` |
| definition / headword | `.def.zh` (with `data-src` on its wavebox), glyph | `<term>-def-zh.mp3`, `<term>-char.mp3` |

**Waveforms (🌊 A/B-loop):** any line that should be loopable has a `.swave` toggle and a
`.wavebox`. `app.js`'s `waveSrc()` resolves the clip from `data-src` → the sentence's own
`.zh-t[data-audio]` → the nearest ancestor with `[data-audio]`. So a wavebox needs **no
audio attribute of its own** unless its clip lives on a sibling (then set `data-src`).
To add a waveform to a new line: add the `.swave` button + the standard `.wavebox` block;
the wiring is automatic on `DOMContentLoaded`.

## The three tools (run from anywhere; they self-locate)

Both Python tools find their files relative to their own location and **re-exec into the
Tsumugu voice venv automatically** — just call them with system `python3`.

```sh
cd quartz/static/dict-demo      # (optional; tools work from any cwd)

# 1. GENERATE any clips listed in the manifest that don't exist yet (idempotent)
python3 render_demo_audio.py

# 2. AUDIT — transcribe every clip back (whisper) and score vs its data-say
python3 qa_demo_audio.py audit

# 3. FIX — regenerate whatever audit flagged, at lower temperature, until it verifies
python3 qa_demo_audio.py fix                 # all flagged
python3 qa_demo_audio.py fix she-ex-2 gao-ex-2   # or specific clips
python3 qa_demo_audio.py audit               # re-confirm
```

`render_demo_audio.py` holds the clip→text manifest for **new** content (add a
`(filename, text)` tuple and re-run). `qa_demo_audio.py` derives clip→text directly from
the HTML `data-say`, so it covers every clip the demo actually references.

## Why QA exists (the failure it catches)

Qwen3-TTS occasionally **hallucinates**: a clip exists and plays, but is garbled,
stuttered, or has a wrong word (e.g. 廣告→"光勾", or babble before the sentence). You can't
hear this by checking that files exist. `audit` catches it by transcribing each clip with
`whisper-large-v3-turbo`, normalising both sides (OpenCC → Simplified, CJK-only) and
scoring with `difflib`:

- **≥ 0.80** → OK
- **< 0.80** → BAD (regenerate) — for real sentences
- **≤ 2 chars** → `chr`: isolated glyphs/headwords transcribe unreliably; reported, never flagged.

Long teacher narrations (字源/釋義/EVOLUTION) can sit ~0.78–0.85 purely from rare-character
ASR noise (彳 辵 金文 …) on **good** audio. `fix` keeps a regenerated take only if it beats
the original, so it never churns audio that's actually fine — a stubborn ~0.80 narration is
a known false positive, not a defect.

## Requirements

Everything is already in the Tsumugu **voice venv** (the tools find it via
`TSUMUGU_VOICE_PYTHON`, then `<tsumugu>/personal/research/bakeoff/.venv`, then
`<tsumugu>/personal/voice/.venv`): `mlx_audio`, `mlx_whisper`, `opencc`, `soundfile`,
`numpy`; plus `ffmpeg` on PATH. Models are cached on first use (Serena ~3.5 GB, whisper
~1.5 GB). The TTS worker lives in the **engine repo**:
`<tsumugu>/scripts/gen/voice/synthesize_qwen3_mlx.py`.

Overrides if auto-discovery fails: `TSUMUGU_REPO=/path/to/tsumugu`,
`TSUMUGU_VOICE_PYTHON=/path/to/venv/bin/python`.

## Publishing

`RENDER-AND-PUBLISH-DICT-DEMO.command` (repo root) renders → commits the demo files →
cherry-picks onto `main` → pushes (Pages deploys in ~2 min). Run `audit` and ensure it is
clean **before** publishing. Live URL:
<https://logos52.github.io/tsumugu-wiki/static/dict-demo/index.html>.
