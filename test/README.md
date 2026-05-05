# Reflection-skill tests

Automated fixture tests for the conceptual core of the skill. Loads `SKILL.md` plus everything under `references/` as a cached system prompt, mocks the storage adapter operations as tool calls, runs each fixture against the Claude API, and asserts on the resulting tool-call sequence, final mock-storage state, and response text.

These tests cover the runtime-agnostic behavior of the skill: capture taxonomy, voice-to-text discipline, immutability, and the lens application engine's read-fresh-from-storage discipline. They do **not** exercise a real storage adapter (`local-fs`, `google-drive`, `github`) — adapter-specific behaviors like Drive read-modify-write or GitHub commits need to be tested against a live backend.

## Setup

```bash
pip install -r test/requirements.txt
export ANTHROPIC_API_KEY=...
```

## Run

```bash
python test/run_tests.py                    # run every suite
python test/run_tests.py capture            # one suite
python test/run_tests.py --fixture captures_gratitude    # one fixture
python test/run_tests.py --model claude-sonnet-4-6        # cheaper model
python test/run_tests.py -v                 # show tool call list and response text on failures
```

A full run is ~16 fixtures. Default model is `claude-opus-4-7`. Switching to `claude-sonnet-4-6` runs ~3× cheaper and is fine for most fixtures.

## Cost

The system prompt (~8K tokens of `SKILL.md` + references) is sent on every fixture but uses prompt caching, so only the first request pays full price. Per-fixture cost on Opus 4.7 is roughly `$0.05–0.10` after the cache warms; on Sonnet 4.6 roughly `$0.02–0.04`. Plan for `~$1` for a full Opus run, `~$0.30` for Sonnet.

## How it works

`run_tests.py`:

1. Reads `SKILL.md` and every file under `references/` and packs them into a single cacheable `<file path="...">` block in the system prompt.
2. Defines tools matching the storage adapter operations declared in `SKILL.md` (`read_entry_for_date`, `append_to_entry_for_date`, `list_entries_in_date_range`, `read_annotation`, `write_annotation`, etc.).
3. For each fixture, constructs a `MockState` (optionally pre-loaded with entries / annotations / config), pins today's date and time via a small bracketed system note, and runs the agentic loop until the model stops calling tools or hits the turn limit.
4. Evaluates the fixture's assertions against the recorded tool calls, the final `MockState`, and the model's response text.

## Fixture format

Each fixture is a JSON object. A representative example:

```json
{
  "name": "captures_gratitude",
  "today": "2026-05-05",
  "now_time": "09:15",
  "preload_entries": {
    "2026-05-04": "---\ndate: 2026-05-04\n---\n\n## 14:30\n\nPrior content.\n"
  },
  "preload_annotations": {
    "2026-05-04|gnosticism": "..."
  },
  "preload_config": { "declared_lenses": ["buddhism"] },

  "message": "I'm grateful for the clarity this morning.",

  "must_call": ["append_to_entry_for_date"],
  "must_not_call": ["write_entry_for_date"],
  "expected_tool_sequence": ["list_entries_in_date_range", "read_entry_for_date"],
  "exact_tool_count": { "read_entry_for_date": 3 },

  "expected_entries": {
    "2026-05-05": {
      "contains": ["grateful"],
      "not_contains": ["fabricated content"]
    }
  },
  "expected_no_entry_changes": ["2026-05-04"],
  "expected_annotations": [
    { "range_key": "2026-W18", "lens": "buddhism", "contains": ["[→ entry"] }
  ],

  "response_contains": ["got it"],
  "response_not_contains": ["I cannot"]
}
```

| Field | Meaning |
|---|---|
| `name` | Fixture identifier (used by `--fixture`). |
| `today`, `now_time` | Pinned via a bracketed test-harness note in the user message so date math is deterministic. |
| `preload_entries` | Map of `YYYY-MM-DD` → markdown body to seed `MockState.entries` before the run. |
| `preload_annotations` | Map of `"range_key\|lens"` → markdown to seed `MockState.annotations`. |
| `preload_config` | Object to seed `MockState.config` (so `read_config` returns it). |
| `message` | The user message that drives the run. |
| `must_call` | Tool names that must appear in the call list. |
| `must_not_call` | Tool names that must not appear. |
| `expected_tool_sequence` | A subsequence the actual call list must contain in order. |
| `exact_tool_count` | Exact count match for specific tools. |
| `expected_entries` | After the run, each named entry must exist; `contains` / `not_contains` are substring checks. |
| `expected_no_entry_changes` | Entries that must be byte-identical to their `preload_entries` value (immutability). |
| `expected_annotations` | After the run, each annotation must exist; supports `contains` and `not_contains`. |
| `response_contains` / `response_not_contains` | Case-insensitive substring checks on the model's final text. |

## What's covered

- **`capture.json`** — capture taxonomy: gratitude, dreams, emotional processing should be captured; task management, debugging, and logistics should be skipped. Append-vs-overwrite discipline.
- **`immutability.json`** — explicit edit requests on past entries should not call `write_entry_for_date`. Corrections create new sections, not edits.
- **`lens.json`** — weekly lens reflection lists the date range, reads each entry fresh (one `read_entry_for_date` per entry in range), and writes an annotation containing the entry-reference format and the "What This Lens Illuminates" closing section. Empty range handled gracefully.
- **`reflection.json`** — user-initiated daily check (with and without entries) and longitudinal pattern recognition.

## What's NOT covered

- **Adapter-specific behavior.** Drive read-modify-write semantics, GitHub commit shape, local-fs frontmatter formatting — these live in adapter-implementation territory and need a real backend. Run a one-shot smoke test against the actual deployment before shipping.
- **Trigger description matching.** The harness assumes the skill is engaged; it doesn't simulate the routing layer that selects which skill applies. The `test/trigger-fixtures.md` document holds prose-form trigger fixtures for that purpose; a routing-style test could be added later as a separate suite.
- **Heartbeat scheduling.** No scheduler is exercised. Tests focus on the user-initiated equivalent of every workflow, since the conceptual core is identical.

## Adding fixtures

Create a new entry in any `fixtures/*.json` file (or a new file — every `.json` under `fixtures/` is picked up automatically). A new fixture costs nothing to add structurally; the only cost is the API call when you run it.

Use `-v` for failure diagnostics — it prints the actual tool-call list and the first 200 chars of the response.

## Non-determinism

Model responses vary, so fixtures should assert on structural properties (which tools got called, what state ended up in storage, key strings in output) rather than exact prose. If a fixture flakes intermittently, it's usually because the assertion is too tight — loosen `response_contains` to a more invariant phrase, or replace prose checks with state checks.
