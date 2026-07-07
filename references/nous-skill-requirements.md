# Nous Research — Skill System Requirements

Source: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

Key requirements from the official docs that skilllab should enforce during audit/critique.

## Frontmatter Requirements

### Required Fields
- `name` (1-64 chars, lowercase `[a-z0-9-]`, matches directory name)
- `description` (1-1024 chars, non-empty, includes trigger keywords)

### Hermes-Specific Metadata (`metadata.hermes`)
- `tags: [str]` — array of tag strings for `skills_list` grouping
- `category: str` — controls `skills_list` category grouping. Must be a recognized category
- `config: [{key, description, default}]` — env var declarations for `hermes config migrate/show`
- `fallback_for_toolsets: [str]` — conditional activation (show when toolset unavailable)
- `requires_toolsets: [str]` — conditional activation (show when toolset available)
- `fallback_for_tools: [str]` — same, for individual tools
- `requires_tools: [str]` — same, for individual tools

### Optional Fields
- `platforms: [macos | linux | windows]` — OS restriction. Omit = all platforms
- `required_environment_variables:` — formal declaration for secure setup prompts
- `source:` — URL for skills synced from external repos
- `triggers:` — trigger phrases (enables slash command discovery)

### Anti-Patterns
- `category:` at top level → silently ignored, must be `metadata.hermes.category`
- `tags:` only at top level → works but misses Hermes grouping
- Env vars only in body table, not in `metadata.hermes.config` → D1-4 deduction
- `tools:` instead of `allowed-tools:` → silently ignored
- Name with spaces/uppercase → may fail matching
- Name doesn't match directory → activation mismatch

## Directory Structure

```
~/.hermes/skills/<name>/
├── SKILL.md          # Required — main instructions
├── references/       # Additional docs (loaded on demand)
├── templates/        # Output formats
├── scripts/          # Helper scripts
└── assets/           # Supplementary files
```

- No ad-hoc subdirectories
- `includes:` should list `references/**` and `scripts/**` if those directories exist
- Reference files over 100 lines should have a table of contents
- File references one level deep from SKILL.md (A→B→C chains are a D4 failure)

## Progressive Disclosure (Three-Layer Architecture)

- **Layer 1:** Metadata (~100 tokens) — always in context at catalog scan
- **Layer 2:** SKILL.md (<5k tokens) — loaded on skill activation
- **Layer 3:** References (unloaded) — on-demand, per-file, only when relevant

SKILL.md body should be under 500 lines, ideally under 5000 tokens.

## Support File Maps

Must use a "When to read" column with conditional language:
- "Before [action]" — e.g., "Before running genie.py"
- "During [phase]" — e.g., "During Phase 2 discovery"
- "When [condition]" — e.g., "When bot detection blocks access"
- "If [situation]" — e.g., "If VPN is blocked"

Static topic descriptions (e.g., "API error reference") are a D8-3 deduction.

## Skill Bundles

Bundles are YAML files at `~/.hermes/skill-bundles/<slug>.yaml`:
```yaml
name: backend-dev
description: Backend feature work
skills:
  - github-code-review
  - test-driven-development
instruction: |
  Always start by writing failing tests.
```

Fields: `name`, `description`, `skills` (required), `instruction` (optional).

## Conditional Activation

Skills can auto-show/hide based on tool availability:
- `fallback_for_toolsets: [web]` — shown when web toolset is unavailable
- `requires_toolsets: [terminal]` — shown when terminal toolset is available

## Platform-Specific Skills

```yaml
platforms: [macos]        # macOS only
platforms: [macos, linux] # macOS and Linux
```

When set, skill is hidden from `skills_list()` and slash commands on incompatible platforms.

## Secure Setup on Load

Skills can declare required env vars for secure prompting:
```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

## Publishing (agentskills.io)

- agentskills.io discovers skills from GitHub repos (no submission API)
- Remove non-standard Hermes extensions before publishing: `metadata.hermes`, `metadata.email` → `metadata.author`, `metadata.openclaw` (legacy), top-level `version` → `metadata.version`
- Required: `name` and `description` in frontmatter
