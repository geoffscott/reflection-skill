---
name: reflection
version: 0.1.0
description: Capture and reflect on your stream of consciousness with interpretive lenses
kind: skill
author: Geoff Scott
tags: [journaling, reflection, personal-practice, stream-of-consciousness]
---

# reflection-skill

Capture your stream of consciousness and reflect on it through multiple interpretive lenses—without ever modifying the raw entries.

## Purpose

Your thinking unfolds in real time: daily meditation, conversations, random insights, work thoughts. Reflection-skill preserves that stream as immutable history, then lets you layer interpretive lenses on top (Jungian, Stoic, CBT, indigenous-spiritual, contemplative, IFS, freeform) to deepen your understanding of patterns, growth, and self-knowledge over time.

The stream is the data. The lenses are the interpretation.

## Architecture

### Data Structure

```
reflection/
├── entries/                           # Immutable raw entries
│   ├── 2025-10-04.md                 # Daily entry
│   ├── 2025-10-05.md
│   └── 2026-03-06.md                 # Multiple timestamps per day
├── annotations/                       # Overlays, organized by lens
│   ├── jungian/
│   │   ├── 2025-10-04.md            # Jungian interpretation of that day
│   │   └── index.md
│   ├── stoic/
│   │   ├── 2025-10-04.md
│   │   └── index.md
│   ├── cbt/
│   └── [other lenses...]
├── signals/                           # Metadata for Kaizen skill
│   ├── patterns.jsonl               # Pattern signals
│   └── milestones.jsonl             # Milestone/insight signals
└── metadata.json                      # Reflection history (import dates, etc.)
```

### Entry Format

Each file in `reflection/entries/` is immutable:

```markdown
---
date: 2026-03-06
imported_from: discord|markdown|craft_archive
length_words: 342
---

## 07:15 — Morning Thought
Raw meditation capture. No filtering. This is the stream.

## 09:30 — From Discord
Another thought that landed throughout the day.

## 14:00 — Reflection
Something else.
```

**Key principles:**
- One file per calendar day
- Timestamps within the file preserve intra-day sequence
- Frontmatter captures metadata (date, source, length)
- No modifications after creation (immutable raw data)

### Lens Format

Each lens is a directory of dated files that *reference* entries without modifying them:

```markdown
# Jungian Reflection — March 6, 2026

## Shadow Work
The 09:30 entry hints at [reference: entries/2026-03-06.md#09:30] an unexamined part of yourself...

## Synchronicity
The morning thought [reference: entries/2026-03-06.md#07:15] connects to the larger pattern of...
```

Lenses are *overlay* structures—they add meaning without touching the original entries.

## First User Story: Import

**As a user, I want to import my existing journal entries so I can reflect on my full history.**

### What Gets Imported

**Phase 1 (this release):**
- 154 daily entries (YYYY-MM-DD.md format, Oct 2025–early 2026)
- 25 Craft reflections (longer-form, dates inferred from file metadata)
- **Total: 179 entries** covering the full reflective archive

**Not imported (Phase 2):**
- Tasks, Projects, Notes, Unsorted, etc. (require separate design)

### Import Workflow

1. **First run detection** — Skill checks if `reflection/entries/` is empty
2. **Onboarding prompt** — Offers import; asks for source directory path
3. **Validation** — Scans source; counts files, date range, any errors
4. **Confirmation** — Shows what will be imported; requires approval
5. **Import execution** — Copies files, adds frontmatter, creates metadata.json
6. **Summary** — Reports: files imported, date range, any skipped/errors

### Import Logic

#### Daily Entries (YYYY-MM-DD.md)

**Source pattern:** `Personal/Journal/YYYY-MM-DD.md`

**Process:**
1. Parse filename for date (e.g., `2026-03-06.md`)
2. Read raw content
3. Create `reflection/entries/2026-03-06.md` with frontmatter:
   ```yaml
   date: 2026-03-06
   imported_from: markdown
   length_words: [count]
   ```
4. Preserve all original content exactly

#### Craft Reflections (topic-based names)

**Source pattern:** `Personal/Archive/Craft/My Space/Journal/*.md`

**Process:**
1. No date in filename → use file creation time from filesystem
2. Round creation time to date (e.g., file created Mar 4, 2024 14:33 → 2024-03-04)
3. If multiple Craft files on same date, append as separate timestamp sections
4. Create entry with frontmatter:
   ```yaml
   date: 2024-03-04
   imported_from: craft_archive
   original_filename: [Enabling dreams of others.md]
   length_words: [count]
   ```

### Acceptance Criteria

- [x] Skill directory structure created
- [ ] SKILL.md defines behavior and data formats
- [ ] Import script scans source directory
- [ ] Parses YYYY-MM-DD filenames correctly
- [ ] Infers dates from Craft file metadata
- [ ] Creates frontmatter with date, source, word count
- [ ] Preserves original content without modification
- [ ] Generates import summary report
- [ ] Handles edge cases (missing dates, encoding, empty files)
- [ ] Onboarding flow walks user through import
- [ ] metadata.json records import history

## Implementation Notes

### Tech Stack
- Shell scripts for file scanning and processing
- Markdown frontmatter (YAML) for entry metadata
- Filesystem structure for organization (no database for Phase 1)
- `wc -w` for word count, `stat` for file timestamps

### Design Decisions
- **No database yet** — Phase 1 is files on disk. Mirrors your workflow.
- **One entry per day** — Simplifies navigation, matches your existing structure
- **Immutability at filesystem level** — entries/ is the source of truth; lenses are separate
- **Signals file (for Kaizen)** — jsonl format, contains only metadata (no content)

## Future Phases

**Phase 2:** Parse Tasks, Projects, and Unsorted; determine proper structure for each

**Phase 3:** Lens generation (automated + manual)

**Phase 4:** Query interface ("show me all Jungian entries in 2025 about relationships")

**Phase 5:** Integration with Kaizen skill (pattern detection, growth tracking)

## Related Skills

- **kaizen-skill** — Consumes signals from reflection/signals/ to identify patterns and growth
- **todo-skill** — Could import from reflection/ with metadata tagging

## Files in This Skill

- `SKILL.md` — This file (user-facing skill definition)
- `dev/DEVELOPMENT.md` — Implementation guide for developers
- `dev/import-script.sh` — File scanning and import logic
- `entries/` — User's journal entries (created on first import)
- `annotations/` — Interpretive lenses (created as user adds lenses)
- `signals/` — Metadata for Kaizen consumption
