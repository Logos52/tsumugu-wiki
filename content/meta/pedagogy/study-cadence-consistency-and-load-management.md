I have enough to match conventions. The frontmatter contract uses `type`, `lang`, `title`, `tags` — exactly what the task specifies. The page goes in `meta/pedagogy/`. Now I'll write the page.

```markdown
---
type: pedagogy
lang: en
target_lang: zh-Hant
title: "Study Cadence, Consistency, and Load Management"
tags: [pedagogy, study-cadence, consistency, load-management, habit, spaced-practice]
---

# Study Cadence, Consistency, and Load Management

> Distilled from the recurring patterns across 34 "Get Speaking Mandarin" live Q&A sessions, where cadence and overload questions surfaced again and again regardless of the specific topic asked. The advice below is for two readers: a Mandarin learner planning real practice sessions, and an AI generating graded readings and vocabulary that have to fit inside those sessions without overloading them.

## The Core Law: Frequency Beats Volume

- **Short daily practice beats long gapped sessions, every time.** 15 minutes a day surpasses a 5-hour session followed by a 2-week gap — the gap erases nearly everything the marathon built.
- **Pace matters less than consistency and correctness.** A slower learner who shows up daily and practices correctly outruns a faster one who binges and disappears.
- **Mastery is a multi-year lifestyle, not a sprint.** Casual ~20 min/day won't reach fluency on its own; what reaches it is years of consistent reps you genuinely enjoy — including enjoying the repetitive "suffering."
- **Reframe slow progress with exposure math.** 3 months at 1 hr/day ≈ ~15 days of a child's waking spoken-input. Tiny, but normal — don't read slowness as failure.

## Session Length and Splitting

- **Stop at cognitive fatigue, don't push through it.** Fatigue often arrives around ~30 min; sessions reliably become counterproductive past ~75 min. Cognitive overload is a signal to break *now*, not to grind.
- **Split into 2–4 short bursts across the day** rather than one marathon. Distributed reps consolidate better and dodge the fatigue ceiling.
- **Focus on one aspect per session** — meaning *or* pronunciation *or* comprehension. You cannot optimize all three simultaneously; trying to fries the session.
- **Temporal consistency lowers cost:** same language at the same time of day reduces the expensive context-switching tax between languages.

## Within-Session Load Management

- **Place easy sentences between hard ones** as mental breaks inside the session — recovery without stopping.
- **Put tedious material at the END** (long number sequences, dull drills) so it doesn't kill momentum; lead with short, engaging items.
- **Slow audio to 0.8–0.9x on day 1**, then bump up daily to build stamina without frying the brain. Slowing is a temporary stamina aid, not a permanent crutch.
- **Isolate problem sentences and repeat them 50+ times** rather than re-running the whole dialogue to fix one stumble.

## Reading the Body's Signals

- **Early-session fatigue is "sore muscles after running" — a sign to keep going, not to quit.** Mental load *decreases* over ~11–12 lessons as control automates, the way driving stops demanding conscious effort. Endurance is built, not given.
- **Avoidance behavior means reduce load, not push harder.** Starting homework at 11pm, procrastination, internal resistance → recalibrate. Redo an *earlier, easier* dialogue to restore motivation before advancing.
- **Rising difficulty in later lessons is progression, not breakdown.** Problem sentences scaling (e.g., ~1 at lesson 11 → ~4 at lesson 16) tracks the material getting harder, exactly as intended.
- **Keep a dated notebook of what's hard vs. easy** and track your endurance. Your optimization patterns are personal; only logged data reveals them.

## Sleep and Spacing as Mechanisms

- **Sleep consolidates motor learning.** Difficult chunks measurably improve *overnight* — distributing reps across days beats cramming them into one because sleep does free work between sessions.
- **Short breaks (a few days) preserve momentum; long breaks (weeks) are hard to restart.** Default to short.
- **One deliberate exception:** a planned week-long break every few months, during heavy cycles, aids consolidation. The line is *intent* — drift erases, planned rest restores. Don't let "consolidation" become an excuse for a 2-week disappearance.

## Pivot Fast When the Method Fails

- **Monitor whether your method produces results, and switch fast if it doesn't.** The cautionary case: 20 years on Spanish, still unable to speak — the fix was changing methods at year one, not working harder at the wrong thing.
- **Working harder at a broken method just fossilizes the error.** Effort is not the variable to maximize first; correctness of method is.

## Guidance for the Generator (AI Producing Readings + Vocab)

- **Size a unit to fit ~30 minutes, not a marathon.** Target dialogues at ~20–26 sentences; reserve ~50-sentence review sets only when they can be split into individual sentence files with multiple reps each.
- **Cap new load per unit.** Keep roughly 50–70% review vocab to 30–50% new; cap daily new cards (~20). When a learner's difficult-card backlog is high, consolidate before adding more.
- **Interleave difficulty deliberately.** Open with short, engaging items; bury number sequences and tedious drills at the end; seat hard sentences between easy ones so the rhythm has built-in recovery.
- **Generate at native tempo with the option to slow.** Provide natural-speed audio plus a clean way to play it at 0.8–0.9x for day-1 stamina — never ship permanently slowed prosody as the primary form.
- **Front-load only one new aspect per unit** (new meaning *or* new sound focus *or* new structure), so a learner can keep "one aspect per session."
- **Build for redo, not one-pass completion.** Tag units so a learner can re-surface an earlier, easier reading on demand (the motivation-restoring move) and so spaced repetition can re-present only the non-fluent items on revisit.
- **Escalate difficulty gradually and label it.** Make rising challenge legible as progression — a learner who knows lesson 16 is *meant* to be harder than lesson 11 reads struggle correctly instead of quitting.
```

The file content is the Markdown above. Path for the page: `/Users/n1/Projects/tsumugu/wiki/.../meta/pedagogy/study-cadence-consistency-and-load-management.md` (target directory `meta/pedagogy/` per the wiki ARCHITECTURE schema; the generator pipeline writes to its configured `OUT`).