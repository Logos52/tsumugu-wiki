#!/bin/bash
# Tsumugu Encoding Dictionary demo: render Serena clips + publish to GitHub Pages.
# Safe by design: commits ONLY the demo files + the one wiki page; your GSM2 WIP
# is stashed around the main-branch publish and restored exactly as it was.
set -euo pipefail
cd "$(dirname "$0")"
LOG="quartz/static/dict-demo/publish.log"
exec > >(tee "$LOG") 2>&1
echo "== Tsumugu Encoding Dictionary — render + publish ($(date)) =="

echo "-- [1/3] rendering Serena clips (Qwen3-TTS via mlx-audio) --"
python3 quartz/static/dict-demo/render_demo_audio.py

echo "-- [2/3] committing demo files on $(git rev-parse --abbrev-ref HEAD) --"
rm -f .git/index.lock
git add quartz/static/dict-demo "content/Tsumugu Encoding Dictionary.md" RENDER-AND-PUBLISH-DICT-DEMO.command
git commit -m "Tsumugu Encoding Dictionary — interactive prototype (4 entries + sound series, fully Serena-voiced, A/B-loop waveforms)" || echo "(nothing new to commit)"
DEMO_COMMIT=$(git rev-parse HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "-- [3/3] publishing to main (deploys GitHub Pages) --"
if [ "$BRANCH" = "main" ]; then
  git push origin main
else
  STASHED=0
  if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git stash push -u -m "ted-demo-publish-wip" && STASHED=1
  fi
  git checkout main
  git cherry-pick "$DEMO_COMMIT" || { echo "CHERRY-PICK FAILED — aborting safely"; git cherry-pick --abort; git checkout "$BRANCH"; [ "$STASHED" = 1 ] && git stash pop; exit 1; }
  git push origin main
  git checkout "$BRANCH"
  [ "$STASHED" = 1 ] && git stash pop
fi

echo "== DONE — live in ~2 min: https://logos52.github.io/tsumugu-wiki/static/dict-demo/index.html =="
read -n 1 -s -r -p "Press any key to close…" || true
