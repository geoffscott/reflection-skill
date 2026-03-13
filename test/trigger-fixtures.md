# Skill Description Trigger Test Fixtures

Test whether the reflection skill's description correctly triggers (or doesn't)
for these sample messages. Run manually by sending each phrase and checking
which skill activates.

## MUST trigger reflection skill

### Explicit reflection requests
- "give me a Buddhist reading of this week"
- "apply the Gnosticism lens to February"
- "what did I journal yesterday?"
- "review my entries from last week"
- "reflect on what I wrote in January"
- "show me my journal entries"
- "what patterns do you see in my reflections?"

### Explicit capture requests
- "journal this: I had an insight about impermanence today"
- "capture this thought"
- "save this reflection"
- "I want to note something for my journal"

### Lens-specific triggers
- "Buddhism lens on this week"
- "Gnosticism reflection"
- "what would a Stoic reading of my month look like?"
- "apply a lens to my entries"
- "annotate this week with Buddhism"

### Onboarding (first run)
- "set up my journal"
- "configure reflection skill"
- "I want to start journaling"

## MUST NOT trigger reflection (belongs to completion skill)

- "remind me to journal tonight"
- "add 'write reflection' to my personal tasks"
- "what's on my plate today?"
- "standup"
- "what tasks are stuck?"
- "I need to finish the PR review"

## MUST NOT trigger reflection (no skill needed)

- "what's the weather?"
- "help me debug this Python script"
- "check the CI status on that PR"
- "what time is it?"
- "summarize this document"

## AMBIGUOUS — document expected behavior

These could go either way. Document what SHOULD happen:

- "capture this idea for the product roadmap"
  → Expected: completion (it's a task/idea, not a reflection)

- "I had a dream about work last night"
  → Expected: reflection (dream content is journal-worthy)

- "I'm feeling frustrated with this project"
  → Expected: reflection auto-capture (if installed in AGENTS.md)
  → Without auto-capture: may not trigger (it's conversational)

- "I'm grateful for my team today"
  → Expected: reflection auto-capture (gratitude)
  → Without auto-capture: may not trigger

- "what did I say about Kerry last week?"
  → Expected: reflection (searching journal entries)
  → Could also be: general memory recall

## Testing Procedure

### Manual test
1. Send each phrase in #inbox
2. Note which skill triggers (check if SKILL.md is read)
3. Record results below
4. Adjust description if misses or false positives found

### Automated test (future)
Build a script that:
1. Constructs a prompt with all skill descriptions + test message
2. Asks LLM: "which skill applies?"
3. Compares response to expected result
4. Reports pass/fail

```python
# Sketch of automated test
import json

skills = [
    {"name": "reflection", "description": "..."},
    {"name": "completion", "description": "..."},
    {"name": "weather", "description": "..."},
    # ... all installed skills
]

fixtures = [
    {"message": "give me a Buddhist reading", "expected": "reflection"},
    {"message": "remind me to journal", "expected": "completion"},
    {"message": "what's the weather?", "expected": "weather"},
]

prompt = f"""Given these available skills:
{json.dumps(skills, indent=2)}

For this user message: "{message}"

Which skill clearly applies? Reply with just the skill name, or "none".
"""

# Call LLM API, compare result to expected
```

## Results Log

| Date | Phrase | Expected | Actual | Pass? |
|------|--------|----------|--------|-------|
| | | | | |
