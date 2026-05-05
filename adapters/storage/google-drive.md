# Storage Adapter: `google-drive`

Persists entries, annotations, config, and metadata as files in a Google Drive folder, accessed via Drive connector tools available to the agent.

## Runtime Requirements

- The agent has access to Drive connector tools that can list, read, create, and update files (e.g. `search_files`, `read_file_content`, `create_file`, `copy_file`, `get_file_metadata`)
- The user has shared a Drive folder with the connector and granted write access
- The connector exposes file metadata sufficient to identify files by name within a folder

This adapter is the primary target for Anthropic's agent skill runtime, which lacks persistent local filesystem access but has Drive connectors.

## Configuration

```json
{
  "storage": {
    "adapter": "google-drive",
    "root_folder_id": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
    "root_folder_name": "Reflection Journal"
  }
}
```

Either `root_folder_id` (preferred) or `root_folder_name` (fallback for resolving by search) is required. The adapter uses the folder ID once known and caches it in metadata.

Layout under the root folder:

```
[root folder]/
├── config.json
├── metadata.json
├── entries/
│   └── YYYY-MM-DD.md
└── annotations/
    └── [lens-name]/
        └── YYYY-MM-DD.md (or weekly key)
```

Subfolders are real Drive subfolders, not name prefixes.

## Operations

| Operation | Implementation |
|---|---|
| `read entry for date(date)` | Search the `entries/` subfolder for a file named `YYYY-MM-DD.md`. Read its content. Return `null` if not found. |
| `append to entry for date(date, content)` | Read existing content (or treat as empty). If empty, prepend `---\ndate: YYYY-MM-DD\n---\n\n`. Append `## HH:MM` section. Write the full updated content back as a new revision. Drive does not support true append; every append is a read-modify-write. |
| `write entry for date(date, content)` | Create or overwrite `YYYY-MM-DD.md` in the `entries/` folder. |
| `list entries in date range(start, end)` | List files in the `entries/` subfolder, filter names matching `YYYY-MM-DD.md` within range, return sorted dates. |
| `read annotation for (date-range, lens)` | Read from `annotations/[lens]/[range-key].md`. |
| `write annotation for (date-range, lens, content)` | Create the lens subfolder if needed. Write the file. |
| `read config()` / `write config(c)` | `config.json` at the root folder. |
| `read metadata()` / `write metadata(m)` | `metadata.json` at the root folder. |

## Setup Steps

On first run when `read config()` returns null:

1. Confirm the Drive folder is reachable. If only `root_folder_name` is configured, search for it and resolve to an ID; if multiple match, ask the user to disambiguate.
2. Verify write access by creating and deleting a tiny test file. If write fails, instruct the user to share the folder with edit access.
3. Create `entries/` and `annotations/` subfolders if missing.
4. Run the onboarding conversation defined in `SKILL.md`.
5. `write config(...)` with the user's responses, including the resolved folder ID.

## Failure Modes

- **Auth expiry / connector revoked.** Surface clearly: "I can't reach your Drive folder. Reconnect Drive and try again." Do not retry silently.
- **Rate limiting.** Drive APIs throttle. Back off and retry once; if still rate-limited, tell the user the capture failed and suggest trying again in a moment. Do not lose the content — keep it in conversation memory until written.
- **File-name collisions** if the user manually creates entries with the same name. Read the existing file and treat it as the current entry; append normally.
- **Read-modify-write race.** Two captures within seconds can clobber each other. Mitigate by serializing append operations within a session and reading immediately before writing.
- **Folder moved or unshared.** The cached folder ID becomes invalid. Detect on first failed read; ask the user to reconfigure.
- **Eventual consistency.** A just-written file may not appear in a `list` call for a few seconds. When listing for date ranges that include today, also explicitly attempt to read today's file by name.

## Notes

Drive does not support true append, so capture costs one read plus one write per moment. This is fine for typical journaling volumes (a handful of captures per day). If a deployment expects much higher volumes, prefer `local-fs` or `github`.
