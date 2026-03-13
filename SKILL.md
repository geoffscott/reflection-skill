---
name: reflection
description: Capture and reflect on your stream of consciousness with interpretive lenses. Use when the user shares personal reflections, insights, emotional processing, dreams, meditations, gratitude, or relationship observations. Also triggers on requests to apply a lens or review journal entries.
---

# Reflection Skill

Capture stream of consciousness throughout the day. Reflect on it through interpretive lenses without modifying the raw entries.

## How It Works

### Auto-Capture

On every inbound user message, evaluate whether it's journal-worthy:

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

**When capturing:**
1. Clean voice-to-text artifacts (spelling, punctuation, obvious mishearings)
2. Do not synthesize, summarize, or significantly alter the content
3. Append to the daily entry file with a timestamp header
4. Do not respond about the capture — continue normal processing silently

### Entry Format

Runtime data location: `~/.openclaw/reflection/`

Each day gets one file: `entries/YYYY-MM-DD.md`

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
- One file per calendar day
- `## HH:MM` timestamp headers in chronological order
- Frontmatter on first capture of the day; subsequent captures append
- Entries are immutable once written — never modify past entries
- Use UTC timestamps

### Writing an Entry

To append a captured moment to today's file:

1. Check if `entries/YYYY-MM-DD.md` exists
2. If not, create it with frontmatter: `date: YYYY-MM-DD`
3. Append `## HH:MM` header + cleaned content
4. Ensure a blank line before and after the new section

### Reflection Mode

When the user requests a lens reflection (e.g., "give me a Buddhist reading of this week"):

1. Load the requested lens from `references/lenses/[name].md` in the skill repo
2. Load entries for the requested time period
3. Apply the lens using the process in `references/LENS_APPLICATION_ENGINE.md`
4. Write the annotation to `annotations/[lens-name]/YYYY-MM-DD.md`
5. Present a summary to the user
6. Offer the full annotation if they want it

### Available Lenses

Lens definitions live in the skill repo under `references/lenses/`:

- **Buddhism** — Craving, impermanence, presence, reactivity patterns
- **Gnosticism** — Sophia/archontic choices, false authority, awakening moments

See `references/TAXONOMY.md` for the full taxonomy of available lens categories.
See `references/LENSES.md` for how lenses are structured and how to contribute new ones.

## Data Layout

```
~/.openclaw/reflection/          # Runtime data (never in git)
├── entries/                     # Immutable journal entries
│   └── YYYY-MM-DD.md
├── annotations/                 # Lens interpretation overlays
│   └── [lens-name]/
│       └── YYYY-MM-DD.md
└── metadata.json                # Usage tracking

skill repo (references/)         # Lens definitions (in git)
├── lenses/
│   ├── buddhism.md
│   └── gnosticism.md
├── LENSES.md
├── TAXONOMY.md
└── LENS_APPLICATION_ENGINE.md
```

## Historical Entries

154 entries imported from Obsidian (Oct 2025 – Mar 2026) use an older template format with `# Section` headers (Gratitudes, Meditations, etc.). These remain as-is. New auto-captured entries use the timestamped format above.
