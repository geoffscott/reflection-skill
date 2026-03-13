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

## Setup & Onboarding

### First Run Detection

Before executing any skill operation, check:

```
Does ~/.openclaw/reflection/initialized exist?
```

**If NO → run onboarding (below)**
**If YES → proceed to normal operation**

### Onboarding Flow

When triggered for the first time:

#### Step 1: Create Directory Structure

```bash
mkdir -p ~/.openclaw/reflection/entries
mkdir -p ~/.openclaw/reflection/annotations
```

#### Step 2: Onboarding Conversation

Walk the user through setup. Keep it conversational, not interrogative.

**Ask (in natural order, not as a survey):**

1. **Lens preferences:** "Which belief systems or traditions resonate with you? I have Buddhism and Gnosticism ready, with many more available. You can always add more later."
   - Record responses in config.json `declared_lenses`

2. **Capture preferences:** "I can silently capture journal-worthy moments from our conversations — reflections, insights, dreams, gratitude. Want me to do that?"
   - If yes: will install auto-capture in AGENTS.md (Step 4)

3. **Reflection cadence:** "How often do you want reflection prompts? I'd suggest daily (quick check) and weekly (deeper lens reflection)."
   - Record in config.json `heartbeat_schedule`

4. **Timezone:** "What timezone are you in? This affects when I prompt you."
   - Record in config.json `timezone`

#### Step 3: Write Configuration

Create `~/.openclaw/reflection/config.json`:

```json
{
  "declared_lenses": ["buddhism", "gnosticism"],
  "timezone": "America/New_York",
  "auto_capture": true,
  "heartbeat_schedule": {
    "daily_check": "09:00",
    "weekly_reflection": "sunday 08:00"
  },
  "entities_path": "~/.openclaw/entities.json",
  "initialized_at": "2026-03-13T12:00:00Z"
}
```

#### Step 4: Install Auto-Capture (if user opted in)

Append to AGENTS.md:

```markdown
## Reflection Skill: Auto-Capture

On every inbound user message, silently evaluate whether it's journal-worthy:
- Emotional processing, self-reflection, insights, pattern recognition
- Relationship reflections, gratitude, spiritual/contemplative content
- Life decisions, values-level thinking, dreams, meditations
- Creative ideas with personal meaning

If journal-worthy: clean voice-to-text artifacts, append to
~/.openclaw/reflection/entries/YYYY-MM-DD.md with ## HH:MM timestamp.
Do not respond about the capture. Continue normal processing.

Skip: task management, debugging, scheduling, logistics, commands.
```

This ensures auto-capture is always in the agent's context, not gated behind skill triggering.

#### Step 5: Register Shared Entities

Check if `~/.openclaw/entities.json` exists. If so, note the path in config.json so the lens application engine can reference known people, organizations, and projects when generating annotations.

#### Step 6: Set Up Heartbeat

Append to the workspace HEARTBEAT.md:

```markdown
## Reflection Skill

### Daily Journal Check (09:00 [timezone])
- Check if ~/.openclaw/reflection/entries/YYYY-MM-DD.md exists for today
- If empty: "Nothing captured today. Anything on your mind worth noting?"
- If has entries: silent (no prompt needed)

### Weekly Reflection (Sunday 08:00 [timezone])
- Load this week's entries
- Offer: "Want a lens reflection on this week? I can apply [declared_lenses]."
- If accepted: run lens application engine, present summary
```

#### Step 7: Mark Initialized

```bash
echo "initialized: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > ~/.openclaw/reflection/initialized
```

#### Step 8: Confirm

"All set. I'll silently capture journal-worthy moments, check in daily at [time], and offer a deeper reflection every Sunday. You can ask for a lens reading anytime — just say something like 'give me a Buddhist reading of this week.'"

### Uninstall

To remove the skill's hooks:
1. Remove the "Reflection Skill: Auto-Capture" section from AGENTS.md
2. Remove the "Reflection Skill" section from HEARTBEAT.md
3. Delete ~/.openclaw/reflection/initialized
4. Optionally delete ~/.openclaw/reflection/ (entries and annotations)
