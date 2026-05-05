# Scheduling Adapter: `heartbeat`

Runs the skill's scheduled behaviors at configured times via a runtime scheduler. Daily checks and weekly lens reflections fire automatically.

## Runtime Requirements

- The runtime exposes a scheduler that can fire prompts or callbacks at cron-like intervals
- The scheduler can pass enough context to the skill that it knows which scheduled behavior is firing

OpenClaw provides this via `HEARTBEAT.md`: scheduled blocks defined there are evaluated by the runtime at the configured times.

This adapter is **not available** in runtimes without a scheduler (e.g. Anthropic's claude.ai, mobile, desktop). Those deployments must use `user-initiated` instead — every scheduled behavior has a documented user-initiated equivalent.

## Configuration

Schedule lives in the skill's config (written by the storage adapter):

```json
{
  "scheduling": {
    "adapter": "heartbeat",
    "schedule": {
      "daily_check": "09:00",
      "weekly_reflection": "sunday 08:00"
    }
  },
  "timezone": "America/New_York"
}
```

The deployment is responsible for translating this into the runtime's scheduler syntax.

For OpenClaw, the install location is `HEARTBEAT.md` in the workspace.

```markdown
## Reflection Skill

### Daily Journal Check (09:00 [timezone])
- Call the reflection skill's `daily check` workflow.
- If today's entry is empty, prompt: "Nothing captured today. Anything on your mind worth noting?"
- If it has entries, stay silent.

### Weekly Reflection (Sunday 08:00 [timezone])
- Call the reflection skill's `weekly lens reflection` workflow.
- Offer: "Want a lens reflection on this week? I can apply [declared_lenses]."
- If accepted, run lens application and present a summary.
```

## Operations

The scheduling adapter triggers the skill's named workflows:

| Workflow | When it fires |
|---|---|
| `daily check` | At the configured daily time |
| `weekly lens reflection` | At the configured weekly time |

Each workflow has the same definition under `heartbeat` and `user-initiated` — the only difference is who initiates.

## Setup Steps

1. During onboarding, ask the user for their preferred daily and weekly times (and timezone).
2. Persist the schedule in config via the storage adapter.
3. Install the heartbeat block at the runtime's scheduler location (e.g. `HEARTBEAT.md`).
4. Verify by either waiting for the next scheduled fire or invoking the equivalent user-initiated workflow and confirming the same result.

## Uninstall

Remove the heartbeat block from the scheduler location. The skill remains installed; scheduling falls back to user-initiated.

## Failure Modes

- **Missed fires** if the runtime is offline at the scheduled time. The skill should not assume the heartbeat fired; on next interaction, it can detect a gap and offer the missed prompt if still relevant.
- **Timezone drift** if the user travels or DST changes. Re-prompt for timezone during onboarding-like flows; consider storing UTC + offset rather than a region name if precision matters.
- **Schedule overload** if the user configures too many heartbeats. Keep the default to two (daily, weekly); discourage more without a clear reason.
- **Heartbeat removed** by other tools that manage the same file. Document the block clearly so other tools/maintainers see why it's there.

## Composition Notes

Pairs with `every-message-hook` triggering on OpenClaw to give the full original behavior: capture on every message, scheduled prompts on a cadence. Pairs equally well with `description-based` triggering — in that combination, the skill is conservative about capture but proactive about scheduled reflections.
