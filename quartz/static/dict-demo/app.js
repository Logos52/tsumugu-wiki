/* Tsumugu Encoding Dictionary — prototype behaviors */
(function () {
  "use strict";

  /* ---------- audio: Serena mp3 first, browser voice fallback ---------- */
  let currentAudio = null;
  let speakSeq = 0;

  function stopAll() {
    speakSeq++;
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    window.speechSynthesis && speechSynthesis.cancel();
    document.querySelectorAll(".speaking").forEach((n) => n.classList.remove("speaking"));
    document.querySelectorAll(".sent.playing").forEach((n) => n.classList.remove("playing"));
  }

  function speakTTS(text, rate) {
    return new Promise((resolve) => {
      if (!window.speechSynthesis) return resolve();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = "zh-TW";
      u.rate = rate || 0.92;
      const vs = speechSynthesis.getVoices();
      const v = vs.find((x) => /zh[-_](TW|HK)/i.test(x.lang)) || vs.find((x) => /^zh/i.test(x.lang));
      if (v) u.voice = v;
      u.onend = u.onerror = () => resolve();
      speechSynthesis.speak(u);
    });
  }

  function playClip(src, rate) {
    return new Promise((resolve, reject) => {
      const a = new Audio(src);
      a.playbackRate = rate || 1;
      currentAudio = a;
      a.onended = () => resolve();
      a.onerror = () => reject(new Error("missing"));
      a.play().catch(() => reject(new Error("blocked")));
    });
  }

  /* play one element: data-audio (mp3, Serena) else data-say (browser voice) */
  async function playEl(el, opts) {
    const seq = ++speakSeq;
    const slow = document.body.classList.contains("slow");
    const src = el.getAttribute("data-audio");
    const say = el.getAttribute("data-say") || el.textContent;
    el.classList.add("speaking");
    try {
      if (src) await playClip(src, slow ? 0.85 : 1);
      else await speakTTS(say, slow ? 0.7 : 0.92);
    } catch (e) {
      if (seq === speakSeq) await speakTTS(say, slow ? 0.7 : 0.92); // Serena pending → fallback
    }
    if (seq === speakSeq) el.classList.remove("speaking");
  }

  /* ---------- play-through with synced section highlight ---------- */
  async function playEntry() {
    stopAll();
    const seq = speakSeq;
    const secs = Array.from(document.querySelectorAll(".sec[data-speak]")).filter(
      (s) => s.offsetParent !== null && !s.classList.contains("veiled")
    );
    if (!secs.length) {
      const g = document.querySelector("[data-play-self]");
      if (g) await playEl(g);
      for (const sent of document.querySelectorAll(".sent")) {
        if (seq !== speakSeq) return;
        sent.classList.add("playing");
        sent.scrollIntoView({ behavior: "smooth", block: "center" });
        await playEl(sent.querySelector(".zh-t"));
        sent.classList.remove("playing");
        await new Promise((r) => setTimeout(r, 350));
      }
      return;
    }
    for (const s of secs) {
      if (seq !== speakSeq) return;
      s.scrollIntoView({ behavior: "smooth", block: "center" });
      await playEl(s);
    }
  }

  /* ---------- depth dial ---------- */
  function setDepth(d) {
    document.body.dataset.depth = d;
    document.querySelectorAll(".seg [data-depth]").forEach((b) =>
      b.classList.toggle("on", b.dataset.depth === d)
    );
    localStorage.setItem("ted-depth", d);
  }

  /* ---------- study mode: staged reveal ---------- */
  let revealIdx = 0;
  function studySections() {
    return Array.from(document.querySelectorAll(".sec[data-study]"));
  }
  function applyStudy() {
    studySections().forEach((s, i) => s.classList.toggle("veiled", i >= revealIdx));
    const bar = document.querySelector(".revealbar .btn");
    if (bar) bar.textContent = revealIdx >= studySections().length ? "完成 — exit study" : "Reveal next ↓";
  }
  function toggleStudy(on) {
    document.body.classList.toggle("study", on);
    const b = document.getElementById("studyBtn");
    if (b) b.classList.toggle("on", on);
    if (on) { setDepth("3"); revealIdx = 0; applyStudy(); }
    else studySections().forEach((s) => s.classList.remove("veiled"));
  }

  /* ---------- story-first vs analysis-first ---------- */
  function setLead(lead) {
    const duo = document.querySelector(".duo");
    if (duo) {
      const story = duo.querySelector(".card-story");
      const origin = duo.querySelector(".card-origin");
      if (story && origin) {
        if (lead === "story") duo.insertBefore(story, origin);
        else duo.insertBefore(origin, story);
      }
    }
    document.querySelectorAll("[data-lead]").forEach((b) =>
      b.classList.toggle("on", b.dataset.lead === lead)
    );
    localStorage.setItem("ted-lead", lead);
  }

  /* ---------- definitions default (word page) ---------- */
  function setDef(d) {
    document.body.dataset.def = d;
    document.querySelectorAll("[data-def-btn]").forEach((b) =>
      b.classList.toggle("on", b.dataset.defBtn === d)
    );
    document.querySelectorAll(".default-pin").forEach((p) => {
      p.style.display = p.closest(".def").classList.contains(d) ? "" : "none";
    });
    localStorage.setItem("ted-def", d);
  }

  /* ---------- sentence player + play-all ---------- */
  async function playSent(sent) {
    stopAll();
    const seq = speakSeq;
    sent.classList.add("playing");
    await playEl(sent.querySelector(".zh-t"));
    if (seq === speakSeq) sent.classList.remove("playing");
  }
  async function playAllSents() {
    stopAll();
    const seq = speakSeq;
    for (const sent of document.querySelectorAll(".sent")) {
      if (seq !== speakSeq) return;
      sent.classList.add("playing");
      sent.scrollIntoView({ behavior: "smooth", block: "center" });
      await playEl(sent.querySelector(".zh-t"));
      sent.classList.remove("playing");
      await new Promise((r) => setTimeout(r, 350));
    }
  }

  /* ---------- A/B loop waveform (real Serena mp3s; wavesurfer via CDN) ---------- */
  const waves = new Map();
  /* resolve the clip a wavebox should load: explicit data-src, else its sentence's
     clip, else the nearest voiced ancestor (a narration section / definition). */
  function waveSrc(box) {
    if (box.dataset.src) return box.dataset.src;
    const sent = box.closest(".sent");
    if (sent) {
      const z = sent.querySelector(".zh-t");
      if (z && z.getAttribute("data-audio")) return z.getAttribute("data-audio");
    }
    const host = box.closest("[data-audio]");
    return host ? host.getAttribute("data-audio") : null;
  }
  async function toggleWave(box) {
    if (!box) return;
    box.classList.toggle("open");
    if (!box.classList.contains("open") || waves.has(box)) return;
    const src = waveSrc(box);
    if (!src) { box.querySelector(".hint").textContent = "Waveform needs the pre-baked Serena clip (pending for this line)."; return; }
    try {
      const WS = (await import("https://unpkg.com/wavesurfer.js@7/dist/wavesurfer.esm.js")).default;
      const Regions = (await import("https://unpkg.com/wavesurfer.js@7/dist/plugins/regions.esm.js")).default;
      const ws = WS.create({
        container: box.querySelector(".wv"), url: src, height: 52,
        waveColor: "#3b5476", progressColor: "#7aa2ff", cursorColor: "#e8b35a",
      });
      const regions = ws.registerPlugin(Regions.create());
      regions.enableDragSelection({ color: "rgba(232,179,90,.25)" });
      let loop = false, region = null, rate = 1;
      regions.on("region-created", (r) => {
        regions.getRegions().forEach((o) => { if (o !== r) o.remove(); });
        region = r;
      });
      regions.on("region-out", (r) => { if (loop && r === region) r.play(); });
      box.querySelector(".wplay").onclick = () => { stopAll(); region ? region.play() : ws.play(); };
      box.querySelector(".wloop").onclick = (e) => { loop = !loop; e.target.classList.toggle("on", loop); if (loop) (region ? region.play() : ws.play()); };
      box.querySelector(".wspeed").onclick = (e) => {
        rate = rate === 1 ? 0.85 : rate === 0.85 ? 0.75 : 1;
        ws.setPlaybackRate(rate, true); e.target.textContent = rate + "×";
      };
      waves.set(box, ws);
    } catch (e) {
      box.querySelector(".hint").textContent = "Waveform unavailable offline (CDN) — ▶ still plays the clip.";
    }
  }

  /* ---------- predict-reveal flip cards ---------- */
  function bindFlips() {
    document.querySelectorAll(".fc").forEach((c) => {
      c.addEventListener("click", () => {
        c.classList.add("revealed");
        if (c.getAttribute("data-say") || c.getAttribute("data-audio")) { stopAll(); playEl(c); }
      });
    });
  }

  /* ---------- wire up ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    // legend
    const lg = document.getElementById("legendBtn");
    if (lg) lg.addEventListener("click", () => document.querySelector(".legend").classList.toggle("open"));
    // entry play-through
    const pe = document.getElementById("playEntry");
    if (pe) pe.addEventListener("click", playEntry);
    const st = document.getElementById("stopBtn");
    if (st) st.addEventListener("click", stopAll);
    // slow
    const slowB = document.getElementById("slowBtn");
    if (slowB) slowB.addEventListener("click", () => {
      document.body.classList.toggle("slow");
      slowB.classList.toggle("on");
    });
    // depth
    document.querySelectorAll(".seg [data-depth]").forEach((b) =>
      b.addEventListener("click", () => { toggleStudy(false); setDepth(b.dataset.depth); })
    );
    if (document.querySelector(".seg [data-depth]")) setDepth(localStorage.getItem("ted-depth") || "3");
    // study
    const sb = document.getElementById("studyBtn");
    if (sb) sb.addEventListener("click", () => toggleStudy(!document.body.classList.contains("study")));
    const rb = document.querySelector(".revealbar .btn");
    if (rb) rb.addEventListener("click", () => {
      revealIdx++;
      if (revealIdx > studySections().length) { toggleStudy(false); return; }
      applyStudy();
      const next = studySections()[revealIdx - 1];
      if (next) { next.scrollIntoView({ behavior: "smooth", block: "center" }); playEl(next); }
    });
    // lead
    document.querySelectorAll("[data-lead]").forEach((b) =>
      b.addEventListener("click", () => setLead(b.dataset.lead))
    );
    if (document.querySelector("[data-lead]")) setLead(localStorage.getItem("ted-lead") || document.body.dataset.leadDefault || "origin");
    // defs
    document.querySelectorAll("[data-def-btn]").forEach((b) =>
      b.addEventListener("click", () => setDef(b.dataset.defBtn))
    );
    if (document.querySelector("[data-def-btn]")) setDef(localStorage.getItem("ted-def") || "en");
    // section play buttons
    document.querySelectorAll(".sec .play").forEach((p) =>
      p.addEventListener("click", (e) => { e.stopPropagation(); stopAll(); playEl(p.closest(".sec")); })
    );
    // sentence play buttons
    document.querySelectorAll(".sent").forEach((sent) => {
      const pl = sent.querySelector(".sp");
      if (pl) pl.addEventListener("click", () => playSent(sent));
    });
    // every A/B-loop toggle → its nearest wavebox (example sentences, narration
    // sections, definitions). closest(".sent") wins inside the examples list, so
    // each sentence keeps its own waveform; section toggles get the section's.
    document.querySelectorAll(".swave").forEach((wv) => {
      const host = wv.closest(".sent, .sec, .def, .wavehost");
      const box = host && host.querySelector(".wavebox");
      if (box) wv.addEventListener("click", (e) => { e.stopPropagation(); toggleWave(box); });
    });
    const pa = document.getElementById("playAll");
    if (pa) pa.addEventListener("click", playAllSents);
    // header glyph / term audio
    document.querySelectorAll("[data-play-self]").forEach((g) =>
      g.addEventListener("click", () => { stopAll(); playEl(g); })
    );
    bindFlips();
    if (window.speechSynthesis) speechSynthesis.getVoices(); // warm voices
  });
})();

// Peek & reveal layer: word glosses (shift-hover or tap) + translation modes
(() => {
  const on = (v) => document.body.classList.toggle("gloss-on", v);
  addEventListener("keydown", (e) => { if (e.key === "Shift") on(true); });
  addEventListener("keyup", (e) => { if (e.key === "Shift") on(false); });
  addEventListener("blur", () => on(false));

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".w[data-gloss]").forEach((w) => {
      w.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const had = w.querySelector(".tip");
        document.querySelectorAll(".w .tip").forEach((x) => x.remove());
        if (!had) {
          const s = document.createElement("span");
          s.className = "tip";
          s.textContent = w.dataset.gloss;
          w.appendChild(s);
        }
      });
    });
    document.addEventListener("click", (ev) => {
      if (!ev.target.closest(".w")) document.querySelectorAll(".w .tip").forEach((x) => x.remove());
    });

    const firstSent = document.querySelector(".sent");
    if (!firstSent) return;
    const exSec = firstSent.closest("section") || firstSent.parentElement;
    const h2 = exSec.querySelector("h2");

    const seg = document.createElement("div");
    seg.className = "seg trseg";
    seg.innerHTML = '<button data-tr="tap">譯 on tap</button><button data-tr="blur">blurred</button><button data-tr="always">shown</button>';
    if (h2) h2.insertAdjacentElement("afterend", seg);
    else exSec.insertBefore(seg, exSec.firstChild);

    const hint = document.createElement("div");
    hint.className = "hint";
    seg.insertAdjacentElement("afterend", hint);

    const hints = {
      tap: "Tap a sentence for its translation. Hold ⇧ Shift and hover — or tap — a dotted word for its gloss.",
      blur: "Tap a blurred line to focus it. ⇧ Shift + hover — or tap — a dotted word for its gloss.",
      always: "⇧ Shift + hover — or tap — a dotted word for its gloss.",
    };
    function setTr(m) {
      document.body.dataset.tr = m;
      localStorage.setItem("ted-tr", m);
      seg.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.tr === m));
      hint.textContent = hints[m];
      document.querySelectorAll(".sent.open").forEach((s) => s.classList.remove("open"));
    }
    seg.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => setTr(b.dataset.tr)));
    setTr(localStorage.getItem("ted-tr") || "tap");

    document.querySelectorAll(".sent").forEach((s) => {
      const z = s.querySelector(".zh-t");
      if (z) z.addEventListener("click", (ev) => {
        if (ev.target.closest(".w")) return;
        if (document.body.dataset.tr === "tap") s.classList.toggle("open");
      });
      const tr = s.querySelector(".tr");
      if (tr) tr.addEventListener("click", () => {
        if (document.body.dataset.tr === "blur") s.classList.toggle("open");
      });
    });
  });
})();
