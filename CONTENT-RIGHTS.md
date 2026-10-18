# Content rights

Copyright 2026 Logos52 (Tsumugu).

Upstream Quartz files stay under the MIT License in `LICENSE.txt` (Copyright (c) 2021 jackyzha0). `package.json` keeps `"license": "MIT"`. Fork code stays under that same MIT License. The paths below are this repository's own content. The MIT License does not cover them. All rights reserved. No content license is chosen.

## Paths

`content/zh-Hant/sources/videos/` holds seven YouTube video reading bundles: `2025-top-ten-gadgets`, `ai-replaced-my-thinking`, `ios27-epic-update`, `iphone-18-lineup-preview`, `life-as-open-world-rpg`, `steam-controller-review`, and `why-friendship-differs`. Each bundle has `index.md`, `summary.md`, and `vocab.md`. `content/zh-Hant/sources/videos/index.md` is the videos index.

`content/zh-Hant/gsm1/` holds the GSM1 course vocabulary (lessons 02 through 24, plus `index.md`) and 181 pronunciation clips in `content/zh-Hant/gsm1/audio/`.

`content/zh-Hant/gsm2/` holds the GSM2 course vocabulary (19 lesson pages, plus `index.md`) and 512 pronunciation clips in `content/zh-Hant/gsm2/audio/`. The lesson pages present are 01 through 04, 06 through 09, 11 through 14, 16, 18, 19, and 21 through 24.

`content/zh-Hant/audio/vocab/` holds 126 pronunciation clips for those seven video readings, one folder per bundle, plus `manifest.json` and `_qa_report.json`.

`content/meta/pedagogy/` holds 15 pedagogy pages (14 theme pages and `index.md`).

`content/zh-Hant/encoding/熱鬧.md` is an encoding page.

`content/zh-Hant/夜市.md` is a word page.

`content/Tsumugu Encoding Dictionary.md` is the encoding-dictionary note.

These index pages are content: `content/index.md`, `content/meta/index.md`, `content/zh-Hant/index.md`, and `content/zh-Hant/sources/index.md`. `content/index.md` and `content/zh-Hant/index.md` redirect to the vault site.

`content/private/` is gitignored and is not in this tree.

## Encoding-dictionary demo

The Chinese dictionary text in these pages is content. The clips beside them are content.

- `quartz/static/dict-demo/index.html`
- `quartz/static/dict-demo/about.html`
- `quartz/static/dict-demo/series-gao.html`
- `quartz/static/dict-demo/zao.html`
- `quartz/static/dict-demo/nao.html`
- `quartz/static/dict-demo/renao.html`
- `quartz/static/dict-demo/she.html`
- `quartz/static/dict-demo/audio/` (47 mp3 clips)

These files are application code and pipeline notes. The MIT License covers them.

- `quartz/static/dict-demo/app.js`
- `quartz/static/dict-demo/styles.css`
- `quartz/static/dict-demo/render_demo_audio.py`
- `quartz/static/dict-demo/qa_demo_audio.py`
- `quartz/static/dict-demo/README.md`
- `quartz/static/dict-demo/render-missing-audio.md`

`quartz/static/vocab-voice/` is the waveform helper for the video vocab pages. The MIT License covers it. The clips it plays live under `content/zh-Hant/audio/vocab/`.

## Audio

This repository contains 866 mp3 files. 819 are under `content/` (181 in GSM1, 512 in GSM2, 126 in the video vocab folders). 47 are under `quartz/static/dict-demo/audio/`. All rights reserved. No content license is chosen.

## Portraits

This repository contains no portrait or cover image files.

## Site icons

`quartz/static/icon.png` and `quartz/static/og-image.png` are the upstream Quartz site icon and social image. The MIT License covers them.

## Fonts

This repository commits no font files. `quartz.config.ts` names Schibsted Grotesk, Source Sans Pro, and IBM Plex Mono. Those font files are not in the tree.

## Upstream Quartz

Upstream Quartz files stay MIT. That includes the Quartz source under `quartz/` (aside from the dictionary-demo content named above), the Quartz docs under `docs/`, `quartz/static/giscus/`, and `LICENSE.txt`.

`CODE_OF_CONDUCT.md` keeps the Creative Commons Attribution-ShareAlike 3.0 notice already in that file.

`ARCHITECTURE.md`, `CLAUDE.md`, and `scripts/` are fork notes and code. The MIT License covers them. They are not content paths.
