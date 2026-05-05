# Triggering Adapter: `every-message-hook`

Runs the skill's capture-evaluation logic on every inbound user message via a runtime hook. The skill sees every message, applies the capture taxonomy, and acts silently when content is journal-worthy.

## Runtime Requirements

- The runtime must expose an inbound-message hook — a mechanism that runs custom logic on every user turn before normal agent processing
- The hook must be able to read the message, perform side effects (writing to storage), and continue normal processing without prompting the user

OpenClaw provides this via `AGENTS.md`: instructions appended there are part of every turn's system context.

This adapter is **not available** in runtimes that lack such a hook (e.g. Anthropic's skill runtime, where skills are loaded based on description matching rather than running on every message). If the runtime cannot guarantee the hook fires on every message, choose `description-based` or `project-default` instead.

## Configuration

The hook content is injected into the runtime's per-turn context. The skill provides the hook text; the deployment is responsible for installing it.

For OpenClaw, the install location is `AGENTS.md` in the workspace.

```markdown
## Reflection Skill: Auto-Capture

On every inbound user message, silently evaluate whether it's journal-worthy:
- Emotional processing, self-reflection, insights, pattern recognition
- Relationship reflections, gratitude, spiritual/contemplative content
- Life decisions, values-level thinking, dreams, meditations
- Creative ideas with personal meaning

If journal-worthy: clean voice-to-text artifacts and append to today's entry
via the reflection skill's storage adapter (do not name a specific path here —
the storage adapter resolves it). Do not respond about the capture. Continue
normal processing.

Skip: task management, debugging, scheduling, logistics, commands.
```

## Operations

The triggering adapter exposes one operation:

| Operation | Behavior |
|---|---|
| `should engage(message) → bool` | True for every message. The capture taxonomy in `SKILL.md` decides whether to actually capture; the hook only guarantees the skill *sees* the message. |

## Setup Steps

1. Locate the runtime's hook installation point. For OpenClaw, this is `AGENTS.md` at the workspace root.
2. Append the hook block above (or refer to `SKILL.md` from the hook).
3. Verify the hook is loaded by sending a journal-worthy test message and confirming an entry is written.

## Uninstall

Remove the hook block from the runtime's hook location. The skill remains installed but no longer engages on every message — it falls back to whatever other triggering adapter is configured (typically `description-based`).

## Failure Modes

- **Hook removed or overwritten** by other tools that manage the same file. Document the hook so other tools/maintainers can see why it's there.
- **Hook truncation** if the install location has a size limit. Keep the hook block short; reference `SKILL.md` for details rather than duplicating.
- **Conflicting hooks** from other skills that also want to run on every message. Order matters; the reflection hook should not block or short-circuit other hooks.
- **Hook silently disabled** by a runtime upgrade. Periodically verify by checking that today's entry exists for days where the user clearly journaled.

## Composition Notes

Pairs naturally with `local-fs` storage and `heartbeat` scheduling on OpenClaw. Can also pair with `github` storage if commits-per-message is acceptable. Cannot be used in runtimes without an inbound-message hook.
