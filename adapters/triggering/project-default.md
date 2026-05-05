# Triggering Adapter: `project-default`

Engages the skill by default within a scoped project context. Inside the project, every message routes through the skill unless the user is clearly doing something else.

## Runtime Requirements

- The runtime supports scoped projects that bind a default skill
- The user can create a project, attach this skill to it, and have all messages in that project flow through the skill

Anthropic's project feature provides this. Other runtimes with similar scoping primitives can use this adapter.

## Configuration

Configuration is owned by the runtime, not the skill — the user creates a project in the runtime's UI and attaches the reflection skill as the project's default. The skill itself just needs to know it's running under `project-default` so it applies the correct capture defaults.

```json
{
  "triggering": {
    "adapter": "project-default"
  }
}
```

## Operations

| Operation | Behavior |
|---|---|
| `should engage(message) → bool` | True for every message in the project. Inside the project the skill assumes engagement. |

## Setup Steps

1. The user creates a project in the runtime (e.g. a Claude project) and attaches the reflection skill.
2. The user is told that within this project, the skill assumes capture is the default and will silently file journal-worthy moments. Outside the project, the skill is not invoked at all.
3. The skill writes config (via the storage adapter) so it knows it's running in project-default mode.

## Capture Defaults

Under `project-default`, treat capture as the default behavior. From `SKILL.md`:

> Only stop and ask the user when the content is ambiguous or when they're clearly doing something else (asking for a lens reflection, reviewing past entries, asking a meta question about the skill).

This mirrors the behavior of `every-message-hook` semantically, even though the underlying mechanism is different (project scoping vs. runtime hook). The user's experience should be: "in this project, my conversations get captured automatically."

## Failure Modes

- **Project leakage.** If the user accidentally types in the wrong project, the skill captures content that doesn't belong. Tell the user during onboarding which project the skill is bound to and how to tell.
- **Project ambiguity.** If multiple projects are configured for the same user, the user may not realize which project is the journal one. Encourage naming the project clearly (e.g. "Reflection Journal").
- **Project deletion** removes the skill's runtime context but does not delete entries (those are in the storage adapter, separately). The user can re-attach the skill to a new project pointing at the same storage.
- **Cross-project entity confusion.** The skill cannot reliably know the same person is referenced across projects unless cross-skill state is configured.

## Composition Notes

Pairs naturally with `google-drive` storage and `user-initiated` scheduling for the Anthropic deployment. Pairs with `none` cross-skill state by default; if the runtime gains a richer cross-skill primitive, that adapter can replace it without affecting the rest of the skill.
