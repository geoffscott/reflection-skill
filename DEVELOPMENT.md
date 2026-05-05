# Development Guide

This file is for developers building and iterating on the skill. The user-facing definition lives in `SKILL.md`; the conceptual core under `references/`; runtime adapters under `adapters/`.

## Architecture in One Page

The skill is a markdown-based agent skill. There is no runtime code in the core — the model reads `SKILL.md`, follows the instructions there, and uses adapter-defined operations to talk to the surrounding runtime.

Four adapter axes:

1. **Storage** — where entries, annotations, config, metadata live
2. **Triggering** — how the skill decides to engage on a given message
3. **Scheduling** — whether and how the skill runs without user prompting
4. **Cross-skill state** — how shared resources (e.g. an entities registry) are accessed

Adapters compose freely. The only constraint: triggering adapters that depend on a runtime hook (`every-message-hook`) cannot be selected in runtimes that don't expose that hook. See [`adapters/README.md`](adapters/README.md) for the full capability matrix.

## Where to Edit What

| If you're changing... | Edit... |
|---|---|
| What the skill captures (taxonomy, voice-to-text rules) | `SKILL.md` |
| Entry format conventions | `SKILL.md` |
| How a lens interprets entries | `references/LENS_APPLICATION_ENGINE.md` |
| A specific lens's framework or inference rules | `references/lenses/[name].md` |
| The lens taxonomy or universal questions | `references/TAXONOMY.md`, `references/LENSES.md` |
| A storage backend's behavior or setup | `adapters/storage/[name].md` |
| How the skill engages on messages in a runtime | `adapters/triggering/[name].md` |
| Scheduled behaviors | `adapters/scheduling/[name].md` |
| Shared cross-skill state | `adapters/cross-skill-state/[name].md` |
| The capability matrix or example configurations | `adapters/README.md` |

## Adding a New Adapter

Adapters are markdown files describing behavior — not implementations. To add a new adapter:

1. Create `adapters/[axis]/[name].md` with these sections:
   - **Runtime Requirements** — what the runtime must provide
   - **Configuration** — what the user/deployment must set
   - **Operations** — how each core operation is implemented for this backend
   - **Setup Steps** — first-run flow
   - **Failure Modes** — concrete failure cases and how to handle them
   - **Composition Notes** — which other adapters pair well, which constraints apply
2. Update `adapters/README.md`:
   - Add the adapter to the axis list
   - Add a row to the capability matrix
   - Update the validity-by-runtime table if applicable
3. Verify by walking through all four scenarios (capture, daily, weekly, longitudinal) end-to-end with the new adapter selected.

Keep adapters concrete. Each one targets a real backend with materially different operations — don't add an adapter for a hypothetical case.

## Adding a New Lens

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Lens contributions follow a research → draft → review → merge process. The lens file template is documented there and in `references/LENSES.md`.

## Testing the Skill

The skill is markdown, so "testing" means walking through scenarios mentally with the configured adapters and confirming the instructions produce a coherent sequence.

Four scenarios to walk through for any deployment:

1. **Capture moment.** A user message comes in. Does the active triggering adapter route it to the skill? If yes, does the capture taxonomy decide correctly? Does the storage adapter handle the append?
2. **Daily reflection.** Either via heartbeat or user-initiated. Does the storage adapter surface today's entry? Does the response handle the empty-day and has-entries cases?
3. **Weekly lens reflection.** Lens loads, entries enumerate and read fresh, lens application produces an annotation, storage writes it. Does the user get the same result they'd get from a fired heartbeat?
4. **Longitudinal pattern query.** Read entries across a longer range, identify recurring themes (with or without cross-skill entity resolution), present findings.

If any step requires the model to do something not described in the adapters or the core, that's a gap to fix.

For trigger-routing tests under `description-based`, see `test/trigger-fixtures.md`.

## Migration & Imports

Each storage adapter handles imports differently. When importing an existing journal:

- For `local-fs`: write a one-time shell or Python script that reads the source files, parses dates, and calls the adapter's `write entry for date` for each. Live outside the skill repo or in a per-adapter migration helper.
- For `google-drive`: use a script that reads source files locally and uploads via the Drive API or connector tools.
- For `github`: a one-time series of commits to the configured branch.

Don't try to write a generic import script that handles all backends. The shape of source data and the failure modes differ enough that adapter-specific helpers are clearer.

For historical context: the original OpenClaw deployment imported 154 entries from an Obsidian vault using shell scripts. Those entries use an older template format (`# Section` headers like Gratitudes, Meditations) and remain as-is; new auto-captured entries use the timestamped format documented in `SKILL.md`.

## Releasing

The repo uses two long-running branches:

- `main` — Stable. Always deployable.
- `develop` — Active development.

Feature branches off `develop`, merged via PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.
