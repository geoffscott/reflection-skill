# Storage Adapter: `github`

Persists entries, annotations, config, and metadata as files in a configured branch of a GitHub repository, with each write becoming a commit.

## Runtime Requirements

- Either local Git operations (`git` CLI with credentials configured) or GitHub API access (a token with read/write to the target repo, or an MCP server like `mcp__github__create_or_update_file`)
- A repository the user owns (or has write access to) and a designated branch

This adapter is the right choice when the user wants a versioned, auditable journal — entries become commits, annotations are tracked, and the full history is preserved.

## Configuration

```json
{
  "storage": {
    "adapter": "github",
    "owner": "geoffscott",
    "repo": "my-reflections",
    "branch": "main",
    "path_prefix": ""
  }
}
```

`path_prefix` is optional; useful when the journal lives in a subdirectory of a larger repo.

Layout:

```
[path_prefix]/
├── config.json
├── metadata.json
├── entries/
│   └── YYYY-MM-DD.md
└── annotations/
    └── [lens-name]/
        └── YYYY-MM-DD.md
```

## Operations

| Operation | Implementation |
|---|---|
| `read entry for date(date)` | Fetch `[path_prefix]/entries/YYYY-MM-DD.md` from the configured branch. Return `null` on 404. |
| `append to entry for date(date, content)` | Fetch existing content (or treat as empty with frontmatter), append the new `## HH:MM` section, commit the updated file. Commit message: `journal: capture YYYY-MM-DD HH:MM`. |
| `write entry for date(date, content)` | Commit the file with message `journal: import YYYY-MM-DD` (or similar). |
| `list entries in date range(start, end)` | List the contents of `[path_prefix]/entries/`, filter to filenames matching the range. |
| `read annotation for (date-range, lens)` | Fetch `[path_prefix]/annotations/[lens]/[range-key].md`. |
| `write annotation for (date-range, lens, content)` | Commit the file. Commit message: `lens: [name] reflection on [range]`. |
| `read config()` / `write config(c)` | `[path_prefix]/config.json`. |
| `read metadata()` / `write metadata(m)` | `[path_prefix]/metadata.json`. |

## Setup Steps

On first run when `read config()` returns null:

1. Confirm read and write access by reading the branch HEAD and committing a `.gitkeep` to `entries/` and `annotations/`.
2. If the repo doesn't exist yet, ask the user to create it (do not auto-create — repo creation is a meaningful side effect).
3. Run the onboarding conversation defined in `SKILL.md`.
4. Commit `config.json` to the branch.

## Failure Modes

- **Auth failure.** Surface immediately and ask the user to refresh credentials. Do not retry silently.
- **Branch protection / required reviews.** If the configured branch requires PR review, direct commits will fail. Ask the user to either pick an unprotected branch or set up auto-merge for the journal commit pattern.
- **Merge conflicts** if another writer commits between read and write. Detect via base-SHA mismatch, refetch, retry once. If conflict persists, surface it.
- **Rate limiting.** GitHub API limits apply. Back off and retry once; tell the user if capture failed.
- **Large repo trees** can make `list` slow. Use directory-listing endpoints (`get_file_contents` on a folder), not full trees.
- **Commit noise.** Every capture is a commit. Some users will love this (auditable), some will find it noisy. Document the tradeoff during onboarding.

## Notes

Because every write is a commit, the entire history is recoverable. A user can `git log` their `entries/` directory and see exactly when each moment was captured. This is a feature, not a side effect.
