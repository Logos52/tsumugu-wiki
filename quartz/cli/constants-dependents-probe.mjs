import { writeFile, readFile } from "node:fs/promises"
import { mock } from "node:test"
import { createRequire } from "node:module"

const require = createRequire(import.meta.url)
const realChildProcess = require("child_process")
const calls = []

mock.module("child_process", {
  namedExports: {
    ...realChildProcess,
    spawnSync: (cmd, args) => {
      calls.push({ cmd, args })
      return { status: 0, stderr: null, stdout: "" }
    },
    execSync: (cmd) => {
      calls.push({ exec: String(cmd) })
      return "probe-branch\n"
    },
  },
})

const childProcess = await import("child_process")
childProcess.spawnSync("quartz-constants-probe", ["ok"])
if (!calls.some((call) => call.cmd === "quartz-constants-probe")) {
  throw new Error("child_process mock did not apply")
}
calls.splice(0, calls.length)

const contentDir = process.env.CONTENT_DIR
const resultPath = process.env.RESULT_PATH
const { handleSync, handleUpdate } = await import("./handlers.js")

await handleUpdate({ directory: contentDir })
await handleSync({
  directory: contentDir,
  commit: false,
  pull: true,
  push: true,
})

const note = await readFile(`${contentDir}/nested/note.md`, "utf8")
await writeFile(
  resultPath,
  JSON.stringify({
    note,
    spawns: calls.filter((call) => call.cmd),
    execs: calls.filter((call) => call.exec),
  }),
)
