# Triggering Adapter: `description-based`

Engages the skill when the runtime determines that the message matches the skill's `description` frontmatter. The runtime decides; the skill provides a description rich enough to match the right messages without false positives.

## Runtime Requirements

- The runtime loads skills based on description matching (most modern skill-loading runtimes, including Anthropic's, OpenClaw's skill loader, and others)
- The runtime presents the skill's description to a routing layer that picks which skill applies to a given message

This adapter works in any runtime that loads skills this way. It is the universal fallback.

## Configuration

No deployment-specific configuration. The skill's `description` block in `SKILL.md` does the work. The current description matches messages like:

- Explicit reflection requests ("give me a Buddhist reading," "review my entries")
- Explicit capture requests ("journal this," "capture that")
- Lens-specific triggers ("Buddhism lens on this week," "apply Stoicism")
- Onboarding ("set up my journal," "configure reflection")

It does not match:

- Task management ("remind me to journal tonight" — that's the completion skill)
- Conversational sharing without explicit save intent ("I'm feeling frustrated" alone)

## Operations

| Operation | Behavior |
|---|---|
| `should engage(message) → bool` | Determined by the runtime's skill router based on the description. The skill itself sees only messages the router has already routed to it. |

## Setup Steps

1. Confirm the runtime supports description-based skill loading.
2. Install the skill (deployment-specific — copy the repo into the runtime's skill directory, register it via the runtime's tooling, etc.).
3. Verify by sending a known-trigger message ("give me a Buddhist reading of this week") and confirming the skill engages.

## Failure Modes

- **False positives.** A message about "task management" containing the word "journal" might over-match. The description has been tuned to avoid the obvious cases; new false positives should be addressed by tightening the description, not by adding logic in the skill body.
- **False negatives.** A clearly journal-worthy message that doesn't match the description gets routed elsewhere or to no skill. The user can recover by being more explicit ("capture this:") — the skill is conservative by design under this adapter, since it can't see every message.
- **Routing layer changes.** Runtime upgrades may alter how descriptions are matched. Keep the description pattern-rich and concrete; avoid relying on subtle wording.

## Conservative Behavior

Under `description-based` triggering without project scoping, the skill cannot assume capture is the default — it only sees messages the router selected. Apply the capture taxonomy more conservatively:

- Capture when the user explicitly invokes the skill or shares something unmistakably journal-worthy
- Otherwise treat the engagement as a request for reflection workflows (lens application, review, longitudinal patterns)

If the user wants every-message capture, they need either `every-message-hook` (where supported) or `project-default` (where supported).

## Composition Notes

Pairs with any storage adapter. Pairs naturally with `user-initiated` scheduling. Compatible with both `shared-file` and `none` cross-skill state. The most portable triggering adapter — works wherever skills load by description.
