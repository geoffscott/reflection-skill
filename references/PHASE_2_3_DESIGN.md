# Phase 2.3: Auto-Journaling Classifier — Design Document

## Purpose

Watch the user's message stream and identify content that should become a journal entry. The classifier is the brain; the heartbeat (Phase 2.4) is the clock.

## Decisions

### Capture Mode: Silent
File journal-worthy content without interrupting. No prompts, no confirmations.

### Source: All Channels (default)
Not hardcoded to any specific channel. Open source skill — works wherever installed.

### Granularity: Clean Voice-to-Text, Preserve Meaning
Fix transcription artifacts (spelling, punctuation, obvious mishearings). Do not synthesize, summarize, or significantly alter the original content.

### Entry Format: Append to Daily File
Captured content appends to `~/.openclaw/reflection/entries/YYYY-MM-DD.md` with timestamp headers. One file per calendar day, matching existing entry format.

### Lens-Shaped Capture: Deferred
Lenses influence interpretation only (Phase 2.2), not capture. Try it simple first.

## Journal-Worthy Content (capture)

- Emotional processing, self-reflection
- Insights, realizations, pattern recognition
- Relationship reflections (people, dynamics, feelings)
- Gratitude, spiritual/contemplative content
- Life decisions, values-level thinking
- Dreams, meditations
- Creative/generative ideas with personal meaning

## Not Journal-Worthy (skip)

- Task management ("remind me to X")
- Technical debugging
- Scheduling, logistics
- Routine operational updates
- Commands to the agent

## Entry Format

```markdown
---
date: YYYY-MM-DD
---

## HH:MM — [optional context]

[Cleaned content from message stream]

## HH:MM — [optional context]

[Another captured moment]
```

## Integration Points

### Phase 2.4 (Heartbeat Rituals)
- Daily heartbeat (9 AM): Check if anything was captured. If not, prompt.
- Weekly heartbeat (Sunday 8 AM): Offer lens reflection on the week's entries.

### Phase 2.5 (Learning System)
- Track which captures get kept vs. dismissed over time
- Improve classifier accuracy based on user preferences

## Implementation Notes

- Classifier runs as part of normal agent message processing (not a separate service)
- Per SKILL.md: capture is silent ("Got it" equivalent — no response needed)
- Entries are immutable once written
- All runtime data in ~/.openclaw/reflection/ (not in repo)
- Frontmatter created on first capture of the day; subsequent captures append
