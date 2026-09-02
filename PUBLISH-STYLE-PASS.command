#!/bin/zsh
# One-click: commit the 鬧/射 style-pass text sync and publish to GitHub Pages.
set -e
cd "$(dirname "$0")"
rm -f .git/index.lock .git/HEAD.lock .git/objects/maintenance.lock 2>/dev/null || true
git add quartz/static/dict-demo
git commit -m "dict-demo: display redesign — tap-to-reveal translations, section wave-chrome stripped, touch word-peek" || echo "(nothing new to commit)"
git push origin main
echo "✅ Pushed. Pages rebuilds in ~1–2 min, then check:"
echo "   https://logos52.github.io/tsumugu-wiki/static/dict-demo/she.html"
echo "   https://logos52.github.io/tsumugu-wiki/static/dict-demo/nao.html"
