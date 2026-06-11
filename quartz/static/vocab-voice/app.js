/* Wiki reading vocab — Serena clips + A/B-loop waveforms (dict-demo contract). */
(function () {
  "use strict";
  if (!document.querySelector(".vocab-sent")) return;

  let currentAudio = null;
  let speakSeq = 0;
  const waves = new Map();

  function stopAll() {
    speakSeq++;
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    window.speechSynthesis && speechSynthesis.cancel();
    document.querySelectorAll(".vocab-sent.playing, .zh-t.speaking").forEach((n) => {
      n.classList.remove("playing", "speaking");
    });
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

  function resolveAudioSrc(el, attr) {
    const raw = el.getAttribute(attr);
    if (!raw) return null;
    if (/^https?:\/\//.test(raw) || raw.startsWith("/")) return raw;
    return new URL(raw, window.location.href).href;
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

  async function playZh(el) {
    const seq = ++speakSeq;
    const src = resolveAudioSrc(el, "data-audio");
    const say = el.getAttribute("data-say") || el.textContent;
    el.classList.add("speaking");
    try {
      if (src) await playClip(src, 1);
      else await speakTTS(say, 0.92);
    } catch (e) {
      if (seq === speakSeq) await speakTTS(say, 0.92);
    }
    if (seq === speakSeq) el.classList.remove("speaking");
  }

  function waveSrc(box) {
    const sent = box.closest(".vocab-sent");
    if (!sent) return null;
    const z = sent.querySelector(".zh-t");
    return z ? resolveAudioSrc(z, "data-audio") : null;
  }

  async function toggleWave(box) {
    if (!box) return;
    box.classList.toggle("open");
    if (!box.classList.contains("open") || waves.has(box)) return;
    const src = waveSrc(box);
    if (!src) {
      const hint = box.querySelector(".vocab-hint");
      if (hint) hint.textContent = "Waveform needs the Serena clip for this line.";
      return;
    }
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
      box.querySelector(".vocab-wplay").onclick = () => { stopAll(); region ? region.play() : ws.play(); };
      box.querySelector(".vocab-wloop").onclick = (e) => {
        loop = !loop; e.target.classList.toggle("on", loop);
        if (loop) (region ? region.play() : ws.play());
      };
      box.querySelector(".vocab-wspeed").onclick = (e) => {
        rate = rate === 1 ? 0.85 : rate === 0.85 ? 0.75 : 1;
        ws.setPlaybackRate(rate, true); e.target.textContent = rate + "×";
      };
      waves.set(box, ws);
    } catch (e) {
      const hint = box.querySelector(".vocab-hint");
      if (hint) hint.textContent = "Waveform unavailable offline (CDN) — ▶ still plays the clip.";
    }
  }

  function bind() {
    document.querySelectorAll(".vocab-sent:not([data-voice-bound])").forEach((sent) => {
      sent.dataset.voiceBound = "1";
      const zh = sent.querySelector(".zh-t");
      const playBtn = sent.querySelector(".vocab-play");
      const waveBtn = sent.querySelector(".vocab-swave");
      const box = sent.querySelector(".vocab-wavebox");
      if (playBtn && zh) {
        playBtn.addEventListener("click", () => { stopAll(); sent.classList.add("playing"); playZh(zh).then(() => sent.classList.remove("playing")); });
      }
      if (zh) zh.addEventListener("click", () => { stopAll(); sent.classList.add("playing"); playZh(zh).then(() => sent.classList.remove("playing")); });
      if (waveBtn && box) waveBtn.addEventListener("click", () => toggleWave(box));
    });
  }

  function init() { bind(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
  document.addEventListener("nav", init);
})();