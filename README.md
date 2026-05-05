# reflection-skill

A portable agent skill for journaling stream of consciousness and reflecting on it through interpretive lenses (Buddhism, Gnosticism, etc.). Entries are immutable; lenses produce separate annotation overlays that never modify the source.

## Layout

```
SKILL.md                          # Runtime-agnostic conceptual core
references/
├── TAXONOMY.md                   # Belief-system taxonomy
├── LENSES.md                     # Lens index and contribution guide
├── LENS_APPLICATION_ENGINE.md    # How lenses interpret entries
└── lenses/
    ├── buddhism.md
    └── gnosticism.md
adapters/
├── README.md                     # Capability matrix and composition rules
├── storage/                      # Where data lives
├── triggering/                   # When the skill engages
├── scheduling/                   # Whether/how it runs unprompted
└── cross-skill-state/            # Shared resources across skills
DEVELOPMENT.md                    # Working on the skill
CONTRIBUTING.md                   # Contribution process (esp. new lenses)
```

## Portable Design

The skill has a runtime-agnostic core (`SKILL.md` + `references/`) and a set of pluggable adapters (`adapters/`) along four orthogonal axes: storage, triggering, scheduling, and cross-skill state. Different runtimes — OpenClaw, Anthropic's claude.ai, future runtimes — pick adapters that fit their capabilities. The conceptual core does not change.

See [`adapters/README.md`](adapters/README.md) for the capability matrix and concrete deployment examples (OpenClaw and Anthropic project).

## Two Concrete Deployments

### OpenClaw

- **Storage:** `local-fs` rooted at `~/.openclaw/reflection/`
- **Triggering:** `every-message-hook` installed in `AGENTS.md`
- **Scheduling:** `heartbeat` in `HEARTBEAT.md`
- **Cross-skill state:** `shared-file` at `~/.openclaw/entities.json`

Captures silently from every message, prompts daily and weekly, integrates with the broader OpenClaw entity registry. This preserves the original behavior of the skill before the portable refactor.

### Anthropic project

- **Storage:** `google-drive`, folder shared with Claude
- **Triggering:** `project-default` — the skill is the project's default
- **Scheduling:** `user-initiated` — no scheduler, every behavior has a user-initiated equivalent
- **Cross-skill state:** `none`

The user creates a Claude project and attaches the skill. Inside the project, every message is treated as a potential capture. Daily and weekly reflections happen on demand: "give me a Buddhist reading of this week" produces the same result a fired heartbeat would have.

## Working with the Skill

- Edit `SKILL.md` for conceptual changes that apply everywhere.
- Edit files under `adapters/[axis]/[name].md` for runtime-specific behavior.
- Add new adapters by creating a new file under the appropriate axis directory and updating `adapters/README.md`.
- See [`DEVELOPMENT.md`](DEVELOPMENT.md) for development conventions and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the lens contribution process.
