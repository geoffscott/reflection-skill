# Scheduling Adapter: `user-initiated`

The skill never runs without a user message. Every behavior that would fire automatically under `heartbeat` has a user-initiated equivalent, and those equivalents are the only way the skill engages here.

## Runtime Requirements

None. Works in every runtime, including those without schedulers (Anthropic's claude.ai, mobile, desktop).

This is the universal fallback. It should be the default choice when in doubt.

## Configuration

No configuration needed.

```json
{
  "scheduling": {
    "adapter": "user-initiated"
  }
}
```

The `heartbeat_schedule` field in skill config is ignored under this adapter.

## Operations

The scheduling adapter exposes user-initiated equivalents of every workflow that `heartbeat` would have scheduled.

| Workflow | How the user invokes |
|---|---|
| `daily check` | "What did I journal today?" / "Show me today's entry" / "Did I capture anything today?" |
| `weekly lens reflection` | "Give me a Buddhist reading of this week" / "Apply Gnosticism to last week" / "Reflect on this past week" |
| `longitudinal pattern recognition` | "What patterns do you see across the last three months?" / "How has my relationship with X evolved?" |

Each workflow produces the same result a fired heartbeat would have produced. The lens application engine reads entries fresh from storage; nothing depends on a prior heartbeat having run.

## Setup Steps

1. During onboarding, tell the user how to invoke each workflow. Use plain language, not jargon.
2. If they want a daily-prompt habit, suggest a calendar reminder or a habit tracker external to the skill — the skill itself does not schedule.
3. Confirm: "Whenever you want a reflection, just ask. I'll read your entries fresh and apply the lens you specify."

## Failure Modes

- **User forgets** the prompts that invoke workflows. Mitigate by keeping the description block in `SKILL.md` rich with example phrases, and by reminding the user during onboarding.
- **User expects automatic prompts** because they're used to a heartbeat-equipped runtime. Set expectations during onboarding: "in this runtime, I won't prompt you on a schedule — you ask, I respond."
- **Drift in user habits.** Without a heartbeat, a user can go weeks without reflecting. The skill cannot fix this; it can only be ready when asked.

## Composition Notes

Pairs with any storage and any triggering adapter. The default scheduling choice for the Anthropic deployment. Also a reasonable choice on OpenClaw if the user prefers explicit invocation over scheduled prompts.
