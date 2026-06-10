---
type: pedagogy
lang: en
target_lang: zh-Hant
title: Graded Input and Comprehensible Media
tags:
  - pedagogy
  - graded-input
  - comprehensible-input
  - listening
  - media
  - vocabulary
---

# Graded Input and Comprehensible Media

Distilled from the recurring threads across 34 "Get Speaking Mandarin" Q&A sessions. The pattern is consistent: input only works when it is *almost* understood and *almost* heard. Too hard and it is noise; too slow and it is a lie about how the language sounds. This page sets the rules for choosing, leveling, and sequencing input — for a learner reading and listening, and for an AI generating graded readings and vocab.

## The Comprehensibility Sweet Spot

- Target **~80% comprehensibility**. If more than **25% of characters/words are new**, the text is too hard — stop and build frequency flashcards first. Roughly 75% known vocabulary is the floor that supports comprehension.
- Sort all input by **vocabulary frequency**. The top **~1,000 frequency words cover 90%+ of most shows**. Learn that core, then layer content-specific vocab on top.
- Graded readers should add **~60 new words per level** — small, deliberate increments. A brute-force start (e.g. a 150-character first book) works because the gap stays bounded.
- Diagnose load mechanically before committing: extract the unique characters of a text (e.g. neovim `unique`), check unknowns in a dictionary (Pleco), and **defer the text if >25% is new**.
- Below B1, media trains **intonation, not vocab/grammar**. Movies become highly effective only around **HSK5+**. Match the medium to the level — don't expect plot-heavy film to teach a beginner.

## Master Vocab Before You Chorus

- Know **~80% of a dialogue's vocabulary before chorusing it**. Chorusing an unanchored text degrades into empty pronunciation drill with no semantic hooks — the reps don't stick to meaning.
- Mine new vocabulary **only from material you have already consumed** (completed lessons, finished graded readers). Pulling words from unknown sources floods you with incidental vocab and derails the target practice.
- Add HSK / frequency-list words **only once they have actually appeared** in your lessons or reading. Frequency lists are a guide, not a syllabus.
- Know the gloss *before* the lesson, then defer meaning *within* a single rep cycle so attention can go to cadence. "Defer meaning" is about the moment of repetition, not about studying blind.

## Real Audio, Real Speed

- Use **natural-speed native audio with accurate transcripts**. Artificially slowed textbook speech distorts prosody, tone contours, and word boundaries — it teaches a register that does not exist.
- To build stamina without distorting the model, slow **playback** (0.8–0.9x) on day one and bump it up daily back to 1.0x. This is a temporary scaffold, not a different recording.
- Read **characters while listening**, not romanization. Characters disambiguate homophones and reinforce grammatical form; pinyin lets the brain default to alphabetic processing and bypass tone internalization.
- Native fast speech **compresses and reduces**: neutral tones drop, vowels shorten, syllables merge (`zheyang` → `jiang`). Learn both the reduced and the full forms at native tempo. Male speakers compress and nasalize more and are harder — train on them deliberately.
- Expect **100+ (sometimes 250+) reps** of a single native-speed sentence just to catch its word boundaries. This is normal, not failure.

## Choose for Engagement, Not Relevance

- **Intrinsic motivation beats topical relevance.** Boredom kills consistency, and consistency is the whole game. Pick content you actually want to finish.
- **Action and visual content is more comprehensible** than plot-heavy or abstract material — cartoons, cooking shows, shopping shows. The visual channel carries meaning the ear can't yet decode.
- Pick speakers who reflect **the everyday speech you want to mimic**, not stylized or young-anime voices. You will sound like your input.
- Exploit repetitive structure: **time-loop films** that replay a scene 7–8 times with small variations force deep listening and lock patterns. Repetitive narrative (e.g. *Journey to the West*) is far easier than allusive literary text.
- For hard classical texts, **pre-load**: read a simpler or translated version, or watch the screen adaptation, before tackling the original. Technical/scientific Chinese is easier than literary — it prizes clarity over allusion.

## Reading + Listening, Together

- Learners routinely **understand a sentence in writing but miss it by ear.** Integrate reading and listening *in tandem*, not sequentially — the transcript is what converts heard noise into recognized words.
- Once you know **~3,000–4,000 characters**, component/radical inference unlocks context-guessing the way roots do in European languages. Below that, guessing is unreliable; look it up.
- **Background/passive listening habituates the ear** to the sound inventory and rhythm even without comprehension — but it does **not** substitute for concentrated, active chorusing. Treat it as a supplement that lowers the activation energy of focused work, never as the work itself.

## Tooling

- **Mandarin Companion** — graded readers (150-char start, +60/level, clickable Kindle glosses).
- **Mandarin Spot** — hover-lookup over arbitrary text.
- **Pleco** — multiple C–C dictionaries, strong handwriting recognition; use it for the unknown-character triage above.
- **SubEasy** — auto PRC/Taiwan subtitles (~1–2 errors per 2-min clip).
- **YouGlish** — video search for words in context; more reliable than crowdsourced Forvo, whose dialect quality varies.
- **Outlier foundation podcast** — start once you grasp 60–70% without the script.
- **Audacity** silence-detection (cut at >0.4s gaps) auto-segments English–Chinese–English files into cards and lets you set per-sentence reps.

## Guidance for AI Generating Graded Readings + Vocab

- **Cap novelty per unit.** Target ~80% known vocabulary in any generated reading; never exceed ~25% new tokens. Prefer ~60 new words per level step.
- **Recycle, then introduce.** Balance roughly 50–70% review vocab with 30–50% new, anchored slightly above the learner's current band (deliberate slight overshoot, e.g. anchored to HSK3) so reading stays a stretch, not a wall.
- **Store sentences, not words.** Vocab entries must carry their sentence/context — the sentence is the retrieval pathway. Embed new words in narrative; isolated entries fail to trigger recall.
- **Audio-first, no romanization.** Every word must be hearable before it is processed. Generate audio-cue → character cards. Strip pinyin/Latin script from card faces; use pure characters or zhuyin only.
- **Source vocab from consumed material only.** Draw new words from texts the learner has already finished, not from external frequency lists in the abstract. Add a frequency word only after it has appeared in graded content.
- **Teach measure words with their nouns**, and introduce **one meaning per word first**, revisiting polysemy later, to cap cognitive load.
- **Generate at natural tempo.** Produce audio at native speed; expose reduced *and* full forms. Do not "clean up" connected-speech compression — it is the target, not an error.
- **Pre-check your own output.** LLM-generated Chinese practice sentences have needed ~40% native correction; hallucination in the target language is common. Validate generated text against a frequency/known-word model and flag anything above the novelty cap rather than emitting it blind.
