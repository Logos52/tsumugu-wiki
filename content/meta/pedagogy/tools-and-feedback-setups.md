---
type: pedagogy
lang: en
target_lang: zh-Hant
title: Tools and Feedback Setups
tags:
  - pedagogy
  - tools-and-feedback-setups
  - chorusing
  - self-recording
  - srs
---

# Tools and Feedback Setups

Distilled from the recurring patterns across 34 "Get Speaking Mandarin" Q&A sessions. The throughline: pronunciation does not improve from diagrams or willpower, it improves from a tight loop of native audio in, your voice out, and an objective comparison of the two. The tools below exist to close the gap between what you *think* you said and what you *actually* said — a gap almost no learner closes on their own.

## The Core Loop: Chorusing First

Chorusing (speaking simultaneously *over* native audio) is the primary acquisition tool, not a warm-up. It builds procedural sound-pattern memory that reading or thinking about tones cannot.

- Chorusing needs only ~1 syllable of working memory, so it scales to long sentences. Shadowing (repeat-after) fails as sentences grow; chorus does not. Both are valid — experiment to find your style.
- The standard unit: **10 choruses + 10 repeats per sentence**. (Instructor wanted 50 with zero gap; 10+10 was the compromise. More is better.)
- Master ~80% of a sentence's vocabulary *before* chorusing it. Chorusing unknown material degrades into empty pronunciation with no semantic anchor.
- Repetition is the mechanism, not lazy advice. Practice until you *can't get it wrong*, not until you get it right once. Expect 100+ (sometimes 250+) reps to even catch word boundaries in native-speed audio.
- Reps keep paying out: after 20–50 reps you suddenly hear a contour you missed. The audio didn't change — your ear sharpened. Keep going.
- For brand-new sounds, chorus **single-syllable words**, not sentences.

## Direct Monitoring: The Single Biggest Upgrade

A ~$100 audio interface with mic-into-headphones for real-time monitoring is the largest feedback improvement over audio-only practice.

- Hearing your own voice *over* the native track in real time catches tone errors instantly — faster than record-then-playback because there's no delay between error and awareness.
- Closed-ear (closed-back) headphones capture bone resonance. The signal you're chorusing correctly: your vowel pitch *locks* with the speaker, with resonance felt in mouth/throat/chest — like singing on-key.
- If you can't monitor live, record to a second track and compare (see below). Monitoring is the upgrade; comparison is the fallback.

## Self-Recording: Beating the Perception Gap

Most learners are convinced they're pronouncing correctly and almost never spontaneously discover they're wrong. Recording plus side-by-side comparison is the objective corrective.

- Your real-time self-perception runs through **bone conduction** and differs from playback. Place your recording *next to the native's same syllable* in Audacity to surface consonant, vowel, and aspiration errors you cannot hear live.
- Real cases from the sessions: months of repetition only to discover the consonant, vowel, *and* aspiration were all wrong; a 22-year learner producing "sh" with the tongue at the back of the palate — listening alone never revealed it.
- The discomfort of hearing yourself is normal, proportional to the learning gain, and levels off after roughly the **first 5 corrections** ("needles in the eyes," then it normalizes). Push through.
- Exaggerate tones heavily. Your over-exaggerated version sounds *normal* on playback — that's the perceptual gap made visible.
- Voice-recognition software (Google Translate voice input) is a practical first intelligibility checkpoint before booking a native speaker.

## Audacity Workflows

Audacity is the workhorse for customizing reps and building cards.

- **Looping** lets you set your own rep count per sentence — chorus a single hard sentence 50+ times on infinite repeat.
- **Silence-detection** (cut at gaps >0.4s) auto-segments English–Chinese–English files into individual Anki cards and splits review lessons into per-sentence files.
- Overlay your voice on one track and the native on another to compare, or to build a self+native blended chorus track.
- Manual extraction is tedious but works: one learner hand-cut 80+ Portuguese lessons into 10–12 reps per phrase in Audacity — that effort is the inspiration for raw-MP3 course design.

## SRS / Anki Card Design

Spaced repetition keeps words active for ~2 years, which justifies the upfront card-building effort. But card *format* determines whether tones internalize.

- **Audio-first cards**: audio cue → character answer. Never process a Chinese word without hearing it first. Reading-only vocab creates pronunciation gaps with no audio database to reference.
- **No romanization on cards.** Latin script lets the brain default to alphabetic processing and bypass tone internalization. Pinyin was designed for native speakers learning to write — it's annotation, not primary material. Use pure characters or zhuyin (bopomofo).
- **Store sentences/context, not isolated words.** The sentence is the retrieval pathway; isolated entries fail to trigger recall. (A learner couldn't retain body-part words from lists for 2+ years but retained "feet" from a passage about walking up a mountain.)
- **Mine vocabulary only from material you've already consumed** — course lessons, completed graded readers. Pulling from unknown sources floods you with incidental new vocab and derails target practice. Add HSK words only once they've appeared in a lesson.
- Always pair nouns with their **measure words** on the card to prevent fossilized omission.
- **Reverse the cards for production**: English cue → produce Chinese. This surfaces fossilized word-order, aspect-marker, and time-clause errors that passive recognition hides. Optional grammar hint (e.g., "I can go swimming tomorrow" + hint *keyi*) scaffolds before full dialogue.
- Cap daily new cards (~20). When difficult-card count is high, consolidate before adding more.

## Practice-Material Selection Tools

- **Use natural-speed native audio with accurate transcripts** — never artificially slowed textbook speech, which distorts prosody, tone contours, and word boundaries. To build stamina, slow *real* audio to 0.8–0.9x on day 1 and bump it up daily, rather than using audio recorded slow.
- Read **characters, not romanization,** while listening — disambiguates homophones and reinforces grammar form.
- Hearing **4+ voices on the same sentences** trains the ear for regional variation and holds attention better than one speaker on repeat.
- Reference tools worth knowing:
  - **Pleco** — handwriting recognition (beats iOS), multiple C-C dictionaries.
  - **YouGlish** — video search for a word in context; more reliable than crowdsourced **Forvo** (dialect-variable).
  - **SubEasy** — auto PRC/Taiwan subtitles (~1–2 errors per 2-min clip).
  - **Mandarin Companion** — graded readers (150-char start, +60/level, clickable Kindle glosses).
  - **Mandarin Spot** — hover-lookup. **Storylingua** — real-time sentence-building feedback. **SpeechLink** — colored tone/consonant feedback.
- For comprehensibility triage: run a text's unique characters (e.g., neovim `unique`), check unknowns in Pleco, and **defer if >25% are new** (~75% known supports comprehension).
- LLM-generated practice sentences need correction — ~40% required teacher fixes. Translating the *prompt* into Chinese first markedly improves output; hallucinations in foreign languages are common.

## Sequencing the Feedback Tools

Order matters — using a corrective tool before its prerequisite wastes it.

- **Shadowing/chorusing comes before intensive pronunciation correction.** Self-discovery of a problem motivates the correction effort; correcting what you haven't yet struggled with doesn't stick.
- **Do dialogue review before isolated tone/cadence work.** The real issue is sentence-level cadence at speed, not isolated tones. Don't pre-emptively drill tone pairs — finish the dialogue review, then do tone/cadence work *on those same sentences*.
- **Start variation only after self-recording confirms tone/consonant control.** Substitution drills and original production come *after* the base pattern is clean, not before.
- **Production tools are the bridge to fluency.** Producing *original* sentences (not just shadowing scripts) is the missing, necessary step. Reverse-card drills and personalized answers to topical prompts activate passive vocab into active use.

## Durable Rules

For the learner:

- Build the loop before building vocab: native audio → your voice → objective comparison. Everything else is secondary.
- Budget for the perception gap. You are probably wrong where you feel most confident; only recording or a native ear will tell you.
- Consistency beats intensity: 15 min/day with the right loop beats 5-hour marathons with gaps.

For an AI generating graded readings + vocab:

- **Ship raw, native-speed MP3s** at the sentence level so learners can chorus, loop, and re-segment them however they work. Respect learner autonomy over the audio.
- **Author audio-first, character-or-zhuyin cards with no romanization,** always embedding the word in a context sentence and attaching measure words to nouns.
- **Draw vocab only from already-presented lesson/reader content** — never inject untranslated incidental vocab.
- **Pair every reading with an accurate character transcript** and avoid slowing audio at the source; let the learner slow playback instead.
- **Generate reverse (English → Chinese) production prompts and topical activation questions** alongside each reading — comprehension cards alone do not build output.
- **Gate chorusing material to ~80% known vocabulary** so the learner anchors meaning instead of parroting sound.