# Contributing to Reflection-Skill

Thank you for your interest in contributing! This document explains how to work with the project, whether you're adding a new lens, improving documentation, or extending functionality.

---

## Getting Started

### Prerequisites

- Git
- A text editor or IDE
- For lens contributions: familiarity with a belief system (your own or researched)

### Clone the Repository

```bash
git clone https://github.com/geoffscott/reflection-skill.git
cd reflection-skill
git checkout dev  # Work from the dev branch, not main
```

---

## Branching Strategy

### Branch Structure

- **`main`** — Stable releases only. Always deployable, fully documented.
- **`dev`** — Active development. Working features, recent changes, experimental work.
- **Feature branches** — Off `dev`, deleted after merge.

### Creating a Feature Branch

```bash
git fetch origin                    # Start with latest
git checkout -b draft/[task-name]   # For work in progress
# or
git checkout -b feat/[feature-name] # For completed features
```

**Naming conventions:**
- `draft/vedanta-lens` — Initial research/development
- `feat/auto-journaling` — Complete, ready to merge
- `improve/lens-docs` — Improvements to existing work
- `fix/entity-resolver` — Bug fix

---

## Contributing a Lens

This is the primary way to extend the project. Every lens must be rigorously researched.

### 1. Research Phase

Before writing, study the tradition deeply:

- **Primary texts:** Sacred texts, foundational writings
- **Scholarly sources:** Academic treatments by respected scholars
- **Living practitioners:** Teachers, leaders, people who practice it
- **Your perspective:** Are you inside this tradition or observing from outside? Document this.

### 2. Draft the Lens File

Create `lenses/[name].md` following this structure:

#### Framework
A clear, accessible definition (2-3 paragraphs). No jargon without translation.

Example:
> Stoicism is a philosophical practice from ancient Greece and Rome focused on living according to reason and virtue. Practitioners believe that external events are beyond our control, but our responses (judgments, desires, actions) are entirely within our control. By aligning our will with reason and nature, we find freedom and peace regardless of circumstances.

#### Universal Questions
Which of the six questions does this illuminate? List them with brief explanations:

```markdown
- **How should I live?** — According to virtue and reason, accepting what's outside your control
- **What's true?** — External events are indifferent; what matters is your judgment
- **How do I find peace?** — By focusing effort only on what's in your control
```

#### Inference Rules
What patterns does an agent look for when reading journal entries through this lens?

```markdown
- Language of control/acceptance ("I can/can't control...")
- Emotional reactions to external events
- Distinctions between judgment and fact
- Values alignment in difficult situations
```

#### Epistemological Grounding
What does this lens see well? What might it miss?

```markdown
**Sees well:**
- Personal agency and emotional regulation
- Distinction between fact and interpretation

**May miss:**
- Structural oppression (not always within individual control)
- Collective and relational dimensions of life
```

#### Reference Materials
Authoritative sources. Be specific.

```markdown
- Epictetus, *Enchiridion* (foundational text)
- Marcus Aurelius, *Meditations* (personal practice)
- Pierre Hadot, *Philosophy as a Way of Life* (modern scholarship)
- Irvine, William B. *A Guide to the Good Life* (contemporary)
```

#### Plain Language Translation
One paragraph describing the lived experience.

```markdown
A Stoic focuses energy only on things within their control: their judgments, desires, and actions. When facing difficulty, they ask: "Is this something I can influence?" If yes, act with reason and virtue. If no, accept it without complaint. This creates a kind of freedom—not freedom from difficulty, but freedom from being controlled by circumstances.
```

### 3. Test the Lens

- Read your own journal (if you have one) through this lens
- Does it surface meaningful patterns?
- Are the inference rules actionable for an agent?
- Is every term understandable without specialized knowledge?

### 4. Get Feedback

Before submitting:
- Have someone from the tradition review it (if possible)
- Have someone outside the tradition read it (clarity test)
- Ask: "Could an AI agent use this to read my journal?"

---

## Pull Request Process

### Before You Push

```bash
git add lenses/[name].md    # or whatever you changed
git commit -m "feat: add [belief-system] lens

- Research sources: [list 2-3 key sources]
- Questions addressed: [list which of the 6]
- Ready for: [community review / feedback welcome / draft]"

git push origin draft/[task-name]
```

### Open the PR

On GitHub, create a PR from your branch to `dev` (not `main`).

**PR template:**

```markdown
## What This Does
[One paragraph explaining the lens and why it matters]

## What Changed
- Added [belief-system].md lens
- Researched [X] primary sources and [Y] secondary sources
- Tested against [how you tested it]

## How to Review
1. Read the Framework section first
2. Check if the Universal Questions make sense
3. Test the Inference Rules: could an agent use these?
4. Verify Plain Language Translation is accessible

## Research Sources
- [Authoritative source 1]
- [Authoritative source 2]
- [etc]

## Questions for Reviewers
- [Any uncertainties or areas where feedback would help]
```

### Review & Merge

Community members and maintainers will:
- Verify research accuracy
- Check clarity and accessibility
- Suggest refinements
- Approve or request changes

Once approved, we merge to `dev`, then periodically release `dev` → `main`.

---

## Documentation & Other Contributions

### Improving Docs

Same process:
1. Branch off `dev`
2. Make changes
3. Test readability
4. Open PR with clear explanation
5. Merge when approved

### Bug Fixes

If you find an issue:
1. Open an issue describing the problem
2. Branch off `dev` as `fix/[issue-name]`
3. Fix it
4. Open PR referencing the issue
5. Merge when tests pass (if applicable)

---

## Quality Standards

### For All Contributions

✓ Clear, accessible language (no jargon without translation)
✓ Properly researched (cite sources)
✓ Follows the established template/style
✓ Honest about limitations and perspectives
✓ Respectful of other traditions and viewpoints

### For Lenses Specifically

✓ Framework definition is clear to someone unfamiliar with the tradition
✓ Universal Questions mapping is accurate
✓ Inference Rules are actionable (an agent could use them)
✓ Epistemological Grounding acknowledges limits
✓ References are authoritative and specific
✓ Plain Language Translation matches the Framework

### Not Acceptable

✗ Personal syntheses presented as established traditions (unless explicitly labeled)
✗ Jargon without explanation
✗ Unfounded claims about what the tradition teaches
✗ Dismissal or denigration of other beliefs
✗ Incomplete research (copy-pasted descriptions without understanding)

---

## Code of Conduct

We're building a space where people of many beliefs learn from each other. Be:

- **Respectful:** Engage with other traditions as you'd want your own engaged with
- **Humble:** You may not understand everything about a tradition—that's okay, ask
- **Rigorous:** Research matters. Don't guess about what people believe
- **Kind:** Remember there are real people behind these frameworks

---

## Questions?

- **About a lens?** Open an issue to discuss before you write
- **About the process?** Open an issue or reach out directly
- **Want to contribute but not sure how?** Ask—we'll help you find a good starting point

---

## Recognition

Contributors are recognized in:
- Lens file headers (maintainer attribution)
- Release notes (major contributions)
- Project README (significant work)

Thank you for helping make reflection-skill more rigorous and inclusive.

---

**Contributing Guide Version:** 0.1 | **Last Updated:** Mar 8, 2026
