# skilllab

Skill library maintenance: audit, merge, rename, delete, consolidate, publish, sanitize, and critique.

Manages the full lifecycle of skills in a Hermes Agent environment.

## What it does

- **Audit** — scan for orphans, author gaps, broken frontmatter
- **Critique** — score skills against the 10-dimension rubric, generate improvement plans, run iterative fix loops (merged from ocas-critique)
- **Merge** — consolidate overlapping skills into class-level umbrellas
- **Rename** — move a skill directory and update its name field
- **Delete** — archive a skill to `.archive/`
- **Publish** — push a skill to GitHub for agentskills.io
- **Sanitize** — extract inline credentials to reference files
- **Hygiene** — check for grep false-positives and stale references
