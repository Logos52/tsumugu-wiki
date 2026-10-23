import test, { describe } from "node:test"
import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { access, cp, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises"
import { tmpdir } from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"
import * as constants from "./constants.js"
import { stashContentFolder } from "./helpers.js"
import { handleRestore } from "./handlers.js"

const exportedNames = [
  "ORIGIN_NAME",
  "QUARTZ_SOURCE_BRANCH",
  "UPSTREAM_NAME",
  "cacheFile",
  "contentCacheFolder",
  "cwd",
  "fp",
  "version",
]

describe("quartz/cli/constants exports", () => {
  test("publishes the values the CLI and build import", async () => {
    assert.deepEqual(Object.keys(constants).sort(), exportedNames)
    assert.equal(Object.hasOwn(constants, "cacheDir"), false)
    assert.equal(constants.ORIGIN_NAME, "origin")
    assert.equal(constants.UPSTREAM_NAME, "upstream")
    assert.equal(constants.QUARTZ_SOURCE_BRANCH, "v4")
    assert.equal(constants.cwd, process.cwd())
    assert.equal(constants.cacheFile, "./quartz/.quartz-cache/transpiled-build.mjs")
    assert.equal(constants.fp, "./quartz/build.ts")
    assert.equal(
      constants.contentCacheFolder,
      path.join(constants.cwd, ".quartz-cache", "content-cache"),
    )
    const pkg = JSON.parse(await readFile(path.join(constants.cwd, "package.json"), "utf8"))
    assert.equal(constants.version, pkg.version)
  })

  test("the CLI prints the exported version", () => {
    const out = spawnSync(process.execPath, ["./quartz/bootstrap-cli.mjs", "--version"], {
      cwd: constants.cwd,
      encoding: "utf8",
    })
    assert.equal(out.status, 0, out.stderr)
    assert.equal(out.stdout.trim(), constants.version)
  })

  test("the build imports the bundle written from fp to cacheFile", async () => {
    const handlerDir = path.dirname(fileURLToPath(new URL("./handlers.js", import.meta.url)))
    const imported = path.resolve(handlerDir, `../../${constants.cacheFile}`)
    const written = path.resolve(constants.cwd, constants.cacheFile)
    assert.equal(imported, written)
    const entry = await readFile(path.resolve(constants.cwd, constants.fp), "utf8")
    assert.match(entry, /export default/)
  })
})

describe("behaviour that depends on the exports", { concurrency: 1 }, () => {
  test("stash and restore round-trip content through contentCacheFolder", async () => {
    const scratch = await mkdtemp(path.join(tmpdir(), "quartz-constants-"))
    const contentFolder = path.join(scratch, "content")
    await mkdir(path.join(contentFolder, "nested"), { recursive: true })
    await writeFile(path.join(contentFolder, "nested", "note.md"), "hello cache")

    await withContentCache(async () => {
      await stashContentFolder(contentFolder)
      assert.equal(
        await readFile(path.join(constants.contentCacheFolder, "nested", "note.md"), "utf8"),
        "hello cache",
      )
      await assert.rejects(access(contentFolder))

      await handleRestore({ directory: contentFolder })
      assert.equal(
        await readFile(path.join(contentFolder, "nested", "note.md"), "utf8"),
        "hello cache",
      )
      await assert.rejects(access(constants.contentCacheFolder))
    })

    await rm(scratch, { recursive: true, force: true })
  })

  test("update and sync pass the exported git names into git", async () => {
    const scratch = await mkdtemp(path.join(tmpdir(), "quartz-constants-"))
    const contentFolder = path.join(scratch, "content")
    const resultPath = path.join(scratch, "result.json")
    await mkdir(path.join(contentFolder, "nested"), { recursive: true })
    await writeFile(path.join(contentFolder, "nested", "note.md"), "hello cache")

    await withContentCache(async () => {
      const out = spawnSync(
        process.execPath,
        [
          "--experimental-test-module-mocks",
          fileURLToPath(new URL("./constants-dependents-probe.mjs", import.meta.url)),
        ],
        {
          cwd: constants.cwd,
          encoding: "utf8",
          env: {
            ...process.env,
            CONTENT_DIR: contentFolder,
            RESULT_PATH: resultPath,
          },
        },
      )
      assert.equal(out.status, 0, `${out.stdout}\n${out.stderr}`)
      const result = JSON.parse(await readFile(resultPath, "utf8"))
      assert.equal(result.note, "hello cache")

      const pulls = result.spawns.filter((call) => call.cmd === "git" && call.args[0] === "pull")
      assert.deepEqual(
        pulls.map((call) => call.args.slice(-2)),
        [
          [constants.UPSTREAM_NAME, constants.QUARTZ_SOURCE_BRANCH],
          [constants.ORIGIN_NAME, constants.QUARTZ_SOURCE_BRANCH],
        ],
      )
      for (const pull of pulls) {
        assert.deepEqual(pull.args.slice(1, -2), [
          "--no-rebase",
          "--autostash",
          "-s",
          "recursive",
          "-X",
          "ours",
          "--no-edit",
        ])
      }

      const push = result.spawns.find((call) => call.cmd === "git" && call.args[0] === "push")
      assert.deepEqual(push.args, ["push", "-uf", constants.ORIGIN_NAME, "probe-branch"])
    })

    await rm(scratch, { recursive: true, force: true })
  })
})

async function withContentCache(run) {
  const cache = constants.contentCacheFolder
  const scratch = await mkdtemp(path.join(tmpdir(), "quartz-cache-backup-"))
  const backup = path.join(scratch, "backup")
  let hadCache = false
  try {
    await access(cache)
    hadCache = true
    await cp(cache, backup, {
      recursive: true,
      verbatimSymlinks: true,
      preserveTimestamps: true,
    })
    await rm(cache, { recursive: true, force: true })
  } catch (error) {
    if (error.code !== "ENOENT") throw error
  }
  await mkdir(path.dirname(cache), { recursive: true })
  try {
    await run()
  } finally {
    await rm(cache, { recursive: true, force: true })
    if (hadCache) {
      await mkdir(path.dirname(cache), { recursive: true })
      await cp(backup, cache, {
        recursive: true,
        verbatimSymlinks: true,
        preserveTimestamps: true,
      })
    }
    await rm(scratch, { recursive: true, force: true })
  }
}
