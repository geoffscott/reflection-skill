#!/usr/bin/env python3
"""
Automated tests for the reflection skill.

Loads SKILL.md + references as the system prompt (with prompt caching), mocks
the storage adapter operations as tools, runs each fixture against the Claude
API, and asserts on tool-call sequences, final storage state, and response
text.

Usage
-----
    python test/run_tests.py                      # run all suites
    python test/run_tests.py capture              # run one suite
    python test/run_tests.py --fixture <name>     # run one fixture by name
    python test/run_tests.py --model claude-sonnet-4-6   # cheaper model

Set ANTHROPIC_API_KEY in your environment.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = REPO_ROOT / "SKILL.md"
REFERENCES = REPO_ROOT / "references"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

DEFAULT_MODEL = "claude-opus-4-7"
MAX_TOKENS = 4096
MAX_TURNS = 12


def load_system_blocks() -> list[dict]:
    """Build the system prompt as a single cacheable text block."""
    parts: list[tuple[str, str]] = [
        ("SKILL.md", SKILL_MD.read_text()),
        ("references/TAXONOMY.md", (REFERENCES / "TAXONOMY.md").read_text()),
        ("references/LENSES.md", (REFERENCES / "LENSES.md").read_text()),
        ("references/LENS_APPLICATION_ENGINE.md", (REFERENCES / "LENS_APPLICATION_ENGINE.md").read_text()),
    ]
    for lens in sorted((REFERENCES / "lenses").glob("*.md")):
        parts.append((f"references/lenses/{lens.name}", lens.read_text()))

    body = "\n\n".join(
        f'<file path="{path}">\n{contents}\n</file>' for path, contents in parts
    )
    preamble = (
        "You are running the reflection skill. The skill files below are your "
        "active instructions; follow them as if they were loaded from disk. "
        "Use the provided storage adapter tools for every read or write — do "
        "not invent file paths and do not synthesize entries from memory. When "
        "applying lenses, always read entries fresh via the tools."
    )
    return [
        {
            "type": "text",
            "text": preamble + "\n\n" + body,
            "cache_control": {"type": "ephemeral"},
        }
    ]


TOOLS: list[dict] = [
    {
        "name": "read_entry_for_date",
        "description": "Storage adapter: read the journal entry for the given date. Returns entry contents (markdown) or null if no entry exists for that date.",
        "input_schema": {
            "type": "object",
            "properties": {"date": {"type": "string", "description": "YYYY-MM-DD"}},
            "required": ["date"],
        },
    },
    {
        "name": "append_to_entry_for_date",
        "description": "Storage adapter: append a captured moment to the entry for a date. Creates the entry with frontmatter on first call of the day; otherwise appends a new `## HH:MM` section. Use this for all normal capture writes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "description": "HH:MM in the user's local timezone"},
                "content": {"type": "string", "description": "Cleaned moment text. Do not include the `## HH:MM` header — the adapter adds it."},
            },
            "required": ["date", "time", "content"],
        },
    },
    {
        "name": "write_entry_for_date",
        "description": "Storage adapter: overwrite the full entry for a date. Used only for migrations and historical imports. Never use this for normal capture — use append_to_entry_for_date instead.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "content": {"type": "string", "description": "Full markdown body including frontmatter."},
            },
            "required": ["date", "content"],
        },
    },
    {
        "name": "list_entries_in_date_range",
        "description": "Storage adapter: list dates that have entries in the inclusive [start_date, end_date] range. Returns a list of YYYY-MM-DD strings, sorted ascending.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "read_annotation",
        "description": "Storage adapter: read a saved lens annotation for a (range_key, lens) pair. Returns the markdown or null if not yet written.",
        "input_schema": {
            "type": "object",
            "properties": {
                "range_key": {"type": "string", "description": "e.g. '2026-W18' for a week, 'YYYY-MM-DD' for a day, or 'YYYY-MM-DD..YYYY-MM-DD' for an arbitrary range."},
                "lens": {"type": "string", "description": "lens name, e.g. 'buddhism'"},
            },
            "required": ["range_key", "lens"],
        },
    },
    {
        "name": "write_annotation",
        "description": "Storage adapter: persist an annotation produced by the lens application engine.",
        "input_schema": {
            "type": "object",
            "properties": {
                "range_key": {"type": "string"},
                "lens": {"type": "string"},
                "content": {"type": "string", "description": "Full markdown annotation including the metadata footer."},
            },
            "required": ["range_key", "lens", "content"],
        },
    },
    {
        "name": "read_config",
        "description": "Storage adapter: read the skill's saved configuration. Returns the config object or null on first run.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "write_config",
        "description": "Storage adapter: persist the skill's configuration.",
        "input_schema": {
            "type": "object",
            "properties": {"config": {"type": "object"}},
            "required": ["config"],
        },
    },
]


@dataclass
class MockState:
    entries: dict[str, str] = field(default_factory=dict)
    annotations: dict[tuple[str, str], str] = field(default_factory=dict)
    config: Any = None
    metadata: Any = None
    tool_calls: list[dict] = field(default_factory=list)

    def handle(self, name: str, args: dict[str, Any]) -> Any:
        self.tool_calls.append({"tool": name, "args": args})
        if name == "read_entry_for_date":
            return self.entries.get(args["date"])
        if name == "append_to_entry_for_date":
            date, time, content = args["date"], args["time"], args["content"]
            existing = self.entries.get(date)
            if existing is None:
                existing = f"---\ndate: {date}\n---\n"
            self.entries[date] = existing + f"\n## {time}\n\n{content.rstrip()}\n"
            return "ok"
        if name == "write_entry_for_date":
            self.entries[args["date"]] = args["content"]
            return "ok"
        if name == "list_entries_in_date_range":
            start, end = args["start_date"], args["end_date"]
            return sorted(d for d in self.entries if start <= d <= end)
        if name == "read_annotation":
            return self.annotations.get((args["range_key"], args["lens"]))
        if name == "write_annotation":
            self.annotations[(args["range_key"], args["lens"])] = args["content"]
            return "ok"
        if name == "read_config":
            return self.config
        if name == "write_config":
            self.config = args["config"]
            return "ok"
        raise ValueError(f"unknown tool: {name}")


def run_fixture(
    client: anthropic.Anthropic,
    model: str,
    system: list[dict],
    fixture: dict,
) -> tuple[MockState, str]:
    state = MockState(
        entries=dict(fixture.get("preload_entries", {})),
        annotations={
            tuple(k.split("|", 1)): v
            for k, v in fixture.get("preload_annotations", {}).items()
        },
        config=fixture.get("preload_config"),
    )

    user_text = fixture["message"]
    pin_lines = []
    if "today" in fixture:
        pin_lines.append(f"For this conversation, today's date is {fixture['today']}.")
    if "now_time" in fixture:
        pin_lines.append(f"The current local time is {fixture['now_time']}.")
    if pin_lines:
        user_text = "[Test harness: " + " ".join(pin_lines) + "]\n\n" + user_text

    messages: list[dict] = [{"role": "user", "content": user_text}]
    final_text_parts: list[str] = []

    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        for block in response.content:
            if block.type == "text":
                final_text_parts.append(block.text)

        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                try:
                    result = state.handle(block.name, block.input)
                except Exception as e:
                    result = {"error": f"{type(e).__name__}: {e}"}
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    return state, "\n".join(final_text_parts)


def evaluate(fixture: dict, state: MockState, final_text: str) -> list[str]:
    failures: list[str] = []
    actual_tools = [c["tool"] for c in state.tool_calls]

    for required in fixture.get("must_call", []):
        if required not in actual_tools:
            failures.append(f"missing required tool call: {required}")

    for forbidden in fixture.get("must_not_call", []):
        if forbidden in actual_tools:
            failures.append(f"called forbidden tool: {forbidden}")

    expected_seq = fixture.get("expected_tool_sequence")
    if expected_seq:
        i = 0
        for tool in actual_tools:
            if i < len(expected_seq) and tool == expected_seq[i]:
                i += 1
        if i < len(expected_seq):
            failures.append(
                f"tool subsequence not found: expected {expected_seq}, got {actual_tools}"
            )

    if "exact_tool_count" in fixture:
        for tool, n in fixture["exact_tool_count"].items():
            actual_n = sum(1 for t in actual_tools if t == tool)
            if actual_n != n:
                failures.append(f"tool {tool}: expected {n} calls, got {actual_n}")

    for date, expected in fixture.get("expected_entries", {}).items():
        actual = state.entries.get(date)
        if actual is None:
            failures.append(f"expected entry for {date}, none written")
            continue
        for needle in expected.get("contains", []):
            if needle not in actual:
                failures.append(f"entry {date} missing {needle!r}")
        for needle in expected.get("not_contains", []):
            if needle in actual:
                failures.append(f"entry {date} contains forbidden {needle!r}")

    for date in fixture.get("expected_no_entry_changes", []):
        before = (fixture.get("preload_entries") or {}).get(date)
        after = state.entries.get(date)
        if before != after:
            failures.append(
                f"entry {date} should be unchanged but differs (preload={before!r}, after={after!r})"
            )

    for ann in fixture.get("expected_annotations", []):
        lens = ann["lens"]
        range_key = ann.get("range_key")
        if range_key is not None:
            actual = state.annotations.get((range_key, lens))
            if actual is None:
                failures.append(
                    f"expected annotation for ({range_key}, {lens}), none written"
                )
                continue
        else:
            matches = [v for (rk, ln), v in state.annotations.items() if ln == lens]
            if not matches:
                failures.append(f"expected annotation for lens={lens}, none written")
                continue
            actual = matches[0]
        for needle in ann.get("contains", []):
            if needle not in actual:
                failures.append(
                    f"annotation lens={lens} range={range_key} missing {needle!r}"
                )
        for needle in ann.get("not_contains", []):
            if needle in actual:
                failures.append(
                    f"annotation lens={lens} range={range_key} contains forbidden {needle!r}"
                )

    for needle in fixture.get("response_contains", []):
        if needle.lower() not in final_text.lower():
            failures.append(f"response missing {needle!r} (case-insensitive)")

    for needle in fixture.get("response_not_contains", []):
        if needle.lower() in final_text.lower():
            failures.append(f"response contains forbidden {needle!r}")

    return failures


def run_suite(
    client: anthropic.Anthropic,
    model: str,
    system: list[dict],
    suite_name: str,
    fixtures: list[dict],
    verbose: bool,
) -> tuple[int, int]:
    print(f"\n=== {suite_name} ({len(fixtures)} fixtures) ===")
    passed = 0
    for fixture in fixtures:
        name = fixture["name"]
        try:
            state, text = run_fixture(client, model, system, fixture)
            failures = evaluate(fixture, state, text)
            if not failures:
                print(f"  PASS  {name}")
                passed += 1
            else:
                print(f"  FAIL  {name}")
                for f in failures:
                    print(f"        - {f}")
                if verbose:
                    print(f"        tool_calls: {[c['tool'] for c in state.tool_calls]}")
                    print(f"        response: {text[:200]!r}")
        except anthropic.APIError as e:
            print(f"  ERROR {name}: API {type(e).__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
    return passed, len(fixtures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("suite", nargs="?", help="run only one suite (e.g. capture)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--fixture", help="run only the named fixture")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if not FIXTURES_DIR.exists():
        print(f"no fixtures directory at {FIXTURES_DIR}", file=sys.stderr)
        return 2

    client = anthropic.Anthropic()
    system = load_system_blocks()

    if args.suite:
        suite_files = [FIXTURES_DIR / f"{args.suite}.json"]
        if not suite_files[0].exists():
            print(f"no such suite: {args.suite}", file=sys.stderr)
            return 2
    else:
        suite_files = sorted(FIXTURES_DIR.glob("*.json"))

    total_passed = 0
    total = 0
    for suite_path in suite_files:
        fixtures = json.loads(suite_path.read_text())
        if args.fixture:
            fixtures = [f for f in fixtures if f["name"] == args.fixture]
            if not fixtures:
                continue
        passed, n = run_suite(
            client, args.model, system, suite_path.stem, fixtures, args.verbose
        )
        total_passed += passed
        total += n

    print(f"\n=== Total: {total_passed}/{total} ===")
    return 0 if total_passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
