import { readFileSync, existsSync } from "fs"
import { join } from "path"
import { Root as HTMLRoot, Element, Text } from "hast"
import { visit } from "unist-util-visit"
import { QuartzTransformerPlugin } from "../types"

type Manifest = {
  readings?: Record<string, Record<string, { say?: string }>>
}

const EX_PREFIX = "例句 / example:"

function loadManifest(contentDir: string): Manifest {
  const p = join(contentDir, "zh-Hant/audio/vocab/manifest.json")
  if (!existsSync(p)) return {}
  try {
    return JSON.parse(readFileSync(p, "utf-8")) as Manifest
  } catch {
    return {}
  }
}

function bundleSlug(filePath: string): string | null {
  const m = filePath.match(/sources\/videos\/([^/]+)\/vocab\.md$/)
  return m ? m[1] : null
}

function audioRelPrefix(filePath: string): string {
  const parts = filePath.replace(/\\/g, "/").split("/")
  const idx = parts.indexOf("zh-Hant")
  const depth = idx >= 0 ? parts.length - idx - 2 : 1
  return `${"../".repeat(Math.max(depth, 1))}audio/vocab/`
}

function textContent(node: Element): string {
  let out = ""
  visit(node, "text", (n: Text) => {
    out += n.value
  })
  return out.trim()
}

function displayChildren(p: Element): Element["children"] {
  const out: Element["children"] = []
  let pastLabel = false
  for (const ch of p.children ?? []) {
    if (ch.type === "text") {
      const v = ch.value
      if (!pastLabel) {
        const rest = v.replace(/^\s*例句\s*\/\s*example:\s*/i, "")
        if (rest !== v) {
          pastLabel = true
          if (rest) out.push({ type: "text", value: rest })
        }
        continue
      }
      out.push(ch)
    } else if (ch.type === "element" && ch.tagName === "strong") {
      const inner = textContent(ch)
      if (/例句\s*\/\s*example/i.test(inner)) {
        pastLabel = true
        continue
      }
      pastLabel = true
      out.push(ch)
    } else if (pastLabel) {
      out.push(ch)
    }
  }
  return out
}

function voicedBlock(rel: string, say: string, display: Element["children"]): Element {
  return {
    type: "element",
    tagName: "div",
    properties: { className: ["vocab-sent"] },
    children: [
      {
        type: "element",
        tagName: "span",
        properties: {
          className: ["zh-t"],
          dataAudio: rel,
          dataSay: say,
        },
        children: display,
      },
      {
        type: "element",
        tagName: "div",
        properties: { className: ["vocab-tools"] },
        children: [
          {
            type: "element",
            tagName: "button",
            properties: { type: "button", className: ["btn", "vocab-play"], ariaLabel: "Play sentence" },
            children: [{ type: "text", value: "▶" }],
          },
          {
            type: "element",
            tagName: "button",
            properties: { type: "button", className: ["btn", "vocab-swave"], ariaLabel: "A/B loop waveform" },
            children: [{ type: "text", value: "🌊" }],
          },
        ],
      },
      {
        type: "element",
        tagName: "div",
        properties: { className: ["vocab-wavebox"] },
        children: [
          { type: "element", tagName: "div", properties: { className: ["wv"] }, children: [] },
          {
            type: "element",
            tagName: "div",
            properties: { className: ["vocab-wave-ctrls"] },
            children: [
              {
                type: "element",
                tagName: "button",
                properties: { type: "button", className: ["btn", "vocab-wplay"] },
                children: [{ type: "text", value: "▶" }],
              },
              {
                type: "element",
                tagName: "button",
                properties: { type: "button", className: ["btn", "vocab-wloop"] },
                children: [{ type: "text", value: "🔁" }],
              },
              {
                type: "element",
                tagName: "button",
                properties: { type: "button", className: ["btn", "vocab-wspeed"] },
                children: [{ type: "text", value: "1×" }],
              },
            ],
          },
          {
            type: "element",
            tagName: "div",
            properties: { className: ["vocab-hint"] },
            children: [
              {
                type: "text",
                value: "Drag on the waveform to select a slice, then 🔁 to drill it.",
              },
            ],
          },
        ],
      },
    ],
  }
}

export const VocabVoice: QuartzTransformerPlugin = () => {
  return {
    name: "VocabVoice",
    htmlPlugins(ctx) {
      const manifest = loadManifest(ctx.argv.directory)
      return [
        () => {
          return async (tree: HTMLRoot, file) => {
            const fp = file.data.filePath ?? ""
            if (!fp.endsWith("/vocab.md") && !fp.endsWith("-vocab.md")) return
            const slug =
              bundleSlug(fp) ??
              (file.data.frontmatter?.source as string | undefined) ??
              null
            if (!slug || !manifest.readings?.[slug]) return

            const clips = Object.keys(manifest.readings[slug]).sort()
            const prefix = audioRelPrefix(fp)
            let clipIdx = 0

            visit(tree, "element", (node: Element, idx, parent) => {
              if (node.tagName !== "p" || !parent || typeof idx !== "number") return
              const raw = textContent(node)
              if (!raw.includes(EX_PREFIX)) return
              const clip = clips[clipIdx]
              if (!clip) return
              clipIdx++
              const rec = manifest.readings![slug][clip]
              const say = rec?.say ?? raw.replace(/.*例句\s*\/\s*example:\s*/i, "").trim()
              const display = displayChildren(node)
              const rel = `${prefix}${slug}/${clip}`
              const kids =
                display.length > 0
                  ? display
                  : [{ type: "text" as const, value: say }]
              if (kids[0]?.type === "text") {
                kids[0] = { type: "text", value: kids[0].value.trimStart() }
              }
              parent.children[idx] = voicedBlock(rel, say, kids)
            })
          }
        },
      ]
    },
  }
}