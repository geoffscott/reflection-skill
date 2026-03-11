# Lens Application Engine

## Purpose

The Lens Application Engine reads a belief system lens and applies its inference rules to journal entries to generate interpretive annotations. Annotations are overlays that add meaning to entries without modifying them.

**Core principle:** Entries are immutable. Lenses are separate interpretive layers.

## Input
- **Lens definition** — markdown file from `references/lenses/[name].md`
- **Entry set** — journal entries from `~/.openclaw/reflection/entries/YYYY-MM-DD.md`
- **Date range** — time period to analyze

## Output
- **Annotation** — markdown file at `~/.openclaw/reflection/annotations/[lens-name]/YYYY-MM-DD.md`
- **Reference format:** `[→ entries/YYYY-MM-DD.md#HH:MM]`

## 6-Step Operational Process

1. **Parse lens definition** → extract framework, inference rules, epistemological limits
2. **Load entries** → read each file in date range, index by timestamp
3. **Apply rules** → for each entry, test against each inference rule, estimate confidence
4. **Identify observations** → collect rule matches, synthesize across entries, find meta-patterns
5. **Organize findings** → group into 2-3 thematic sections with narrative
6. **Write annotation** → markdown with sections, entry refs, confidence metadata, footer

## Confidence Levels
- **High** — 5+ rules matched with clear textual evidence
- **Medium** — 3-4 rules matched
- **Low** — 1-2 rules matched

## Annotation Template

```markdown
# [Lens Name] Reflection — [Date Range]

[Opening paragraph: 1-2 sentences on what this lens reveals about the time period.]

## [Theme 1]
[Narrative with entry references as [→ entries/YYYY-MM-DD.md#HH:MM]]

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
- [ ] Entry references use correct format `[→ entries/YYYY-MM-DD.md#HH:MM]`
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
