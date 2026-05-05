# Storage Adapter: `local-fs`

Persists entries, annotations, config, and metadata as files under a configured local directory.

## Runtime Requirements

- A persistent local filesystem with read/write access from the agent process
- Stable path conventions across sessions (the directory is not ephemeral)

This adapter is the natural choice for runtimes like OpenClaw that give the agent durable local storage.

## Configuration

A single root directory. Everything else is derived from it.

```json
{
  "storage": {
    "adapter": "local-fs",
    "root": "~/.openclaw/reflection"
  }
}
```

Layout under `root/`:

```
root/
├── config.json
├── metadata.json
├── entries/
│   └── YYYY-MM-DD.md
└── annotations/
    └── [lens-name]/
        └── YYYY-MM-DD.md
```

The root path can be tilde-expanded or absolute. The adapter creates `entries/` and `annotations/` on first use.

## Operations

| Operation | Implementation |
|---|---|
| `read entry for date(date)` | Read `root/entries/YYYY-MM-DD.md`. Return `null` if missing. |
| `append to entry for date(date, content)` | If file is missing, create it with `---\ndate: YYYY-MM-DD\n---\n\n` frontmatter. Append a blank line, then `## HH:MM`, then a blank line, then the content, then a trailing newline. |
| `write entry for date(date, content)` | Overwrite `root/entries/YYYY-MM-DD.md`. Used only for migrations. |
| `list entries in date range(start, end)` | List files in `root/entries/` matching `YYYY-MM-DD.md`, filter to the inclusive range, return sorted dates. |
| `read annotation for (date-range, lens)` | Read `root/annotations/[lens]/[range-key].md`. The range key is the start date for single-day reflections, an ISO week label like `2026-W14.md` for weekly, or the start date for arbitrary ranges. |
| `write annotation for (date-range, lens, content)` | Write to the same path. Create parent directory if missing. |
| `read config()` / `write config(c)` | `root/config.json`. |
| `read metadata()` / `write metadata(m)` | `root/metadata.json`. |

## Setup Steps

On first run when `read config()` returns null:

1. Ensure `root/` and `root/entries/` and `root/annotations/` exist
2. Run the onboarding conversation defined in `SKILL.md`
3. `write config(...)` with the user's responses

## Failure Modes

- **Permission denied** writing into `root/`. Surface a clear error and ask the user for a writable location.
- **Disk full.** Fail loudly during capture; do not silently drop the entry.
- **Concurrent writes** from multiple agent processes (rare). Last-writer-wins; not a concern in single-agent OpenClaw deployments.
- **Filesystem case sensitivity differences** between macOS and Linux. Always use exact-case filenames `YYYY-MM-DD.md`.
- **User moves or renames the root directory** out from under the skill. The adapter cannot recover automatically; ask the user to update config.

## Migration Helper

For deployments that have an existing journal in another format, write a one-time migration script that reads source files, normalizes date and content, and calls `write entry for date` for each. Migration scripts are deployment-specific and live outside the skill repo.
