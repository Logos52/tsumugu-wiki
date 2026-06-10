# Render the pending Serena clips (run on the Mac, in tsumugu/)

The demo plays real Qwen3-TTS (Serena) wherever an mp3 exists in `quartz/static/dict-demo/audio/`,
and falls back to the browser voice otherwise. 熱鬧's clips are real already. To voice the
character entries, render the lines below with the existing voice worker and drop the mp3s in
(filenames must match exactly), then commit + push — no code changes needed.

One-liner per clip, from the tsumugu repo root (same worker the voice-notes pipeline uses;
`$PY` = your voice venv python, e.g. `personal/research/bakeoff/.venv/bin/python`):

```bash
OUT=../tsumugu-wiki/quartz/static/dict-demo/audio
render () { $PY scripts/gen/voice/synthesize_qwen3_mlx.py --text "$2" --out /tmp/t.wav && ffmpeg -y -i /tmp/t.wav -ac 1 -b:a 96k "$OUT/$1"; }

# headwords
render zao-char.mp3 "造"
render nao-char.mp3 "鬧"
render she-char.mp3 "射"
render gao-char.mp3 "告"

# 造 sections
render zao-origin.mp3 "造，是辶加告。辶是一隻腳走在路上，表示移動。告表示聲音。本義是到達。"
render zao-story.mp3 "要造任何東西，第一步是走到那個地方。腳先到，東西才造得出來。"
render zao-meanings.mp3 "造的本義是到達。製造、建造的意思，是借音來的。再引申為製作、捏造。"
render zao-expert.mp3 "早期金文的造，從彳或辵，加告。現代製造的意思是音借，跟走路的偏旁沒有邏輯關係。"

# 鬧 sections
render nao-story.mp3 "想像一個夜市：到處都是人，大家都在喊。鬥，吵架的聲音，包住一個市場。這就是鬧。"
render nao-origin.mp3 "鬧的內部結構還沒有可靠的開放來源定論。表面上看是鬥加市，但這可能是民間說法。我們先標記為待考。"
render nao-meanings.mp3 "鬧，吵、熱鬧的鬧。引申為鬧脾氣、鬧笑話。"

# 射 sections
render she-origin.mp3 "射的身，不是身體。古文字裡，它本來是一張拉開的弓，箭在弦上。後來字形訛變，寫成了身。寸是一隻手。"
render she-story.mp3 "一個身體，挽起弓，一寸一寸把弦拉滿，咻，射出去。"
render she-meanings.mp3 "射，本義是射箭。引申為噴射、放射。再引申為影射。"
render she-expert.mp3 "甲骨文的射，畫的是弓和箭。金文加上手。弓形後來訛變成身。"

# series flips
render gao-hao.mp3 "誥" ; render gao-gao2.mp3 "郜" ; render hao-water.mp3 "浩" ; render hao-white.mp3 "皓"
```

After rendering, wire each file with a `data-audio="audio/<name>.mp3"` attribute on the matching
element (the section `data-say` text above matches what's in the HTML, so a future `gen dict-voice`
command can automate this whole file away — that's the real plan; this script is the demo-era bridge).
