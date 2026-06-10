#!/usr/bin/env python3
"""Render all missing Serena clips for the Encoding Dictionary demo.

Runs the tsumugu repo's Qwen3-TTS worker (mlx-audio, Apple Silicon) once with a
single job covering every clip that doesn't exist yet in ./audio, then converts
wav -> mono 96k mp3 with ffmpeg. Idempotent: existing mp3s are skipped.

Run with system python3 from anywhere; it resolves the voice venv the same way
the voice-notes pipeline does (TSUMUGU_VOICE_PYTHON -> bakeoff venv -> voice venv).
"""
from __future__ import annotations
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../tsumugu-wiki/quartz/static/dict-demo
AUDIO = HERE / "audio"
TSUMUGU = HERE.parents[3] / "tsumugu"           # Projects/tsumugu — sibling of tsumugu-wiki
WORKER = TSUMUGU / "scripts/gen/voice/synthesize_qwen3_mlx.py"
MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"

CLIPS: list[tuple[str, str]] = [
    # headwords (period helps prosody on bare chars)
    ("zao-char.mp3", "造。"),
    ("nao-char.mp3", "鬧。"),
    ("she-char.mp3", "射。"),
    ("gao-char.mp3", "告。"),
    # series flips
    ("gao-decree.mp3", "誥。"),
    ("gao-state.mp3", "郜。"),
    ("hao-vast.mp3", "浩。"),
    ("hao-bright.mp3", "皓。"),
    # 造 sections
    ("zao-origin.mp3", "造，是辶加告。辶是一隻腳走在路上，表示移動。告表示聲音。本義是到達。"),
    ("zao-story.mp3", "想像：要建造任何東西，第一步是走到那個地方。腳先到，東西才造得出來。"),
    ("zao-meanings.mp3", "造的本義是到達。製造、建造的意思，是借音來的。再引申為製作、捏造。"),
    ("zao-expert.mp3", "專家層：早期金文的造，從彳或辵，加告。現代「製造」的意思是音借，跟走路的偏旁沒有邏輯關係。"),
    # 造 examples
    ("zao-ex-0.mp3", "這座橋是去年造的。"),
    ("zao-ex-1.mp3", "這家工廠製造電動車。"),
    ("zao-ex-2.mp3", "他喜歡自己造句，練習中文。"),
    ("zao-ex-3.mp3", "人造的光，比不上太陽。"),
    ("zao-ex-4.mp3", "別捏造事實。"),
    # 鬧 sections
    ("nao-story.mp3", "想像一個夜市：到處都是人，大家都在喊。鬥，吵架的聲音，包住一個市場。這就是鬧。"),
    ("nao-origin.mp3", "字源層:鬧的內部結構還沒有可靠的開放來源定論。表面上看是鬥加市，但這可能是民間說法。我們先標記為待考。"),
    ("nao-meanings.mp3", "鬧，吵、熱鬧的鬧。引申為鬧脾氣、鬧笑話。"),
    # 鬧 examples
    ("nao-ex-0.mp3", "孩子們在客廳鬧個不停。"),
    ("nao-ex-1.mp3", "別鬧了，我在工作。"),
    ("nao-ex-2.mp3", "他一不開心就鬧脾氣。"),
    ("nao-ex-3.mp3", "夜市又熱又鬧，大家都很開心。"),
    ("nao-ex-4.mp3", "我昨天鬧了一個大笑話。"),
    # 射 sections
    ("she-origin.mp3", "字源層：射的身，不是身體。古文字裡，它本來是一張拉開的弓，箭在弦上。後來字形訛變，寫成了身。寸是一隻手。"),
    ("she-story.mp3", "故事：一個身體，挽起弓，一寸一寸把弦拉滿，咻，射出去。"),
    ("she-meanings.mp3", "射，本義是射箭。引申為噴射、放射。再引申為影射。"),
    ("she-expert.mp3", "專家層：甲骨文的射，畫的是弓和箭。金文加上手。弓形後來訛變成身。"),
    # 射 examples
    ("she-ex-0.mp3", "他射箭射得很準。"),
    ("she-ex-1.mp3", "太陽光射進房間裡。"),
    ("she-ex-2.mp3", "噴泉把水射到空中。"),
    ("she-ex-3.mp3", "這部電影影射了很多社會問題。"),
    ("she-ex-4.mp3", "他射門得分了！"),
    # 熱鬧 additions
    ("renao-ex-4.mp3", "婚禮辦得很熱鬧，親戚朋友都來了。"),
    ("renao-def-zh.mp3", "人多、又吵又有活力，讓人覺得很開心的樣子。像夜市、廟會、過年的街上那種氣氛。"),
]


def voice_python() -> str:
    cands = [os.environ.get("TSUMUGU_VOICE_PYTHON"),
             str(TSUMUGU / "personal/research/bakeoff/.venv/bin/python"),
             str(TSUMUGU / "personal/voice/.venv/bin/python")]
    for c in cands:
        if c and Path(c).exists():
            return c
    sys.exit("No voice venv found (TSUMUGU_VOICE_PYTHON / bakeoff / personal/voice).")


def main() -> None:
    AUDIO.mkdir(exist_ok=True)
    missing = [(n, t) for n, t in CLIPS if not (AUDIO / n).exists()]
    print(f"{len(CLIPS)} clips total, {len(missing)} to render.")
    if not missing:
        print("Nothing to do."); return
    if not WORKER.exists():
        sys.exit(f"Worker not found: {WORKER}")
    tmp = Path(tempfile.mkdtemp(prefix="ted-audio-"))
    job = {
        "model": MODEL, "voice": "Serena", "language": "Chinese",
        "items": [{"index": i, "text": t, "instruct": None,
                   "outWav": str(tmp / f"{i:03d}.wav")} for i, (_, t) in enumerate(missing)],
    }
    jobfile = tmp / "job.json"
    jobfile.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
    vpy = voice_python()
    print(f"Rendering {len(missing)} clips via {vpy} (model loads once; first run may download ~3.5 GB)…")
    out = subprocess.run([vpy, str(WORKER), "--job", str(jobfile)],
                         capture_output=True, text=True)
    m = re.search(r"<<<VOICE_NOTES_REPORT>>>\s*(\{.*\})\s*<<<END_VOICE_NOTES_REPORT>>>",
                  out.stdout, re.S)
    if not m:
        sys.stderr.write(out.stderr[-3000:] + "\n")
        sys.exit("Worker produced no report — see stderr above.")
    report = json.loads(m.group(1))
    ok = fail = 0
    for item in report["items"]:
        i = item["index"]; name = missing[i][0]
        if not item.get("ok"):
            print(f"  ✗ {name}: {item.get('error')}"); fail += 1; continue
        mp3 = AUDIO / name
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", item["outWav"],
                            "-ac", "1", "-b:a", "96k", str(mp3)])
        if r.returncode == 0:
            Path(item["outWav"]).unlink(missing_ok=True)
            print(f"  ✓ {name}  ({item.get('durationSec', '?')}s)"); ok += 1
        else:
            print(f"  ✗ {name}: ffmpeg failed"); fail += 1
    print(f"Done: {ok} rendered, {fail} failed.")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
