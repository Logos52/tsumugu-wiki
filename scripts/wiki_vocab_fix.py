"""Regenerate wiki vocab clips that failed the transcribe-back check."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from wiki_vocab_data import (
    ACCEPT,
    ASR_HINT,
    ASR_MODEL,
    AUDIO_ROOT,
    OK,
    REPLACE_MARGIN,
    TEMPS,
    collect_entries,
    emit,
    load_manifest,
    save_manifest,
)
from wiki_vocab_speech import score, synth_batch, wav_to_mp3


def run_fix(args, whisper, norm) -> None:
    entries = {f"{entry['slug']}/{entry['clip']}": entry for entry in collect_entries(args.slug)}
    chosen = _chosen(args)
    fix = [entries[key] for key in chosen if key in entries]
    if not fix:
        emit("Nothing to fix.")
        return
    best = _seed(fix, norm, whisper)
    tmp = Path("/tmp/wiki_vocab_fix")
    tmp.mkdir(exist_ok=True)
    for rnd, temp in enumerate(TEMPS):
        pending = [key for key, row in best.items() if row["ratio"] < ACCEPT]
        if not pending:
            break
        _one_round(best, (norm, whisper), (tmp, rnd, temp, pending))
    _save(best)


def _chosen(args):
    if args.clips:
        return args.clips
    report = AUDIO_ROOT / "_qa_report.json"
    if not report.exists():
        sys.exit("No _qa_report.json — run audit first")
    return json.loads(report.read_text())["flagged"]


def _seed(fix, norm, whisper):
    best = {}
    for entry in fix:
        ratio = _current_ratio(entry, norm, whisper)
        best[f"{entry['slug']}/{entry['clip']}"] = {
            "ratio": ratio, "orig": ratio, "wav": None, "e": entry,
        }
        emit(f"baseline {entry['slug']}/{entry['clip']}: {ratio:.2f}")
    return best


def _current_ratio(entry, norm, whisper) -> float:
    if not entry["mp3"].exists():
        return 0.0
    return score(entry["say"], _transcribe(entry["mp3"], whisper), norm)


def _transcribe(path: Path, whisper) -> str:
    result = whisper.transcribe(
        str(path),
        path_or_hf_repo=ASR_MODEL,
        language="zh",
        initial_prompt=ASR_HINT,
        temperature=0.0,
    )
    return result["text"].strip()


def _one_round(best, tools, job) -> None:
    norm, whisper = tools
    tmp, rnd, temp, pending = job
    emit(f"\n-- round {rnd} (temp={temp}) — {len(pending)} pending --")
    index = {i: key for i, key in enumerate(pending)}
    items = [{
        "index": i,
        "text": best[key]["e"]["say"],
        "instruct": None,
        "outWav": str(tmp / f"r{rnd}-{i}.wav"),
    } for i, key in index.items()]
    report = synth_batch(items, temp, tmp)
    for i, key in index.items():
        _keep_better(best, (key, report.get(i, {}), (norm, whisper)))


def _keep_better(best, packed) -> None:
    key, item, tools = packed
    if not item.get("ok"):
        emit(f"   {key}: gen failed: {item.get('error')}")
        return
    norm, whisper = tools
    ratio = score(best[key]["e"]["say"], _transcribe(Path(item["outWav"]), whisper), norm)
    mark = "✓" if ratio >= ACCEPT else " "
    emit(f"   {mark} {key}: {ratio:.2f}")
    if ratio > best[key]["ratio"]:
        best[key].update(ratio=ratio, wav=item["outWav"])


def _save(best) -> None:
    manifest = load_manifest()
    readings = manifest.setdefault("readings", {})
    changed = []
    for key, row in best.items():
        _store(key, (row, readings, changed))
    save_manifest(manifest)
    emit(f"changed: {len(changed)}")


def _store(key, packed) -> None:
    row, readings, changed = packed
    entry = row["e"]
    if _should_take(row):
        wav_to_mp3(Path(row["wav"]), entry["mp3"])
        rec = readings.setdefault(entry["slug"], {}).setdefault(entry["clip"], {"say": entry["say"]})
        rec["ratio"] = round(row["ratio"], 3)
        rec["verified"] = row["ratio"] >= OK
        changed.append(key)
        emit(f"  REPLACED {key}: {row['orig']:.2f} -> {row['ratio']:.2f}")
        return
    emit(f"  kept     {key}: {row['orig']:.2f} (best {row['ratio']:.2f})")


def _should_take(row) -> bool:
    if not row["wav"]:
        return False
    if row["ratio"] >= ACCEPT:
        return True
    if row["ratio"] >= row["orig"] + REPLACE_MARGIN:
        return True
    return row["ratio"] >= OK and row["ratio"] > row["orig"]
