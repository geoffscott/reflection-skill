# Phase 2.3: Auto-Journaling Classifier — Design Document

## Purpose

Watch Geoff's Discord stream throughout the day and identify content that should become a journal entry. The classifier is the brain; the heartbeat (Phase 2.4) is the clock.

## Status: Design In Progress

### Decided

- **Source:** Classifier watches Discord messages (not just the daily template)
- **Scope:** Identifies journal-worthy content from the stream of consciousness
- **Relationship to 2.4:** Tightly coupled with heartbeat rituals — classifier decides WHAT, heartbeat decides WHEN

### Journal-Worthy Content (capture)

- Emotional processing, self-reflection
- Insights, realizations, pattern recognition
- Relationship reflections (people, dynamics, feelings)
- Gratitude, spiritual/contemplative content
- Life decisions, values-level thinking
- Dreams, meditations
- Creative/generative ideas with personal meaning (e.g., CFO Kit emergence)

### Not Journal-Worthy (skip)

- Task management ("remind me to X")
- Technical debugging
- Scheduling, logistics
- Routine operational updates
- Commands to the agent

### Open Design Questions

**Q1: Capture mode**
When journal-worthy content is spotted, what happens?
- Option A: Silent capture — file it, review later
- Option B: Flag in moment — "that sounds journal-worthy, want me to capture it?"
- Option C: Silent capture + daily summary of what was captured
- **Decision:** TBD

**Q2: Source channels**
Which Discord channels are monitored?
- Option A: Just #inbox (primary stream)
- Option B: All channels where Geoff sends messages
- Option C: Configurable per channel
- **Decision:** TBD

**Q3: Granularity**
What gets captured?
- Option A: Exact message text (raw, including voice-to-text artifacts)
- Option B: Cleaned/synthesized version (fix transcription errors, normalize)
- Option C: Both — raw preserved, cleaned version for the entry
- **Decision:** TBD

**Q4: Entry format**
How does captured content become an entry?
- Option A: Append to existing daily file (entries/YYYY-MM-DD.md) with timestamp
- Option B: Create separate micro-entries
- Option C: Buffer throughout day, compile into single entry at end of day
- **Decision:** TBD

**Q5: Declared lenses shaping capture**
Per the design spec, declared lenses should influence what gets captured (not just how entries are interpreted). How?
- Option A: Lens-specific triggers (e.g., Buddhism lens → extra sensitivity to craving/aversion patterns)
- Option B: After capture, tag with which lenses might apply
- Option C: Both
- **Decision:** TBD

## Phase 2.4 Integration Points

- Daily heartbeat (9 AM): Check if anything was captured. If not, prompt.
- Weekly heartbeat (Sunday 8 AM): Offer lens reflection on the week's entries.
- Both heartbeats reference classifier output.

## Phase 2.5 Integration Points

- Learning system tracks which captured content gets kept vs. dismissed
- Over time, classifier improves based on preferences
- Proactive lens suggestions based on detected patterns in captured content

## Implementation Notes

- Classifier runs as part of the agent's normal message processing (not a separate service)
- Per SKILL.md three-mode interaction: capture is silent ("Got it")
- Entries are immutable once written
- All runtime data in ~/.openclaw/reflection/ (not in repo)
