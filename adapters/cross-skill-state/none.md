# Cross-Skill State Adapter: `none`

The skill operates without any cross-skill state. Lens application proceeds using only what is in the entries themselves.

## Runtime Requirements

None. Works in every runtime.

## Configuration

```json
{
  "cross_skill_state": {
    "adapter": "none"
  }
}
```

## Operations

| Operation | Behavior |
|---|---|
| `read entities()` | Returns an empty registry. |
| `resolve entity(name)` | Returns null. |
| `write entities(registry)` | No-op. |

The lens application engine treats every name in an entry as opaque. Patterns across entries are still detected via repeated mentions in the entry text itself; the engine just doesn't try to canonicalize them.

## Setup Steps

None. This adapter is the default when no shared-state mechanism is available.

## Failure Modes

- **Same person, multiple names** ("Kerry," "Kerry Smith," "K") will not be unified by the skill. The user can mention the correspondence in an entry and the lens engine will pick that up from text, but there is no programmatic resolution.
- **No cross-skill awareness.** Other skills that might benefit from the journal's view of an entity (or vice versa) cannot share state through this adapter. If that capability becomes important, switch to `shared-file` (or a future cross-skill-state adapter).

## Composition Notes

The default for the Anthropic deployment, where there is no shared filesystem and no other cross-skill primitive. Also a reasonable choice on OpenClaw for a deployment that prefers minimal coupling between skills. Pairs with any storage, triggering, or scheduling adapter.
