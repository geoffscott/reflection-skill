# Lens Application Engine

## Purpose

The Lens Application Engine reads a belief system lens and applies its inference rules to journal entries to generate interpretive annotations. Annotations are overlays that add meaning to entries without modifying them.

**Core principle:** Entries are immutable. Lenses are separate interpretive layers.

## Input
- **Lens definition** — markdown file from `references/lenses/[name].md` in the skill repo
- **Entry set** — journal entries loaded via the storage adapter's `read entry for date` for each date in the requested range
- **Date range** — time period to analyze

## Output
- **Annotation** — written via the storage adapter's `write annotation for (date-range, lens)` operation
- **Reference format:** `[→ entry YYYY-MM-DD#HH:MM]`

The engine never names a path or URL directly. All persistence flows through storage operations defined in `SKILL.md` and implemented by whichever storage adapter is active.

## 6-Step Operational Process

1. **Parse lens definition** → extract framework, inference rules, epistemological limits
2. **Load entries** → for each date in the range, call `read entry for date` and index by timestamp. Always read fresh; never synthesize from memory.
3. **Apply rules** → for each entry, test against each inference rule, estimate confidence
4. **Identify observations** → collect rule matches, synthesize across entries, find meta-patterns
5. **Organize findings** → group into 2-3 thematic sections with narrative
6. **Write annotation** → markdown with sections, entry refs, confidence metadata, footer; persist via `write annotation for (date-range, lens)`

## Confidence Levels
- **High** — 5+ rules matched with clear textual evidence
- **Medium** — 3-4 rules matched
- **Low** — 1-2 rules matched

## Annotation Template

```markdown
# [Lens Name] Reflection — [Date Range]

[Opening paragraph: 1-2 sentences on what this lens reveals about the time period.]

## [Theme 1]
[Narrative with entry references as [→ entry YYYY-MM-DD#HH:MM]]

## [Theme 2]
[Narrative with entry references]

## What This Lens Illuminates
[Summary of insights + limitations of this lens for this content]

---

**Annotation Metadata**
- **Lens:** [name]
- **Date Range:** [dates]
- **Applied:** [timestamp]
- **Confidence:** [High/Medium/Low]
- **Entry Count:** [number]
- **Themes:** [list]
```

## Quality Checklist

- [ ] Framework accurately represented (not misinterpreted)
- [ ] Entry references use correct format `[→ entry YYYY-MM-DD#HH:MM]`
- [ ] Every rule match grounded in specific entry text
- [ ] Notes what lens sees well AND what it misses
- [ ] Jargon translated or explained
- [ ] Sections tell a narrative, not just list rules
- [ ] Confidence calibrated to evidence strength
- [ ] Metadata complete

## Operational Prompt

**You are a lens application expert. Apply a belief system lens to journal entries, creating an interpretive annotation.**

1. Parse the lens definition: extract framework, inference rules, strengths, limitations.
2. Read each entry. Test each lens inference rule against entry content.
3. Identify 2-3 major thematic patterns across entries.
4. Write annotation with opening paragraph, thematic sections (with entry references), and closing "What This Lens Illuminates" section.
5. Include metadata footer.

**Standards:** Ground every claim in entry text. Translate jargon. Note what the lens does NOT see. Write narrative, not lists. Be honest about confidence.
