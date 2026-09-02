# tsumugu-wiki — what this repo is (2026-09-02)

A Quartz v4 fork that publishes Traditional Chinese learning material to GitHub Pages at https://logos52.github.io/tsumugu-wiki/. The site home and the zh-Hant landing both redirect to https://logos52.github.io (the vault site). What still lives here: 7 YouTube video reading bundles under content/zh-Hant/sources/videos/, GSM1 and GSM2 course vocabulary at content/zh-Hant/gsm1 and gsm2, 15 pedagogy pages under content/zh-Hant/meta/pedagogy/, 819 mp3 pronunciation clips, and the encoding-dictionary demo at quartz/static/dict-demo/.

- Last real content commit: 2026-06-11. The repo is parked, not dead.
- content/private/ holds 35 Q&A transcripts. It is gitignored. A dated tarball sits in iCloud Drive under llm-kb-snapshots/.
- Build: `npm ci && npx quartz build --serve`. node_modules is deleted when parked; reinstall from the lockfile.
- Deploy: .github/workflows/deploy.yml on push to main.
- ARCHITECTURE.md is the June 2026 design spec. Its status block at the top says what shipped and what did not.
- Upstream Quartz docs: https://quartz.jzhao.xyz. This is not the upstream repo.
