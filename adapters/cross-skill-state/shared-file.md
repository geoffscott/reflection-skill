# Cross-Skill State Adapter: `shared-file`

Reads (and optionally writes) a shared file at a known path that other skills also use. The most common case is an entities registry — known people, organizations, projects — that multiple skills consult to keep references consistent.

## Runtime Requirements

- Filesystem access (or equivalent stable-path access via a connector) at a path other skills can also reach
- A coordinated convention with those other skills about the file's format and update protocol

OpenClaw uses `~/.openclaw/entities.json` as the canonical entities registry; this adapter targets that pattern.

## Configuration

```json
{
  "cross_skill_state": {
    "adapter": "shared-file",
    "entities_path": "~/.openclaw/entities.json"
  }
}
```

Other shared-file mappings can be added later as needed (e.g. a shared signals file, a global config). For now, the registry use case is the only one in scope.

## Operations

| Operation | Behavior |
|---|---|
| `read entities()` | Read and parse the entities file. Return an empty registry if missing. |
| `resolve entity(name)` | Look up `name` in the registry; return canonical entity record or null. |
| `write entities(registry)` | Write the updated registry. Optional — many deployments treat the file as read-only from the reflection skill's perspective. |

The lens application engine consults `resolve entity` when generating annotations so that "Kerry" in one entry resolves to the same person referenced elsewhere.

## Setup Steps

1. During onboarding, check whether the configured path exists.
2. If yes, record the path in config so the lens application engine can use it.
3. If no, ask the user whether they want to point at a different path or proceed without cross-skill state. If the latter, suggest switching to the `none` adapter.

## Failure Modes

- **Stale data** if other skills update the file but the reflection skill caches it across calls. Re-read on each lens application to avoid this.
- **Missing file** if the cross-skill ecosystem hasn't set it up yet. Treat as an empty registry; do not crash.
- **Format drift** if other skills evolve the schema. Be defensive when parsing; ignore unknown fields.
- **Concurrent writes** from multiple skills. If this adapter is configured for write access, use atomic-rename or filesystem locks; if read-only, the issue doesn't arise.
- **Path tilde-expansion** must happen consistently. Use the same convention as the storage adapter.

## Composition Notes

Pairs naturally with `local-fs` storage on OpenClaw, where multiple skills share a common runtime data directory. Could also be implemented over `google-drive` or another connector, but only if the connector exposes a stable path that all participating skills agree on.
