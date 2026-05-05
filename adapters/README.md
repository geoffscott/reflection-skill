# Adapters

The reflection skill is portable across runtime environments. Runtime-specific behavior is absorbed by adapters along four orthogonal axes. The conceptual core in `SKILL.md` and `references/` is identical regardless of where the skill runs.

## The Four Axes

### 1. Storage

Where entries, annotations, config, and metadata persist. The storage adapter implements:

- `read entry for date(date)`
- `append to entry for date(date, content)` — creates the entry with frontmatter on first call of the day
- `write entry for date(date, content)` — used only for migrations and historical imports
- `list entries in date range(start, end)`
- `read annotation for (date-range, lens)`
- `write annotation for (date-range, lens, content)`
- `read config()`
- `write config(config)`
- `read metadata()`
- `write metadata(metadata)`

Available storage adapters:

- [`local-fs`](storage/local-fs.md) — Files under a configured local directory
- [`google-drive`](storage/google-drive.md) — Files in a configured Drive folder, accessed via Drive connector tools
- [`github`](storage/github.md) — Files in a configured branch of a GitHub repository

### 2. Triggering

How the skill decides to engage on a given message.

Available triggering adapters:

- [`every-message-hook`](triggering/every-message-hook.md) — Runs evaluation logic on every inbound user message via a runtime hook
- [`description-based`](triggering/description-based.md) — Engages when the skill's description matches the message
- [`project-default`](triggering/project-default.md) — Engages by default within a scoped project context

### 3. Scheduling

Whether and how the skill runs without user prompting.

Available scheduling adapters:

- [`heartbeat`](scheduling/heartbeat.md) — Scheduled prompts at configured times
- [`user-initiated`](scheduling/user-initiated.md) — No scheduling; the user initiates everything explicitly

Every scheduled behavior has a documented user-initiated equivalent. `user-initiated` is the universal fallback and works in any runtime.

### 4. Cross-skill state

How shared resources (e.g. a global entities registry) are accessed.

Available cross-skill-state adapters:

- [`shared-file`](cross-skill-state/shared-file.md) — Reads/writes a shared file at a known path
- [`none`](cross-skill-state/none.md) — Operates without cross-skill state

## Composition

Adapters compose freely across axes, with one exception:

> Triggering adapters that depend on a runtime hook (`every-message-hook`) cannot be selected in runtimes that don't expose that hook.

Apart from that, any combination is valid. The skill core treats the four axes independently: changing the storage adapter does not affect triggering, and vice versa.

## Capability Matrix

| Adapter | Axis | Runtime requirement | Notes |
|---|---|---|---|
| `local-fs` | storage | Persistent local filesystem with write access | Original OpenClaw target |
| `google-drive` | storage | Drive connector tools available to the agent | Target for Anthropic skill runtime |
| `github` | storage | Git operations or GitHub API access | Versioned alternative |
| `every-message-hook` | triggering | Runtime exposes an inbound-message hook | OpenClaw `AGENTS.md` provides this |
| `description-based` | triggering | Runtime loads skills based on description matching | Universal — works in Anthropic, OpenClaw, and most skill-loading runtimes |
| `project-default` | triggering | Runtime supports scoped projects that bind a skill as default | Anthropic projects provide this |
| `heartbeat` | scheduling | Runtime exposes a scheduler | OpenClaw `HEARTBEAT.md` provides this |
| `user-initiated` | scheduling | None | Always available |
| `shared-file` | cross-skill-state | Filesystem access at a known path | Pairs naturally with `local-fs` storage |
| `none` | cross-skill-state | None | Always available |

### Validity by runtime

| Runtime | Storage | Triggering | Scheduling | Cross-skill state |
|---|---|---|---|---|
| OpenClaw | `local-fs`, `github` | any | `heartbeat`, `user-initiated` | `shared-file`, `none` |
| Anthropic (claude.ai, mobile, desktop) | `google-drive`, `github` | `description-based`, `project-default` | `user-initiated` | `none` |

`every-message-hook` is unavailable in any runtime that does not expose an inbound-message hook. `heartbeat` is unavailable in any runtime that does not expose a scheduler. When in doubt, fall back to `description-based` triggering and `user-initiated` scheduling — those work everywhere.

## Example Configurations

### OpenClaw deployment

Preserves the original behavior of the skill on the OpenClaw runtime.

- **Storage:** `local-fs` rooted at a directory like `~/.openclaw/reflection/`
- **Triggering:** `every-message-hook` installed in `AGENTS.md`
- **Scheduling:** `heartbeat` registered in `HEARTBEAT.md`
- **Cross-skill state:** `shared-file` pointing at the OpenClaw entities registry (e.g. `~/.openclaw/entities.json`)

End-to-end behavior:

1. **Capture moment.** A user message comes in. The `every-message-hook` triggering adapter routes the message to the skill on every turn. The skill applies the capture taxonomy. If journal-worthy, it cleans voice-to-text artifacts and calls `append to entry for date(today)`. The `local-fs` adapter creates `entries/YYYY-MM-DD.md` if needed (writing frontmatter), then appends `## HH:MM` + content. The skill responds silently.
2. **Daily reflection.** At the configured daily time, the `heartbeat` scheduler fires. The skill calls `read entry for date(today)`. If empty, it prompts the user. The user can also ask "what did I journal today?" at any time and get the same content read out.
3. **Weekly lens reflection.** At the configured weekly time, the `heartbeat` scheduler fires. The skill calls `list entries in date range(week-start, week-end)`, reads each entry, applies the user's declared lenses per `LENS_APPLICATION_ENGINE.md`, and calls `write annotation for (week, lens)`. The `local-fs` adapter writes `annotations/[lens]/YYYY-MM-DD.md`. The user can also ask "give me a Buddhist reading of this week" and get the same result.
4. **Longitudinal pattern query.** The user asks "what patterns do you see across the last three months?" The skill calls `list entries in date range(...)`, reads entries fresh, consults `shared-file` for entity resolution, and presents findings.

### Anthropic project deployment

Targets Anthropic's agent skill runtime (Claude in claude.ai, mobile, desktop) inside a scoped project.

- **Storage:** `google-drive` rooted at a Drive folder the user has shared with Claude
- **Triggering:** `project-default` — the skill is the project's default behavior, so any message in the project routes through the skill unless the user is clearly doing something else
- **Scheduling:** `user-initiated` — no scheduler is available, so the user invokes daily and weekly reflections explicitly
- **Cross-skill state:** `none`

End-to-end behavior:

1. **Capture moment.** The user sends a message in the project. `project-default` routes it to the skill. The skill applies the capture taxonomy. If journal-worthy, it cleans voice-to-text artifacts and calls `append to entry for date(today)`. The `google-drive` adapter looks for a file named `YYYY-MM-DD.md` in the configured `entries/` subfolder, creates it if needed, and appends the new section. The skill responds silently.
2. **Daily reflection.** No heartbeat. The user explicitly says "what did I journal today?" or "show me today's entry." The skill calls `read entry for date(today)` and presents it. If the user wants a daily prompt habit, they can set a calendar reminder; the skill itself does not schedule.
3. **Weekly lens reflection.** No heartbeat. On Sunday morning the user says "give me a Buddhist reading of this past week." The skill runs the full lens application: list entries, read fresh, apply lens, write annotation to Drive under `annotations/buddhism/2026-W14.md` (or equivalent). Same result a heartbeat-fired reflection would have produced.
4. **Longitudinal pattern query.** The user asks "what's been showing up in my entries this quarter?" The skill calls `list entries in date range(...)`, reads entries fresh from Drive, presents findings. No entity registry is consulted; the skill works with what's in the entries.
