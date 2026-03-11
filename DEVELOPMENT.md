# reflection-skill Development Guide

This file is for developers building and iterating on the skill. It's separate from the user-facing SKILL.md.

## Implementation Checklist: Import Feature

### Phase 1a: File Scanning & Parsing

- [ ] Write `scan-source.sh` — scan source directory, list all markdown files
  - Input: source directory path
  - Output: list of files with metadata (path, filename, size, creation date)
  - Handle: spaces in filenames, nested directories, encoding

- [ ] Write `parse-dates.sh` — extract dates from filenames and filesystem
  - Input: file path
  - Output: ISO date (YYYY-MM-DD)
  - Logic:
    - If filename matches `YYYY-MM-DD.md` → use that date
    - Else use file creation time → convert to YYYY-MM-DD
    - Handle: invalid dates, missing file metadata

- [ ] Validation script — test date parsing on sample files
  - Test cases: valid YYYY-MM-DD names, Craft archive filenames, edge cases

### Phase 1b: Import Execution

- [ ] Write `import-entries.sh` — main import logic
  - Input: source directory, target directory (reflection/entries/)
  - Process:
    1. Scan source for .md files
    2. For each file:
       a. Parse date (using parse-dates.sh)
       b. Read content
       c. Count words (`wc -w`)
       d. Determine source type (daily vs craft)
       e. Create frontmatter
       f. Write to reflection/entries/YYYY-MM-DD.md
    3. Handle conflicts (multiple files → same date, merge as timestamps)
    4. Log errors (unparseable dates, write failures, etc.)
  - Output: import summary (files processed, date range, errors)

- [ ] Write `create-metadata.sh` — generate reflection/metadata.json
  - Tracks: import date/time, source directory, files imported, date range
  - Format: JSON
  - Used for future imports (detection of duplicates, incremental updates)

### Phase 1c: Onboarding & Validation

- [ ] Write `validate-import.sh` — pre-import check
  - Input: source directory path
  - Output: validation report
    - Number of files found
    - Date range covered
    - Any unparseable files
    - Estimated word count
    - Approval prompt (yes/no)

- [ ] Write `onboarding.sh` — first-run flow
  - Detect: is reflection/entries/ empty?
  - If yes:
    1. Welcome message + brief explanation
    2. Prompt for source directory path
    3. Run validation
    4. Show summary, ask for confirmation
    5. Run import if approved
  - If no:
    - Skip onboarding, offer manual import command

- [ ] Integration with OpenClaw — how does onboarding trigger?
  - Option A: Skill detects first run, prompts in Discord
  - Option B: Manual invocation (`/reflection-import /path/to/vault`)
  - Option C: Both (auto-detect, manual override)

### Phase 1d: Testing

- [ ] Unit tests for date parsing (valid/invalid cases)
- [ ] Integration test with sample markdown files
  - Create 5-10 test files (daily + Craft format)
  - Run full import pipeline
  - Verify output structure and metadata
- [ ] Edge case tests
  - File with no content
  - File with special characters in name
  - Multiple entries on same date
  - Missing file metadata
- [ ] Performance test
  - Time import of 179 files
  - Verify no data loss or corruption

## Design Decisions (Implementation Details)

### Why Shell Scripts vs Python/Node?
- OpenClaw default is shell for file operations
- Keeps skill lightweight and portable
- Easier to debug in production
- Can call from Discord bot directly

### Date Inference from File Metadata
- Use `stat` command to get file creation time
- Most reliable on macOS (born time), reasonable on Linux (change time)
- Format as ISO date
- Log any ambiguous cases

### Frontmatter Format
- YAML format (standard for markdown)
- Keep minimal: date, source, length, original_filename (for Craft)
- Future: add tags, mood, energy level (user can add manually later)

### Conflict Resolution: Multiple Files → Same Date
```
If User/Journal/2026-03-06.md already exists, and we want to import
Personal/Archive/Craft/Energy Flow.md (dated 2026-03-06):

Create: reflection/entries/2026-03-06.md with both:

---
date: 2026-03-06
imported_from: [mixed]
sources:
  - markdown
  - craft_archive
---

## [timestamp from markdown file]
[content]

## [timestamp from craft file]
[content from craft]
```

### Signals File Format
Not implemented in Phase 1, but plan ahead:
```jsonl
{"date": "2026-03-06", "type": "entry_created", "source": "discord", "length_words": 342}
{"date": "2026-03-05", "type": "entry_imported", "batch_id": "initial_import", "count": 45}
```

## Building the Import Script

### File: `dev/import-script.sh`

The main orchestrator script. Should:
1. Source helper scripts (parse-dates.sh, validate-import.sh, etc.)
2. Accept source directory as argument or prompt for it
3. Run validation
4. Ask for confirmation
5. Execute import
6. Report summary

Example invocation:
```bash
./dev/import-script.sh /path/to/vault
# or
./dev/import-script.sh  # prompts for path
```

## Testing Against Your Actual Vault

Before running on full vault, test with:
1. Sample of 5-10 files (daily + Craft)
2. Verify structure: entries/, metadata.json created
3. Inspect one entry file: frontmatter correct, content preserved
4. Check word count accuracy
5. Review import summary report

Then run full import on your 179 files.

## Future Considerations

### Incremental Import
If you add new daily entries, script should detect them and not re-import existing ones. Use metadata.json to track what's been imported.

### Source Directory Changes
If source directory structure changes (e.g., you reorganize vault), re-import should be possible (skip duplicates by date).

### Annotation Overlays (Lenses)
Plan: User can create `reflection/annotations/jungian/2026-03-06.md` manually, or skill can scaffold templates. Keep lenses separate from entries.

### Kaizen Integration
Plan: Skill writes to `reflection/signals/` with pattern metadata (no content). Kaizen skill reads those signals to identify growth, recurring themes, etc.

---

**Status:** Ready to build. Start with Phase 1a (file scanning).
