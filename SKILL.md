---
name: ocas-skilllab
description: >
  Skill library maintenance: audit, merge, rename, delete, consolidate, publish,
  sanitize, and critique skills. Interactive menu via clarify tool.
  Use when the user asks to clean up the skill library, merge
  overlapping skills, rename skills to follow naming conventions, delete auto-generated
  or stale skills, audit skills for authorship, publish skills to external registries,
  sanitize skills for security scanner compliance, score skills against the 10-dimension
  rubric, generate improvement plans, or run autonomous library grinding.
  Also covers frontmatter conventions
  and how to identify skills by type (ocas-*, util-*, protected, auto-generated).
license: MIT
metadata:
  author: Indigo Karasu (indigokarasu)
  version: "3.1.5"
  merged-from: ocas-critique
source: https://github.com/indigokarasu/skilllab
includes:
  - references/**
  - scripts/**

triggers:
  - skilllab
  - audit skills
  - clean up skills
  - merge skills
  - rename skill
  - delete skill
  - skill library
  - consolidate skills
  - frontmatter check
  - publish skill
  - sanitize skill
  - skill has secrets
  - security scan
  - credential refactor
  - remove inline credential references
  - critique skill
  - score skill
  - evaluate skill
  - skill review
  - skill scoring
  - rubric evaluation
  - 10khr
  - grind
  - improve skill
---

# skilllab

Skill library maintenance: audit, merge, rename, delete, consolidate, publish, sanitize.

The library should contain class-level instruction umbrellas — not hundreds of narrow one-session micro-skills. When merging, prefer one broad skill with labeled subsections over five narrow siblings.

## Interactive Menu

When invoked interactively, present a menu using the `clarify` tool. This gives the user keyboard-navigable selection without leaving the agent session.

Available actions:

1. **Audit** — scan for orphans, author gaps, broken frontmatter
2. **Critique** — score a skill against the 10-dimension rubric, generate improvement plans
3. **Merge** — consolidate overlapping skills
4. **Rename** — move a skill directory and update its name field
5. **Delete** — archive a skill to `.archive/`
6. **Publish** — push a skill to GitHub for agentskills.io
7. **Sanitize** — extract inline credentials to reference files
8. **Hygiene** — check for grep false-positives and stale references
9. **Exit** — close the menu

After the user selects an action, execute it, then present the menu again. Loop until the user chooses Exit or sends `/stop`.

See `references/clarify-interactive-menu.md` for the full clarify-based menu pattern (basic menu loop, sub-menus, dynamic choices, confirmation dialogs, pitfalls).

## Table of Contents

1. [Skill Taxonomy](#1-skill-taxonomy)
2. [Audit Procedure](#2-audit-procedure)
3. [Critique Procedure](#3-critique-procedure)
4. [Merge / Consolidate Procedure](#4-merge--consolidate-procedure)
5. [Rename Procedure](#5-rename-procedure)
6. [Publish Procedure](#6-publish-procedure)
7. [Sanitize Procedure](#7-sanitize-procedure)
8. [Frontmatter Standards](#8-frontmatter-standards)
9. [Pitfalls](#9-pitfalls)
10. [Retired Capability Cleanup](#10-retired-capability-cleanup)

---

## 1. Skill Taxonomy

### Naming Conventions
- `ocas-*` — OCAS family. Authored by Indigo Karasu. Includes meta-skills that manage the skill library itself.
- `util-*` — Utility skills authored by Indigo Karasu.
- `skilllab` — Meta-skill for skill library management (this skill).
- No prefix — Base/generic skills. May have external authors or no author metadata.

**IMPORTANT:** Do NOT arbitrarily rename skills to `ocas-*` or `util-*` unless explicitly told to by the user.

### Directory Layout
- Top-level `~/.hermes/skills/<name>/` is the default for all skills.
- `infrastructure/` is reserved for server/host infrastructure skills only (networking, OS-level services, deployment). Do NOT use it as a miscellaneous subdirectory for utilities or meta-skills.
- If a skill doesn't fit `ocas-*` or `util-*` and isn't truly infrastructure, place it at the top level.

### Skill Location
Skills may live at any depth under `~/.hermes/skills/`:
- Top-level: `~/.hermes/skills/util-github/SKILL.md`
- Subdirectory: `~/.hermes/skills/infrastructure/util-hermes-ops/SKILL.md`

Use `glob.glob("~/.hermes/skills/**/SKILL.md", recursive=True)` to find all skills. Do NOT assume flat layout.

### Protected Skills (DO NOT edit)
- Bundled skills shipped with Hermes (e.g., `hermes-s6-container-supervision`, `kanban-codex-lane`)
- Hub-installed skills (`hermes-agent`, etc.)

### Auto-Generated Skills (DELETE when found)
Any skill with `metadata.hermes.generated_by` in its frontmatter is an auto-generated wrapper. Delete immediately.

### Author Field Location
Check TWO places: top-level `author:` and nested `metadata.author:`.

---

## 2. Audit Procedure

### Check for Auto-Generated Skills
```bash
grep -r "generated_by" ~/.hermes/skills/ ~/.hermes/profiles/indigo/skills/ --include="*.md" -l 2>/dev/null
```

### Check for Author Coverage

**Do NOT use line-level grep for `author:`.** It matches prose containing "authorization", "authoritative", etc. at the same indent. Use a YAML parser instead:

```python
import yaml, glob, os

# Check BOTH locations — default profile and indigo profile
search_roots = [
    os.path.expanduser("~/.hermes/skills"),
    os.path.expanduser("~/.hermes/profiles/indigo/skills"),
]
for root in search_roots:
    for path in glob.glob(f"{root}/**/SKILL.md", recursive=True):
        if ".archive" in path:
            continue
        with open(path) as f:
            parts = f.read().split("---")
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                if not isinstance(fm, dict):
                    print(f"YAML ERR: {path}")
                    continue
                author = (fm.get("metadata") or {}).get("author") or fm.get("author")
                name = fm.get("name", "")
                if not author:
                    print(f"NO AUTHOR: {path} (name={name})")
            except Exception as e:
                print(f"YAML ERR: {path} ({e})")
```

If you must use grep, verify every match falls between `---` delimiters (YAML frontmatter context), not in the markdown body. See `references/audit-2026-05-30.md` for a concrete false-positive example.

### Check for YAML Errors

Invalid YAML frontmatter makes skills invisible to `skills_list`/`skill_view`. Common causes:
- Unescaped markdown in `description:` fields (e.g., `**bold**` or `''italic''` that YAML interprets as flow indicators)
- Bare `---` delimiters inside the document body (not fenced in code blocks)
- Unquoted special characters (`:`, `#`, `*`, `&`, `!`) at the start of description values

**Fix:** Read the raw file, identify the problematic line in the frontmatter, and either quote the value or escape the special characters. For `description:` fields containing markdown, wrap the entire value in single quotes or use the `>-` block scalar.

### Check for Empty Profile Stubs

The default profile (`~/.hermes/skills/`) may contain empty category directories (DESCRIPTION.md stubs with no SKILL.md). These are not skills — they're artifacts from hub installs. During audit, distinguish:
- **Real skill directories:** contain a `SKILL.md` file
- **Empty stubs:** contain only `DESCRIPTION.md` or are completely empty

Empty stubs should be reported as hygiene issues, not counted as skills. Do NOT try to "fix" them — just flag for user review.

### Check for SOUL Repo Install Gap

Skills written to `/root/soul/skills/` are NOT visible to the agent until copied to `~/.hermes/profiles/indigo/skills/`. During audit, compare both directories:

```bash
diff <(ls /root/soul/skills/ | sort) <(ls ~/.hermes/profiles/indigo/skills/ | sort)
```

Any skill in `/root/soul/skills/` missing from the active profile is an install gap. Copy it over immediately. See `references/soul-repo-skill-install-gap.md`.

### Check for Orphaned Reference Files

Skills accumulate reference files over time that are no longer linked from the SKILL.md support file map. During audit, cross-reference:

```bash
# Quick check for a single skill:
comm -23 <(ls <skill_dir>/references/*.md 2>/dev/null | sort) <(grep -oP 'references/\\S+' <skill_dir>/SKILL.md | sed 's/[`.,;:]$//' | sort -u)
```

Orphaned references are not Critical — they don't break the skill. But 100+ orphans across the library signals drift. Flag skills with >10 orphaned references for cleanup.

### Check for Support File Map Completeness

The SKILL.md's Support File Map (or equivalent table) claims to be the canonical index of all reference files and scripts. Audit it against reality:

1. **Duplicate entries** — same file listed twice (copy-paste error during merge)
2. **Phantom references** — listed in map but NOT on disk (stale entry, file was deleted or renamed)
3. **Orphaned files** — on disk but NOT in map (file added but map never updated)
4. **Directory-as-reference** — map entry points to a directory path instead of a specific file (malformed entry)
5. **Body-only references** — referenced in SKILL.md prose but missing from the map (map is incomplete)

A clean Support File Map should have zero duplicates, zero phantoms, and every file on disk should be either in the map or confirmed as intentionally unmapped (e.g., `.archive/` contents).

---

## 3. Critique Procedure

Evaluate skills against a 10-dimension rubric, generate improvement plans, and run iterative fix loops.
Merged from `ocas-critique` (v2.6.0).

### When to Use

- Reviewing, critiquing, or auditing a skill
- Iterating a skill toward a target score
- Pre-publish quality gate before syncing to GitHub
- Batch-auditing a skill library
- Autonomous library-wide improvement ("10khr", "grind")

### Quick Reference

| Command | What it does |
|---------|-------------|
| `critique.assess <path>` | Score only, no changes |
| `critique.plan <path>` | Score + improvement plan |
| `critique.run <path>` | Full pipeline (score → fix → verify) |
| `critique.iterate <path>` | Fix-verify loop until 50/50 |
| `critique.batch [paths]` | Assess multiple skills, ranked table |
| `critique.perfect <skill>` | Grind one skill to 50/50 |
| `critique.10khr` | Autonomous library grinding |
| `critique.10khr --report-only` | Score all, no grinding |

### Procedure

**Phase 1 — Read:** Read the full SKILL.md, all reference files, all scripts. Measure line count (flag if >500). Check for phantom references. **Scan Pitfalls/What NOT to Do sections for absolute prohibitions that may encode failed attempts rather than confirmed hard constraints** — see Pitfall "Absolute prohibitions encoding failed attempts."

**Phase 2 — Score:** Measure code ratio first (`python3 scripts/critique_code_ratio.py <path>/SKILL.md`). Target: under 20%. Evaluate each dimension 1-5 using `references/critique-rubric.md`. Print the score table. Bands: A=40-50, B=30-39, C=20-29, D=10-19, F=0-9.

**Phase 3 — Categorize:** For each dimension scoring ≤3, classify every issue:
- **Critical** — blocks loading/runtime (missing name/description, invalid YAML, broken paths, phantom references)
- **Major** — degrades effectiveness (vague description, wrong voice, SKILL.md >500 lines, missing When to Use/NOT to Use, no Gotchas, code ratio >30%)
- **Minor** — polish (style preferences, optional enhancements)

Use `references/critique-issue-categorization.md` for full rules.

**Phase 4 — Plan:** For each issue, document: Location, Current state, Fix, Impact (+N points). Group: Critical → Major → Minor. Use `references/critique-improvement-plan-template.md`.

**Phase 5 — Execute:** Critical → fix immediately. Major → fix unless documented deferral. Minor → evaluate with 3 questions (genuine improvement? false positive? helps the agent?), then apply if all pass. Use `patch` for targeted edits. Verify syntax after each change. **Full-file rewrite strategy:** When extracting multiple inline sections to references in one pass (3+ sections or >50 lines moved), prefer a `write_file` rewrite of the entire SKILL.md over sequential `patch` calls. Sequential patches cause line-number drift, eaten headings, and duplicate sections — always `grep -n '^## '` after structural patches. When moving code blocks to reference files, scan for absolute paths (`/root/`, `/home/`, `/etc/`) and replace with `{agent_root}/`. Verify cross-skill paths exist before embedding them.

**Phase 6 — Verify:** Re-read modified SKILL.md. Re-score affected dimensions. Confirm all Critical/Major resolved. Print before/after comparison. Run quick checklist at `references/critique-audit-checklist.md`.

### Iteration Loop

Repeat Phases 1-6 until quality bar is met. Default: all Critical/Major resolved, score ≥35. Completion marker: `<critique-complete>`.

**Rationalizations to reject:**
- "I'll mark it complete and come back later" — fix now
- "This minor seems wrong, I'll skip all" — evaluate each one
- "The rubric is too strict" — the bar exists for a reason
- "It's good enough" — if Major issues remain, it's not

### 10khr Mode

Assess ALL skills before fixing any. Do not cherry-pick.

1. Run Bulk D1 Check (missing includes:, invalid license) as pre-pass
2. Read every SKILL.md fully
3. Score all 10 dimensions for each skill
4. Rank all skills by score
5. Fix the single lowest-scoring skill
6. Re-assess and repeat

The heuristic scorer (`python3 scripts/critique_10khr_runner.py`) over-scores by 6-10 points. Use for candidate ranking only. Always do manual assessment before fixing.

### Pitfalls

- **Be active, not passive**: Apply fixes, don't just report
- **Follow the rubric procedure — don't ad-hoc critique**: Execute full Phase 1-6. Ad-hoc critiques miss dimensions
- **Heuristic scorer over-confidence**: The 10khr runner uses keyword matching. After fixes, it won't reflect improvement — manually re-score and move to next
- **Don't cherry-pick skills**: Assess all → identify lowest → fix one → repeat
- **Read fully, don't skim-score**: Read entire SKILL.md, all references, all scripts before scoring
- **Batch speed vs. quality**: Parallel subagent fixes produce inconsistent quality. Single-agent Phase 1-6 produces better results for skills targeting 50/50

---

## 4. Merge / Consolidate Procedure

**Right test for consolidation:** "Would a human maintainer write this as N separate skills, or as one skill with N labeled subsections?" If the latter, merge.

### Prefix Clusters
Identify groups sharing a first word or domain keyword. For each cluster with 2+ members:

1. Identify the **umbrella** (broadest existing member, or create a new one)
2. Add labeled subsections for each sibling's unique insight
3. Demote narrow-but-valuable content to `references/`, `templates/`, or `scripts/`
4. Archive absorbed siblings into `~/.hermes/skills/.archive/`
5. Update `metadata.version` in the umbrella

### Three Consolidation Strategies

**a. Merge into existing umbrella** — Patch the broadest skill to add labeled sections, archive siblings.

**b. Create new umbrella** — Use `skill_manage action=create`, then archive absorbed siblings.

**c. Demote to support files** — Move narrow content to `references/`, `templates/`, or `scripts/` under the umbrella.

### Merge Steps (when absorbing skill B into skill A)
1. Copy B's scripts/references into A's `scripts/` and `references/` directories
2. Append B's SKILL.md content as a new Part/section in A's SKILL.md
3. Add `metadata.merged-from: <B-name>` to A's frontmatter
4. Add B's triggers to A's `triggers:` list
5. Archive B's entire directory to `~/.hermes/skills/.archive/<B-name>/`
6. Update all references (cron jobs, SOUL.md, memory, other skills, cron prompts)

### Package Integrity
Before archiving, inspect the source as a **complete directory package** (may include `references/`, `templates/`, `scripts/`, `assets/`). If it has support files or relative links:
- Re-home every needed support file into the umbrella's canonical directories AND rewrite paths, OR
- Archive the entire original package unchanged.

**Never** flatten only SKILL.md into `references/` while leaving support files behind.

---

## 5. Rename Procedure

```bash
mv ~/.hermes/skills/<old-name> ~/.hermes/skills/<new-name>
```

Then update:
1. Inside SKILL.md: `name:` field, top-level heading, any self-references
2. `~/.hermes/.skills_prompt_snapshot.json` — rename the cached key (Python: load JSON, rename key, dump)
3. `~/.hermes/skills/.usage.json` — rename the tracking key (same pattern)
4. Support file map in the skill itself
5. Any other SKILL.md files that reference the old name

**Lesson (May 2026):** Renaming without updating `.skills_prompt_snapshot.json` and `.usage.json` leaves stale cache entries. The old name persists in the injected system prompt until the next full session refresh.

---

## 6. Publish Procedure

Publish skills to external registries (agentskills.io, LobeHub, Anthropic).

### agentskills.io Spec Requirements

agentskills.io **discovers skills from GitHub repos** — no direct submission API.

**Required frontmatter fields:** `name` (1-64 chars, lowercase `[a-z0-9-]`, matches directory) and `description` (1-1024 chars, includes trigger keywords).

**Non-standard Hermes extensions to remove:** `metadata.hermes`, `metadata.email` → `metadata.author`, `metadata.openclaw` (legacy), top-level `version` → `metadata.version`, `self_update`.

Full spec compliance checklist: see `references/skill-publish-spec-compliance-checklist.md`.

### Publishing Workflow
1. Audit and fix spec compliance
2. Sanitize private data (replace PII with placeholders)
3. Create GitHub repo: `gh repo create indigokarasu/skill-name --private --description "..."`
4. Add LICENSE, README.md, .gitignore
5. Clone, copy files, commit, push
6. For public skills: `gh repo edit indigokarasu/skill-name --visibility public`

### Quality & Security Evaluation
See `references/skill-publish-agentskill-evaluation-criteria.md` for the agentskill.sh 100/100 scoring pattern.

### GitHub Mechanics
- Full push recipe: `references/skill-publish-github-push-recipe.md`
- Bulk sync workflow for existing repos: `references/skill-publish-github-sync-existing-skills.md`

---

## 7. Sanitize Procedure

Remove inline credential references from SKILL.md files by extracting secrets into dedicated `references/` files.

### What Counts as a Credential Reference
**Extract:** API keys, OAuth tokens, client IDs, client secrets, account names, credential file paths, absolute paths under `/root/`, `/home/`, `/etc/`.

**Leave inline:** Public service URLs, generic config keys without values, standard library package names, template variables like `{agent_root}`.

### Sanitize Steps
1. **Scan** — search for env vars ending in `_KEY`, `_SECRET`, `T# Skill Lab Scripts

Scripts for skill library maintenance: audit, critique, merge, sanitize.

| Script | Purpose |
|---|---|
| `scripts/skilllab.py` | Interactive skill library shell — audit, critique, merge, rename, delete, publish, sanitize |
| `scripts/critique_code_ratio.py` | Measure code-to-prose ratio in a SKILL.md file |
| `scripts/critique_10khr_runner.py` | Heuristic batch scorer for 10khr autonomous grinding (over-scores by 6-10pt) |EN`, OAuth fields, absolute paths
2. **Create reference file** — `references/<purpose>.md` with all credential details verbatim
3. **Replace inline** — collapse credential sections to `See references/<file>.md for <description>.`
4. **Check secondary locations** — Gotchas section, support file maps
5. **Update support file map** — add the new reference file
6. **Verify** — grep for remaining patterns

### Scanner False-Positive Patterns
See `references/skill-sanitize-checklist.md` for the full checklist. Key patterns:
- Literal `~/.hermes/` paths in descriptive/instructional context → replace with functional prose
- Word "Lock" in command descriptions → rephrase to "Mark as fixed"
- `curl https://api.github.com/...` → replace with `gh api ...`
- SKILL.md body > 500 lines → move detail to `references/`

### Pointer Language
**Good:** `See references/account-credentials.md for Google account isolation rules.`
**Bad:** `Credentials removed — see references/creds.md` (signals scanners that secrets exist nearby).

---

## 8. Frontmatter Standards

Minimum for authored skills:

````yaml
---
name: <skill-name>
description: >
  What it does. What triggers it. What it does NOT do.
license: MIT
metadata:
  author: Indigo Karasu (indigokarasu)
  version: "3.0.0"
includes:
  - references/**
  - scripts/**
triggers:
  - trigger-phrase-1
  - trigger-phrase-2
---
````

---

## 9. Pitfalls

- **Batch replace can double author fields:** `Indigo Karasu (indigokarasu)` → `Indigo Karasu (indigokarasu) (indigokarasu)`. Always verify after bulk replacements.
- **Don't arbitrarily prefix skills:** Only apply `ocas-*` or `util-*` when directed.
- **Skills in subdirectories:** Use recursive glob to find them all.
- **Frontmatter YAML examples must be fenced:** Wrap YAML examples in fenced code blocks. Never use bare `---` delimiters or unindented top-level YAML keys inside the document body — YAML parsers treat them as duplicate frontmatter.
- **Frontmatter YAML:** Use `patch` for targeted edits, not `write_file`. Validate after edits.
- **Over-sanitization:** Public URLs, standard packages, and config schemas without values are NOT credentials.
- **Preserve context:** When moving credentials to a reference file, include enough context for future agents.
- **Package integrity:** Never flatten only SKILL.md while leaving support files behind.
- **Style guides are not blockers:** When a skill provides writing/style guidance (like ocas-vibes), use it as a prose standard to apply during editing — not as a runtime dependency or invocation target. Do NOT wire other skills to call it as a mandatory step.
- **Audit logs should be name-neutral:** When retiring a capability, describe the action in the audit log without naming the archived entity. Don't leave breadcrumbs pointing to things that shouldn't be referenced anymore.
- **`infrastructure/` is not miscellaneous:** It is for server/host infrastructure only. Utilities and meta-skills go at the top level.
- **Don't grep for author: with line-level tools:** Use a YAML parser. grep false-positives on "authorization", "authoritative", etc.
- **MemPalace kg_add rejects special characters:** `@`, `/`, `.`, commas in object/subject fields cause silent failures. Sanitize strings before calling, or use `mempalace_add_drawer` for structured/profile data. See `references/mempalace-gotchas.md`.
- **Renaming skills requires gateway restart:** After renaming a skill directory, the old name persists in Hermes's `/` autocomplete and injected SKILL.md until you: (1) update all references in the skill body text, (2) clear `.skills_prompt_snapshot.json`, (3) restart the gateway via `hermes gateway restart`. Doing only #1 without #3 leaves stale autocomplete entries.
- **Skill directory name must match frontmatter `name:` field.** If a skill directory is renamed (e.g., `ocas-corvus` → `ocas-corvus-disabled`), the skill system cannot find it — `skills_list` and `skill_view` match on directory name, not frontmatter content. Cron jobs that reference the skill by name will silently fail to load it. Before renaming a skill directory, check all cron jobs, references, and the `.skills_prompt_snapshot.json` cache. To disable a skill without breaking references, keep the directory name intact and add a `status: disabled` field to frontmatter instead of renaming the directory.
- **Git merge conflict markers in skill files.** When a skill is synced from GitHub via `git pull` or `git merge` and there's a conflict, the file will contain unresolved markers (`<<<<<<< HEAD`, `=======`, `>>>>>>>`). These break YAML frontmatter parsing, making the skill invisible to `skills_list`/`skill_view`. During audit, check for these markers with `grep -r '<<<<<<<' <skills_dir> --include="*.md"`. To resolve: read both sides, pick the newer/more-complete version (usually "theirs"), and write the resolved file with `write_file`. The indigo profile copy and default profile copy may diverge — check both locations.
- **Section renumbering after insertion:** When inserting a new section (e.g., during a merge), ALL downstream section numbers and TOC entries must be incremented. Use `grep -n '^## '` to verify numbering is contiguous after any structural insert. Missing this causes broken TOC links and duplicate section numbers.
- **Interactive menu 4-choice limit:** The `clarify` tool supports max 4 visible choices (5th is always "Other"). For skills with >4 operations, either chunk into categories (first clarify picks category, second picks action) or list all operations in the menu text and use the first 4 as the most common, with "Other" capturing the rest. The menu text should list ALL operations for agent reference regardless of the 4-choice UI limit.
- **Always update at least one skill per session**: After any non-trivial session, look for at least one skill to update. "Nothing to save" is the exception, not the rule. Signals: user corrected style/tone/workflow, new technique discovered, loaded skill was wrong/missing steps, tool-usage pattern emerged.
- **`--skills-dir` arg not propagating:** The `critique_10khr_runner.py` accepts `--skills-dir` but the value was never passed to `find_ocas_skills()` or `run_full_assessment()` — they used the module-level `SKILLS_DIR` instead. Fixed 2026-06-14: both functions now accept an explicit `skills_dir` parameter, and `main()` wires the argument through. Always `grep SKILLS_DIR` after changing the default to confirm no stale references remain.
- **Sequential patch fragility during bulk extraction:** When moving multiple inline sections to `references/` in one pass, sequential `patch` calls corrupt the file (eaten headings, duplicates, line-number drift). Prefer a full-file `write_file` rewrite. Always `grep -n '^## '` after structural patches. Scan moved code for absolute paths (`/root/` → `{agent_root}/`) and verify cross-skill path existence.
- **Reference file path convention:** Design references live at `~/.hermes/references/design/`. If you find design refs at old paths like `/root/references/creative/`, migrate them to the design directory and update all pointers.
- **Post-migration reference drift**: After a backend migration (e.g., database engine change, API version upgrade), ALL reference files must be audited — not just code. Check every `.md` in `references/` for: stale imports, old DB paths, deprecated query languages, outdated CLI commands, and code examples that reference the removed backend. Orphaned reference files (not linked from SKILL.md's support file map) should be archived or deleted. This is a D10 (Completeness) failure pattern — the SKILL.md description says "SQLite" but the schema reference still documents the old engine.
- **Stale code examples in reference files**: When critiquing a skill, read the code examples in ALL referenced `.md` files — not just SKILL.md. Reference files often contain Python/Cypher/CLI examples that drift after migrations. A single stale `import real_ladybug` in a reference file is a Critical D10 finding.
- **Orphaned reference file detection**: During audit or critique, cross-reference the SKILL.md support file map against actual files in `references/`. Files on disk but not linked from SKILL.md are orphaned — archive them to `references/.archive/`. Quick check: `comm -23 <(ls references/*.md | sort) <(grep -oP 'references/\S+' SKILL.md | sed 's/[`.,;:]$//' | sort -u)`.
- **Category field discipline:** The `category:` frontmatter field controls `skills_list` grouping. Only `util-` prefixed skills should carry `category: utility`. Never add `category: utility` to non-util skills. When reorganizing the library, audit all `category:` fields and remove any that violate this rule.
- **Cron-aware skill deletion:** Before deleting a skill directory, check whether any cron jobs reference it. Run `cronjob action=list` and grep for the skill name. If found, either update the cron job to reference a different skill or delete the cron job first. Silently breaking cron jobs by deleting their referenced skill causes invisible failures that may not surface for days.
- **Profile ↔ monorepo sync gap:** Skills with a `source:` field pointing to a GitHub repo must have their profile copy (`~/.hermes/profiles/indigo/skills/<name>/`) and monorepo copy in sync. After any skill edit, run `diff` on both SKILL.md files before considering the session complete. The monorepo is canonical for `source:`-referenced skills.
- **Skill sprawl — prefer functions over new skills:** Before creating a new skill, check `skills_list` for an existing umbrella. If one exists, add a subsection or reference file instead. Style guides → reference inside the output skill. Single-channel integrations → module inside the comms skill. Prompt wrappers → reference file. Testing utilities → operational skills. Skills invoked by only one parent → sub-module of that parent. See `references/skill-architecture-sprawl-audit-2026-06-17.md` for the full audit and merge plan.
- **Audit must check both profiles:** The active skill library lives at `~/.hermes/profiles/indigo/skills/`, not `~/.hermes/skills/`. The default profile (`~/.hermes/skills/`) may contain empty stub directories from hub installs — these are NOT skills. Always audit the indigo profile path. Check both if the user asks for a full system audit.
- **Deletion marked but not executed — completion-reflex failure:** When a skill (or any task) is marked for deletion/repeatedly identified as needing deletion, execute immediately. Do not mark it mentally and move on. The `ocas-critique` skill was identified for deletion 5+ times over multiple sessions and was only deleted when Jared directly asked "didn't you already delete this?" — if a deletion is agreed upon, do it in the same session. This applies to all tasks: if the decision is made, execute before context switches.
- **Memory full — consolidate before adding:** When the memory tool returns "Memory at X/2,200 chars" errors, stop adding new entries. Consolidate first: merge overlapping entries, remove stale one-off task narratives, and reduce verbosity. Research details, Wikipedia corrections, and session-specific notes do not belong in memory — they belong in session transcripts. Memory is for durable facts: user preferences, environment details, tool quirks, and stable conventions.
- **"Don't say MEMORY.md" — structural fixes over memory reminders:** When Jared asks "how will you ensure you won't keep doing X?", the answer is NOT "remember this in memory." Memory is a speed bump, not a wall — it gets re-read as a directive and can cause repeated work. The answer should be: identify the structural fix that makes the mistake impossible (symlinks, path conventions, tool defaults). If the fix is already in place but you're still making the mistake, the issue is attention/awareness — slow down and check the system prompt's path conventions before acting.
- **YAML errors from unescaped markdown in frontmatter:** A `description:` field containing `**bold**`, `''italic''`, or unquoted special characters (`:`, `#`, `*`) breaks YAML parsing, making the skill invisible. During audit, catch YAML parse errors separately from missing fields — they're Critical (skill won't load at all). Fix by quoting the value or using `>-` block scalar.
- **Orphaned reference files accumulate silently:** Every session that adds a reference file but forgets to update the support file map creates drift. During audit, flag skills with >10 orphaned references. This is a hygiene issue, not Critical — but it makes the library harder to navigate and inflates the support file count.
- **Empty default-profile stubs are not skills:** Hub installs may leave empty category directories under `~/.hermes/skills/` (apple, creative, email, etc.) with only a `DESCRIPTION.md`. These are artifacts, not skills. Report them separately in audit output — do not count them as skills or flag them as missing authors.
- **Judging a skill by its name/description ("empty wrapper shell" anti-pattern):** An agent's highest-error move is to read only the skill's name + description, form a conclusion ("thin wrapper," "empty shell," "just delegates"), and then act on that conclusion without reading the SKILL.md body, references, or scripts. ocas-skilllab itself was called an "empty wrapper shell" — it is 350+ lines of procedure with 38 reference files and 3 scripts. Before evaluating or acting on any skill: read the FULL SKILL.md, all reference files, all scripts. The name and description are the front door, not the house. If you catch yourself using words like "wrapper," "shell," "thin," "just delegates" — stop, you are guessing. Read the full content. This applies doubly when deciding whether a skill is worth keeping, merging, or deleting.

---

## 10. Retired Capability Cleanup

When a capability is retired (archived, superseded, or removed), sweep all references:

1. **Identify** — `grep -r "old-name" ~/.hermes/skills/ --include="*.md"`
2. **Classify each reference:**
   - Prose mentioning old name → replace with successor or remove
   - Section about retired capability → remove or rewrite as historical note
   - Data values in state.db → leave alone (not a skill reference)
   - Audit logs recording what was done → leave alone (historical record)
3. **Rename support files** referencing the retired capability
4. **Update support file maps** in affected SKILL.md files
5. **Rename cache keys** in `.skills_prompt_snapshot.json` and `.usage.json`
6. **Verify** — re-grep to confirm zero remaining references (excluding `.archive/` and audit logs)

---

## Support File Map

| File | When to read |
|------|-------------|
| `references/audit-2026-05-30.md` | May 2026 audit — fixes, grep false-positive lesson, remaining issues |
| `references/auto-generated-skill-cleanup.md` | Before deleting auto-generated skill thin wrappers |
| `references/merge-session-2026-05-29.md` | May 2026 merge/cleanup session historical reference |
| `references/skill-publish-spec-compliance-checklist.md` | When auditing skills against agentskills.io spec |
| `references/skill-publish-github-push-recipe.md` | When publishing a new skill repo to GitHub |
| `references/skill-publish-github-sync-existing-skills.md` | When bulk-syncing local skills to existing GitHub repos |
| `references/skill-publish-agentskill-evaluation-criteria.md` | When evaluating skill quality/security scores |
| `references/skill-sanitize-checklist.md` | Post-sanitize verification checklist + scanner false-positives |
| `references/mempalace-gotchas.md` | MemPalace MCP tool constraints — kg_add character rejections, drawer vs. KG guidance |
| `references/audit-2026-06-05.md` | June 2026 audit — git merge conflict repair, cross-profile write guard, remaining author gaps |
| `references/audit-2026-06-18.md` | June 2026 audit — full library scan, 94 skills, 26 missing authors, YAML errors, orphaned refs |
| `references/critique-rubric.md` | During Phase 2 scoring — full 10-dimension rubric |
| `references/critique-issue-categorization.md` | During Phase 3 — Critical/Major/Minor rules |
| `references/critique-assessment-mode.md` | Before assessment — decision table for assess vs. fix |
| `references/critique-audit-checklist.md` | During Phase 6 — quick-pass compliance checklist |
| `references/critique-improvement-plan-template.md` | During Phase 4 — plan format and examples |
| `references/critique-usage-examples.md` | Before executing critique commands — score table format, code ratio |
| `references/critique-quick-reference.md` | Before executing — full command table |
| `references/critique-standard-headings.md` | During Phase 1 — required heading names and common non-standard variants |
| `references/critique-inline-to-refs-pattern.md` | Before Phase 5 — moving inline content to references |
| `references/critique-agentic-script-pattern.md` | During D9 assessment — checklist for script quality |
| `references/critique-agentskill-scanner-guide.md` | After manual review — scanner false positives |
| `references/design-library.md` | When building any UI — design reference library (glitch aesthetic, DESIGN.md spec, 72 brand systems, 67 styles, 200 iOS apps, taste-skill anti-slop enforcement), usage guide, refresh commands |
| `~/.hermes/profiles/indigo/skills/responsive-design/references/` | Responsive CSS — container queries, fluid typography, Grid/Flexbox, breakpoints, responsive nav/images/tables (wshobson) |
| `references/critique-10khr-learnings.md` | During 10khr — accumulated grinding patterns |
| `references/critique-10khr-may-2026-batch.md` | During batch critique — scoring insights, fix frequency table |
| `references/critique-10khr-may-2026-learnings.md` | After May 2026 batch — reusable fix patterns |
| `references/critique-10khr-may-2026.md` | May 2026 session — setup and configuration参考 |
| `references/critique-10khr-2026-05-29.md` | May 29 session log — historical reference |
| `references/critique-10khr-2026-05-29-learnings.md` | After May 29 session — bulk rewrite strategy, YAML traps |
| `references/critique-10khr-2026-05-30.md` | May 30 session log — historical reference |
| `references/critique-10khr-2026-05-30-r2.md` | May 30 session round 2 — historical reference |
| `references/critique-10khr-2026-05-30-learnings.md` | After May 30 session — distilled patterns |
| `references/critique-2026-06-15-session-learnings.md` | June 15 session — critique workflow validation, failed-attempt encoding anti-pattern, profile↔monorepo sync |
| `references/skill-architecture-sprawl-audit-2026-06-17.md` | Skill sprawl audit — merge candidates, anti-patterns, class-level umbrella principle |
| `references/soul-repo-skill-install-gap.md` | Skills in `/root/soul/skills/` not visible until installed in active profile — detection + fix |
| `references/design-library.md` | When building any UI — design reference library (glitch aesthetic, DESIGN.md spec, 72 brand systems, 67 styles, 200 iOS apps, taste-skill anti-slop enforcement), usage guide, refresh commands |
| `scripts/critique_code_ratio.py` | During Phase 2 — code ratio measurement |
| `scripts/critique_10khr_runner.py` | During 10khr — heuristic scoring and targeting (over-scores by 6-10pt) |
