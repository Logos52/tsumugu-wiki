"""Transcribe-back report for wiki vocab clips."""
from __future__ import annotations

import json
from pathlib import Path

from wiki_vocab_data import (
    ASR_HINT,
    ASR_MODEL,
    AUDIO_ROOT,
    OK,
    collect_entries,
    emit,
    load_manifest,
    save_manifest,
)
from wiki_vocab_speech import score


def run_audit(args, whisper, norm) -> None:
    manifest = load_manifest()
    readings = manifest.setdefault("readings", {})
    flagged = []
    rows = []
    for entry in collect_entries(args.slug):
        row, bad = _score_entry(entry, readings, (norm, whisper))
        rows.append(row)
        if bad:
            flagged.append(entry)
    save_manifest(manifest)
    rows.sort(key=lambda item: item[0])
    _write_report(rows, flagged, bool(args.json))


def _score_entry(entry, readings, tools):
    norm, whisper = tools
    if not entry["mp3"].exists():
        return (0.0, entry, "<MISSING>"), True
    heard = _transcribe(entry["mp3"], whisper)
    ratio = score(entry["say"], heard, norm)
    rec = readings.setdefault(entry["slug"], {}).setdefault(entry["clip"], {"say": entry["say"]})
    rec["ratio"] = round(ratio, 3)
    rec["verified"] = ratio >= OK
    return (ratio, entry, heard), ratio < OK


def _transcribe(path: Path, whisper) -> str:
    result = whisper.transcribe(
        str(path),
        path_or_hf_repo=ASR_MODEL,
        language="zh",
        initial_prompt=ASR_HINT,
        temperature=0.0,
    )
    return result["text"].strip()


def _write_report(rows, flagged, as_json: bool) -> None:
    if not as_json:
        emit(f"{'ratio':>6}  {'clip':<40} status")
    for ratio, entry, heard in rows:
        _print_row((ratio, entry, heard), as_json)
    names = [f"{entry['slug']}/{entry['clip']}" for entry in flagged]
    report = AUDIO_ROOT / "_qa_report.json"
    report.write_text(json.dumps({"flagged": names}, ensure_ascii=False, indent=2), encoding="utf-8")
    if as_json:
        emit(json.dumps({"flagged": names}))
        return
    emit(f"\nFLAGGED: {len(flagged)} — run `fix` to regenerate")
    emit(f"report: {report}")


def _print_row(row, as_json: bool) -> None:
    ratio, entry, heard = row
    if as_json:
        return
    status = "OK" if ratio >= OK else "BAD"
    emit(f"{ratio:6.2f}  {entry['slug']}/{entry['clip']:<28} [{status}] {entry['say']}")
    if ratio < 0.95:
        emit(f"{'':>6}  {'':40} heard: {heard}")
