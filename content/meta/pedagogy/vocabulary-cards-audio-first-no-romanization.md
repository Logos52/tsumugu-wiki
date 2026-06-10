I'll write the Markdown file directly as my response. Here it is.

---

```markdown
---
type: pedagogy
lang: en
target_lang: zh-Hant
title: "Vocabulary Cards: Audio-First, No Romanization"
tags:
  - pedagogy
  - vocabulary
  - audio-first
  - no-romanization
  - spaced-repetition
  - flashcards
---

This page distills a recurring pattern across 34 "Get Speaking Mandarin" Q&A sessions: how to build and study vocabulary so it actually surfaces in speech instead of dying on a list. The rules below are written for two readers — a Mandarin learner building their own deck, and an AI generating graded readings and vocab cards. Where the two diverge, the AI-facing rule is called out.

## Core Principle: Sound Is the Object, Not the Word

- Never process a Chinese word for the first time as text. **Hear it before you ever read it.** Reading-only vocab builds a pronunciation gap with no audio reference to fix it later.
- The retrieval pathway is the *sound and the context*, not the spelling. A word stored as silent characters has no hook to pull on when you need to say it.
- A character is a writing system pointing at a sound you already own. If the sound isn't solid, the card just trains alphabetic/visual processing and bypasses the tone system entirely.

## Card Format: Audio Cue → Character Answer

- **Front = audio. Back = character (+ gloss).** The prompt is the native recording; the answer reveals the characters and meaning. This forces listening and recognition to fire together.
- Add a reversed twin for production: **English cue → produce Chinese** (spoken, full voice). This is the card type that surfaces fossilized word-order, aspect-marker (了/過), and time-clause errors. Optional grammar hint on the front (e.g. cue "I can go swimming tomorrow" + hint `可以`) scaffolds production before full dialogue.
- Pair every card with a **sentence or paragraph**, not the bare word. Flashcards aid recall but carry no context; the surrounding sentence is what makes the word retrievable. Story/narrative embedding beats word lists outright.
- Teach **measure words bonded to their noun** on the same card. Splitting them fossilizes measure-word omission.
- One meaning per word at first. Revisit additional senses later to cap cognitive load. (用/使用/利用/運用 differ contextually — e.g. 利用人 = "exploit" — so don't cram senses; let exposure separate them.)

## Kill Romanization

- **No pinyin, no Latin letters on the card.** Latin script lets the brain default to alphabetic processing and silently skip tone internalization. Pinyin was designed for *native* speakers learning to write — it is annotation, not sound-teaching material.
- Use **pure characters or zhuyin (注音)** only. Zhuyin is acceptable because it doesn't trigger the native-alphabet fallback; pinyin and romaji do.
- If you must write a hypothesis of what you heard, write it *before* the characters and *before* re-listening — as a guess to be corrected, never as the card's primary face.

## Source Discipline: Mine Only What You've Already Consumed

- **Pull vocabulary only from material you have already worked through** — course lessons, completed graded readers. Mining from unknown sources floods the deck with incidental new words and derails target practice.
- Add frequency-list / HSK words **only after they have actually appeared** in your lessons. A frequency list is a *guide*, not a queue.
- **Caution on frequency lists:** they're built from *written* Chinese, not spoken. Classroom staples rank far above their real spoken use (e.g. 鉛筆 "pencil" sits around #2400 in real usage but gets taught early). Fill gaps by associative/contextual memory, not by marching down a written-corpus list.

### For the AI generating cards

- Generate cards **only from vocabulary present in the reading you just produced or in lessons already delivered.** Do not inject novel high-frequency words "for coverage."
- Every card MUST carry: native-speed audio, the source sentence, the character form, an English gloss, and (for nouns) the measure word. Never emit a romanized field as the studyable face.
- LLM-generated practice sentences need heavy correction (~40% in observed sessions) and hallucinate freely in non-English. **Translate the prompt into Chinese first**, generate, then have output verified before it becomes a card.
- Auto-segment audio with silence detection (cut at gaps >0.4s) to slice English–Chinese–English files into per-card audio cleanly.

## Why Lists Fail and Context Wins

- Isolated entries fail to trigger recall. The classic failure: a learner couldn't retain body-part words from a list for 2+ years, but retained 腳 ("feet") instantly from a *passage about walking up a mountain*. The narrative was the hook.
- Heavy repetition of sentences/paragraphs (500+ choruses) produces **unconscious recall of vocab you never explicitly drilled.** Flashcards aid recall but lack context — so the deck supplements sentence/paragraph repetition; it does not replace it.

## Recognition Is Not Production

- Passive recognition ≠ active production. Words convert from passive to active through **output and real-world encounter**, not through more recognition reps.
- The reversed (English → spoken Chinese) card is the bridge. Produce *original* personalized answers, not just shadowed scripts — answering topical prompts (e.g. the 20 questions per GSM2/3 lesson) doubles as activation and as real conversation material.
- Only start *varying* a pattern (substitution drills, swapping subjects/objects) **after self-recording confirms your tone and consonant control.** Don't tailor a structure you can't yet pronounce.

## Spaced Repetition Mechanics

- SRS (Anki) keeps a word active for ~2 years, which is what justifies the upfront effort of building rich audio cards. Cheap-to-make bad cards aren't worth the 2-year retention slot.
- **Cap new cards (~20/day).** When the difficult-card count climbs, *consolidate before adding* — stop introducing new cards until the backlog of mature-but-shaky ones is under control.
- Put the truly tedious material (long number sequences) at the *end* of a session; lead with short, engaging words to protect momentum.

## Quick Reference: Card Build Checklist

- [ ] Heard before read
- [ ] Front = audio (or English, for the production twin)
- [ ] Characters or zhuyin only — zero pinyin/Latin
- [ ] Embedded in its source sentence
- [ ] Measure word attached (nouns)
- [ ] One sense first
- [ ] Word came from material already consumed
- [ ] Paired with sentence/paragraph repetition, not studied alone

---

This is one node in the GSM pedagogy set. It connects most directly to chorusing/shadowing (where the audio these cards reference gets produced), sound-first-meaning-second (the same priority applied to single words), and graded-input/comprehensible-reading (the consumed material these cards are mined from).
```