"""TTS batching and clip scoring for the wiki audio scripts."""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

from wiki_vocab_data import TTS_MODEL, tsumugu_repo

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
