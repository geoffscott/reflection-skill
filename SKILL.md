---
name: reflection
description: >
  Journal and reflect on stream of consciousness through interpretive lenses.
  Use when the user says things like "capture this," "journal this," "I want to
  reflect on," "give me a Buddhist reading," "apply the Gnosticism lens," "what
  did I journal this week," "review my entries," "what patterns do you see,"
  "reflect on February," or any reference to journaling, lenses, reflections,
  reviewing past entries, or applying belief system frameworks to life experience.
  Also trigger when the user explicitly shares something contemplative, spiritual,
  or emotionally significant and asks to save, capture, or remember it. Trigger
  phrases include: "lens," "reflection," "journal," "entry," "annotate,"
  "Buddhism," "Gnosticism," "Stoicism," "what did I write," "capture that."
---

# Reflection Skill

Capture stream of consciousness throughout the day. Reflect on it through interpretive lenses without modifying the raw entries.

## Architecture

The skill has a runtime-agnostic conceptual core (this file plus everything under `references/`) and a set of pluggable adapters (everything under `adapters/`). The core describes *what* the skill does. Adapters describe *how* it talks to the surrounding runtime.

Adapters compose along four axes:

- **Storage** — where entries, annotations, config, and metadata persist
- **Triggering** — how the skill decides to engage on a given message
- **Scheduling** — whether and how the skill runs without user prompting
- **Cross-skill state** — how shared resources (e.g. a global entities registry) are accessed

Every operation below is described in adapter-neutral terms. The active deployment selects one adapter per axis. See `adapters/README.md` for the capability matrix and concrete deployment examples.

## Capture Taxonomy

When the triggering adapter routes a message to this skill, evaluate whether the message is journal-worthy.

**Capture if the message contains:**
- Emotional processing or self-reflection
- Insights, realizations, or pattern recognition
- Relationship reflections (people, dynamics, feelings)
- Gratitude or spiritual/contemplative content
- Life decisions or values-level thinking
- Dreams or meditations
- Creative ideas with personal meaning

**Skip if the message is:**
- Task management ("remind me to," "add to my list")
- Technical debugging or code discussion
- Scheduling or logistics
- Routine operational updates
- Direct commands to the agent

### Capture Defaults by Triggering Adapter

- **`every-message-hook`** or **`project-default`** — assume capture is the default. Only stop and ask the user when the content is ambiguous or when they're clearly doing something else (asking for a lens reflection, reviewing past entries, asking a meta question about the skill).
- **`description-based`** without project scoping — be more conservative. Only capture when the user explicitly invokes the skill or shares something unmistakably journal-worthy.

## Voice-to-Text Cleaning

When capturing, clean the raw message minimally:

1. Fix obvious transcription artifacts (spelling, punctuation, dropped words)
2. Repair words that were clearly misheard
3. Preserve sentence structure, phrasing, and idioms — even when imperfect
4. Do **not** synthesize, summarize, paraphrase, or significantly alter meaning
5. Do **not** add interpretation, framing, or context the user didn't say

Cleaning is a transcription pass, not an editorial pass. The voice on the page should be the user's voice.

## Entry Format

Each calendar day has one entry file. The storage adapter exposes it as the entry for date `YYYY-MM-DD`.

```markdown
---
date: 2026-03-12
---

## 09:15

I'm grateful for the clarity this morning. Mind-body-spirit
circuit feels complete.

## 11:42

Something Kerry said about the attestation layer is sticking
with me. The accountability piece isn't just legal — it's care
made visible.

## 15:30

Frustrated with Bashan. I'm stuck and it's not in my control.
Noticing the urge to push harder vs. just being honest about
the powerlessness.
```

**Rules:**
- One entry file per calendar day
- `## HH:MM` timestamp headers in chronological order
- Frontmatter (`date: YYYY-MM-DD`) on the first capture of the day; subsequent captures append
- Entries are immutable once written — never modify past entries
- Use the user's local timezone for `HH:MM` headers (configured during onboarding); the date in the frontmatter is the user's local date

### Writing a Captured Moment

When a capture is triggered:

1. Ask the storage adapter whether an entry exists for today's date
2. If not, create it with frontmatter `date: YYYY-MM-DD`
3. Append a `## HH:MM` header followed by the cleaned content
4. Ensure a blank line before and after the new section
5. Do not respond about the capture — continue normal processing silently

The `read entry for date` and `append to entry for date` operations are provided by the storage adapter. The skill never names a path, URL, or file ID directly.

## Lens Application

When the user requests a lens reflection (e.g. "give me a Buddhist reading of this week"):

1. Load the requested lens definition from `references/lenses/[name].md` in the skill repo
2. Use the storage adapter's `list entries in date range` to enumerate entries for the requested period
3. For each entry in range, use `read entry for date` to load it fresh
4. Apply the lens following `references/LENS_APPLICATION_ENGINE.md`
5. Use the storage adapter's `write annotation for (date-range, lens)` to persist the result
6. Present a summary; offer the full annotation if the user wants it

Lenses interpret what's written in the entry files, not what the model remembers. **Read entries fresh from storage every time.** Do not synthesize from conversational memory or context impressions. The immutability of entries and the freshness of reads together preserve the separation between source and interpretation.

## Reflection Workflows

These are the workflows the skill supports. Each has a scheduled form (when a `heartbeat` scheduler is configured) and a user-initiated form (always available, regardless of scheduler).

### Daily Check

- **Scheduled (heartbeat):** at the configured daily time, ask the storage adapter whether today's entry exists. If empty, prompt the user: "Nothing captured today. Anything on your mind worth noting?" If it has entries, stay silent.
- **User-initiated:** the user asks "what did I journal today?" or similar. Read today's entry and present it.

### Weekly Lens Reflection

- **Scheduled (heartbeat):** at the configured weekly time, offer a lens reflection on the past week's entries using the user's declared lenses.
- **User-initiated:** the user asks "give me a Buddhist reading of this week" or "apply Gnosticism to last week." Run the lens application on the requested date range.

### Longitudinal Pattern Recognition

- **User-initiated only.** The user asks "what patterns do you see across the last three months?" or "how has my relationship with X evolved?" Read the relevant date range, identify recurring themes across entries (and any existing annotations), present findings.

Every scheduled behavior has a user-initiated equivalent. A user who comes to the skill on a Sunday morning and asks for a weekly reflection should get the same result a fired heartbeat would have produced. Scheduling is an enhancement, not a requirement.

## Available Lenses

Lens definitions live in the skill repo under `references/lenses/`:

- **Buddhism** — Craving, impermanence, presence, reactivity patterns
- **Gnosticism** — Sophia/archontic choices, false authority, awakening moments

See `references/TAXONOMY.md` for the full taxonomy of available lens categories and `references/LENSES.md` for how lenses are structured and how to contribute new ones.

## Cross-Skill State

When applying lenses or generating annotations, the skill may benefit from shared knowledge — e.g. a registry of known people, organizations, and projects so that "Kerry" in one entry resolves to the same entity referenced elsewhere. The cross-skill-state adapter exposes this. When the adapter is `none`, lens application proceeds without it; when the adapter is `shared-file` (or any future adapter), the lens application engine consults it during annotation.

## Setup

First-run setup is driven by the active storage adapter and triggering adapter:

1. **Check for existing configuration** — ask the storage adapter whether a config record exists.
2. **If yes:** load it. Proceed to normal operation.
3. **If no:** run the onboarding conversation:
   - Which belief systems or traditions resonate with you? (Records `declared_lenses`.)
   - Want me to silently capture journal-worthy moments from our conversations? (Records `auto_capture`.)
   - How often do you want reflection prompts? (Records `heartbeat_schedule` if a scheduler is configured.)
   - What timezone are you in? (Records `timezone`.)
4. **Persist config** via the storage adapter's `write config` operation.
5. **Run any adapter-specific setup steps** documented in the active adapters' setup sections (e.g. installing a hook, registering a heartbeat, granting Drive access).

Configuration shape (storage adapter decides where this lives):

```json
{
  "declared_lenses": ["buddhism", "gnosticism"],
  "timezone": "America/New_York",
  "auto_capture": true,
  "heartbeat_schedule": {
    "daily_check": "09:00",
    "weekly_reflection": "sunday 08:00"
  },
  "initialized_at": "2026-03-13T12:00:00Z"
}
```

The `heartbeat_schedule` field is only meaningful when a `heartbeat` scheduling adapter is active; it is ignored under `user-initiated`.

## Storage Operations Used by the Core

The skill body refers to the following operations. Every storage adapter must implement them; see `adapters/storage/` for backend-specific details.

- `read entry for date(date) → entry contents or null`
- `append to entry for date(date, content)` — creates the entry with frontmatter on first call of the day
- `write entry for date(date, content)` — used only for migrations and historical imports, never for normal capture
- `list entries in date range(start, end) → list of dates`
- `read annotation for (date-range, lens) → annotation or null`
- `write annotation for (date-range, lens, content)`
- `read config() → config or null`
- `write config(config)`
- `read metadata() → metadata or null`
- `write metadata(metadata)`

## What This Skill Does Not Do

- It does not modify raw entries after they are written.
- It does not invent or infer journal content the user didn't say.
- It does not apply lens interpretations from memory; lenses always read from storage.
- It does not name runtime-specific paths, hooks, or schedulers in its core. Those belong to adapters.
