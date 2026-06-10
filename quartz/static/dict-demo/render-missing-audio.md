# Superseded

The audio pipeline is documented in **[README.md](./README.md)**. In short:

- **`render_demo_audio.py`** — generate any missing clips (one Qwen3-TTS/Serena worker run + ffmpeg).
- **`qa_demo_audio.py audit`** — transcribe every clip back and score it vs its intended `data-say`; catches garbled/hallucinated audio that still "plays."
- **`qa_demo_audio.py fix`** — regenerate the flagged clips until they verify (keeps the best take, never degrades good audio).
- **`RENDER-AND-PUBLISH-DICT-DEMO.command`** (repo root) — render → commit → publish to `main` (deploys GitHub Pages).
