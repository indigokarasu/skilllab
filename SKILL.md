---
name: ocas-skilllab
license: MIT
description: >
  Skill library maintenance: audit, merge, rename, delete, consolidate, publish,
  sanitize, and critique skills. Interactive menu via clarify tool.
  Scans ALL profile directories recursively — never hardcodes a single path.
  Use when the user asks to clean up the skill library, merge
  overlapping skills, rename skills to follow naming conventions, delete auto-generated
  or stale skills, audit skills for authorship, publish skills to external registries,
  sanitize skills for security scanner compliance, score skills against the 10-dimension
  rubric, generate improvement plans, or run autonomous library grinding (10khr).
  Also covers frontmatter conventions
  and how to identify skills by type (ocas-*, util-*, protected, auto-generated).
metadata:
  author: Indigo Karasu (indigokarasu)
  version: "3.4.2"
  merged-from: ocas-critique
  hermes:
    category: software-development
    tags:
      - skill-maintenance
      - audit
      - critique
      - library-hygiene

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
  - cross-profile skills
  - koda skills
  - secret scan
  - scan skill for secrets
  - credential leak
---

# skilllab

Skill library maintenance: audit, merge, rename, delete, consolidate, publish, sanitize.

The library should contain class-level instruction umbrellas — not hundreds of narrow one-session micro-skills. When merging, prefer one broad skill with labeled subsections over five narrow siblings.

## Interactive Menu

When invoked interactively, present a menu using the `clarify` tool: Audit, Critique, Merge, Rename, Delete, Publish, Sanitize, Hygiene, Exit. See the Interactive Menu section in the critique procedure for the full pattern (or `references/interactive-menu.md`).

## Table of Contents

The body uses flat numbered section headings (`## 1. Skill Taxonomy` … `## 11. Retired Capability Cleanup`) — they are the navigation. No separate TOC needed.

---

## 1. Skill Taxonomy

- `ocas-*` — OCAS family, authored by Indigo Karasu (includes library-management meta-skills).
- `util-*` — Utility skills authored by Indigo Karasu.
- `skilllab` — This skill; meta-skill for skill library management.
- No prefix — Base/generic skills; may have external authors or no author metadata.

**Conventions (do not skip):**
- Never rename skills to `ocas-*`/`util-*` unless the user explicitly asks.
- Active library lives at `~/.hermes/profiles/<profile>/skills/`; the default profile `~/.hermes/skills/` may hold empty hub stubs (NOT skills). `infrastructure/` is host/server infra only.
- Skills live at any depth — always discover via recursive glob `glob.glob(f"{root}/**/SKILL.md", recursive=True)` across all profiles.
- **Protected (DO NOT edit):** bundled Hermes skills, hub-installed skills (`hermes-agent`, etc.).
- **Auto-generated (DELETE):** any skill whose frontmatter has `metadata.hermes.generated_by`.
- **Author field** is in TWO places: top-level `author:` and nested `metadata.author:`.

## 2. Audit Procedure

Audit checklist: (1) Check for auto-generated skills (`generated_by` in frontmatter), (2) Check author coverage (use YAML parser, not grep), (3) Check for YAML errors (unescaped markdown, bare `---`), (4) Check for empty profile stubs, (5) Check SOUL repo install gap, (6) Check orphaned reference files, (7) Check support file map completeness, (8) Run the secret-scan gate (`scripts/secret-scan.sh <dir>` — must exit 0 / CLEAN). See `references/audit-2026-06-18.md` for the full audit results.

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

**Phase 7 — Fix remaining 4/5 and 3/5 issues:** After Critical/Major are resolved, go back to every dimension that scored 4 or 3. For each, apply the rubric's "5" criteria as a concrete fix target. Don't stop at "no Critical/Major issues remain" — a 4/5 score means the dimension has a specific, fixable gap. Close every gap the user would notice. The goal is 5/5 across all dimensions, not just "passing." If the user has to push you to fix a 4/5, you failed Phase 7.

### Iteration Loop

Repeat Phases 1-6 until quality bar is met. Default: all Critical/Major resolved, score ≥35. Completion marker: `<critique-complete>`.

**Rationalizations to reject:**
- "I'll mark it complete and come back later" — fix now
- "This minor seems wrong, I'll skip all" — evaluate each one
- "The rubric is too strict" — the bar exists for a reason
- "It's good enough" — if Major issues remain, it's not

### 10khr Mode

Assess ALL skills before fixing any. Do not cherry-pick.

The `critique_10khr_runner.py` now scans recursively across all profile directories:
- Active profile: `~/.hermes/profiles/indigo/skills/` (and all subdirectories)
- Default profile: `~/.hermes/skills/`
- All other profiles: `~/.hermes/profiles/*/skills/` (with `--all-profiles` flag)

It finds both `ocas-*` and `util-*` skills at any depth, resolves symlinks to avoid duplicates,
and deduplicates by skill name. Use `--report-only` to assess without outputting a grinding target.

1. Run Bulk D1 Check (missing includes:, invalid license) as pre-pass
2. Read every SKILL.md fully (across ALL profiles and subdirectories)
3. Score all 10 dimensions for each skill
4. Rank all skills by score
5. Fix the single lowest-scoring skill — **to 50/50, not "most issues fixed"**
6. Re-assess and repeat

The heuristic scorer (`python3 scripts/critique_10khr_runner.py`) over-scores by 6-10 points. Use for candidate ranking only. Always do manual assessment before fixing.

**Skip rule:** Before grinding a skill, check if its SKILL.md has been modified since the last 10khr run (`stat` mtime vs `10khr-state.json` `last_run`). If not modified AND the heuristic score is >= 44, skip and move to the next lowest. If all unmodified skills score >= 44, stop — the library is as good as it gets until the next modification.

**State-file split-brain (operational pitfall):** The runner's real state lives at `/root/.hermes/skills/ocas-critique/commons/data/ocas-critique/10khr-state.json` — the `STATE_FILE` constant in `critique_10khr_runner.py`. A separate `ocas-skilllab/10khr-state.json` may exist from older cron prompts but the runner NEVER reads or writes it. If a cron prompt points you at the latter, treat it as stale and use the runner's path for the skip-rule mtime comparison. When you improve a skill, update BOTH files so `current_target` and `skills_improved` stay consistent across invocations.

**Heuristic D8 ref-count trap (loop pitfall):** The runner's D8 heuristic awards +1 only when `references/` holds >= 3 `.md` files AND the literal substring "when to read" appears in the SKILL.md. A skill can be a genuine 50/50 by the manual rubric with only 1-2 reference files, yet score 49/50 (D8=4) by heuristic. Because each grind updates the SKILL.md mtime, the skip rule will NOT skip it next run — producing an endless low-value re-grind. To actually exit the loop: satisfy the heuristic's crude checks with GENUINE on-demand reference files (not filler) — extract schema / error / integration detail into `references/` until there are >= 3 real files, and keep a "When to read" support-file map. Never pad with empty stubs to game the count.

**Cross-dimension token-preservation trap (regression pitfall):** The runner scores each dimension on independent string tokens (D5: `example`/`## pipeline`/`## workflow`; D7/D10: `gotcha`/`pitfall`; D4/D8: `when to read`; D6: `why`/`because`). Extracting a section to clear D3 can silently drop a token another dimension checks — e.g. extracting `ocas-custodian`'s `## Gotchas` removed its only `example`, dropping D5 5→4. **Rule:** after any structural extraction, re-run the heuristic across ALL 10 dims and restore any lost token with a compact genuine example / `## When to use` pointer. Never declare 50/50 until the full table re-verifies.

**D9 script-sampling trap (blind spot, 2026-07-14):** The runner's D9 once scanned only the first 3 scripts; `ocas-custodian` (19 scripts) scored D9=5 while 7 lacked `--help`. It now scans ALL scripts and scores D9=5 only when none are missing `--help`/`usage`/`argparse`. Even so, a hand-rolled usage block the heuristic can't see still needs manual confirmation — run `python3 <script> --help` on each before trusting a D9=5.

**D1 `metadata.hermes.category` blind spot (rubric-vs-heuristic gap):** The runner's D1 heuristic checks only `name`/`description`/`license`/`includes:` — NOT `metadata.hermes.category` or `tags` form. Manual D1 scores 4 (not 5) when `category` is missing. Valid categories to reuse: `infrastructure`, `creative`, `software-development`, `productivity`, `devops`, `research`, `desktop`, `frontend`, `utilities`, `data-science`. Always eyeball the frontmatter for a `metadata.hermes:` block — the runner won't flag its absence.

**D3 redundancy blind spot (rubric vs heuristic mismatch):** The heuristic D3 = code ratio + `>450`-line penalty only; it misses the manual rubric's "repeating the same instruction in different words" red flag. `ocas-custodian` scored D3=5 heuristically (454→446) while its *Critical Pitfalls* restated 6 cron failure modes already in its *Error Handling* table. When D3=5 heuristically but a section restates content elsewhere, collapse it to a pointer at the canonical location. The rubric's D3 red flags (explaining known concepts, repeated instructions, long preamble) are human-read-only.

**Scope clarification:** "10khr" applies to a LIBRARY of skills (all ocas- and util- skills in the profile). It does NOT mean "run code autofix on the skill's scripts." The target is the SKILL.md + references + scripts as a documentation package, scored on the 10-dimension rubric. If the user says "10khr on ocas-skilllab," they mean critique the skilllab skill itself — not run `py_compile` on its Python files.

### Pitfalls

- **Score exactly, not "close enough"**: When scoring against the 10-dimension rubric, every dimension must be 5/5. A skill at 48/50 is NOT done. Go back and find the specific gap — a missing checklist, a missing "why" explanation, a missing error handling table — and fix it.
- **D5 demands checklists**: The rubric explicitly says "Checklists for multi-step workflows." Numbered steps are NOT a checklist. Use `- [ ]` checkbox format for any procedure with 3+ steps.
- **D6 demands "why" for rigid rules**: Any prescriptive rule ("do X, not Y") must include a "why" explanation so the agent can adapt to edge cases. Without "why", score is 3-4, not 5.
- **D9 demands `--help` on scripts**: All bundled scripts must expose `--help` (usage, flags, examples) or score 3-4. Add argparse, or for import-time side-effecting scripts inject a top-level guard: `import sys as _sys; _HELP_ARGS={"--help","-h"}; if set(_sys.argv[1:])&_HELP_ARGS: print((__doc__ or "").strip() or "Usage: python3 <script> [no flags]"); _sys.exit(0)` — **only safe if no other script imports the module** (`grep -rE "import <name>|from <name> import" scripts/` first). After patching, verify: `python3 -c "import ast; ast.parse(open('scripts/X.py').read())"` then `python3 scripts/X.py --help` (expect exit 0). Bash siblings get `if [ "$1" = "--help" ]`. Full pattern + `ocas-rally` 17/28 case: `references/critique-10khr-d9-help-injection.md`.
- **D1 demands `includes:`**: If `references/` or `scripts/` directories exist, the frontmatter must declare `includes:` listing them. Missing `includes:` is a D1-4 deduction.
- **Directory scanning must be recursive**: Never hardcode a single skills directory. Always use `glob.glob(f"{root}/**/SKILL.md", recursive=True)` across all profile directories. Skills live at any depth and in any profile.

- **Read the full skill before acting on it.** I have an 80% "guess from the name/description" rate that produces wrong moves — calling ocas-skilllab an "empty wrapper shell" (it's 350+ lines of procedure), running autofix on scripts instead of the skill itself. Before any action on a skill: read the FULL SKILL.md, all reference files, all scripts. The name and description are not the skill. (2026-06-22, from repeated pattern.)
- **Be active, not passive**: Apply fixes, don't just report
- **Follow the rubric procedure — don't ad-hoc critique**: Execute full Phase 1-6. Ad-hoc critiques miss dimensions
- **Read fully, don't skim-score**: Read entire SKILL.md, all references, all scripts before scoring
- **Batch speed vs. quality**: Parallel subagent fixes produce inconsistent quality. Single-agent Phase 1-6 produces better results for skills targeting 50/50
- **50/50 means 50/50 — not "most issues fixed"**: Stopping at 45-48/50 is the #1 failure mode. Every dimension must be explicitly addressed. D3 (no bloat) and D6 (explain "why") are the most commonly skipped. A skill at 48/50 with "minor" gaps is a skill that will mislead agents. Close every gap.
- **Scripts hardcode a single directory**: The `critique_10khr_runner.py` and `skilllab.py` previously hardcoded `~/.hermes/skills/` as the only search path, missing all skills in the indigo profile and subdirectories. Both scripts now use recursive glob across all profile directories. Always use `glob.glob(f"{root}/**/SKILL.md", recursive=True)` — never `os.listdir()` or flat globs.
- **`--all-profiles` discovery bug (2026-07-15):** `find_all_skills(all_profiles=True)` must resolve the profiles dir from `HERMES_ROOT` (`os.path.join(HERMES_ROOT, "profiles")`), NOT `os.path.expanduser("~/.hermes/profiles")`. Under a profile chroot (`HOME=/root/.hermes/profiles/<profile>/home`) the latter resolves to the *active* profile's home and silently drops every other profile (e.g. `koda` — `koda/ocas-eng-debug` went unscanned). The runner was fixed; verify with `python3 scripts/critique_10khr_runner.py --all-profiles --report-only` and confirm the non-active profiles actually appear.
- **D3 line-count measurement trap (2026-07-15):** The heuristic measures `total_lines = len(content.split("\n"))`. A file ending in a trailing newline reads as `wc -l + 1` — so a 450-line file still trips the `>450` penalty (D3=4). To clear D3 by the heuristic's hard cutoff, the runner's `split("\n")` count must be **≤450**, i.e. `wc -l` must be **≤449**. When grinding to 50/50, trim to 449 by `wc -l` to be safe, then re-run the heuristic to confirm D3=5.

**Degraded-mode read fallback (grind resilience, 2026-07-15):** During a grind, `read_file` / `skill_view` can fail cluster-wide with `DaemonThreadPoolExecutor object has no attribute '_initializer'`. This is the same degraded mode `ocas-dispatch` documents for its own reads. Do NOT abort or retry the agentic tools — switch ALL reads to `terminal()` (`cat` / `sed -n` / `grep -n` / `find`) for the rest of the run; `patch` / `write_file` writes still work. A full 48→50 grind on `ocas-dispatch` (read SKILL.md + every reference + all 47 scripts, score, fix D9 `--help` gaps, extract 126 redundant lines to `references/`) was completed this way. Verify script behavior with `python3 <script> --help` via terminal as usual.

**Safety-critical skill D3 fix (grind judgment, 2026-07-15):** When grinding a skill whose length is driven by non-negotiable safety constraints (e.g. `ocas-dispatch` — autonomous email send rules, eval-gap verification, JSONL corruption guards), do NOT cut the hard safety rules to satisfy the D3 line-count proxy. Instead extract REDUNDANT restatements to `references/` (keeping a one-line pointer in SKILL.md so nothing is orphaned). In the `ocas-dispatch` grind, 126 lines were offloaded this way (support-file-map rows → pointer; eval-gap closure cluster → `references/wave-closure-eval-gap-cluster.md`; duplicated JSONL/path pitfalls collapsed; `## Functions` merged into `## Commands`; deployment notes / lightweight-first pattern / voice-tone / journal-format compacted) — every safety rule stayed inline, D3 reached 5/5 at 448 lines. Cutting safety content to hit a line count would regress D7/D10, which reward comprehensive gotchas.
- **D1 `metadata.hermes` must NEST, not be a literal top-level key**: Write `metadata:\n  hermes:\n    category: ...\n    tags: [...]` — NOT `metadata.hermes:\n  category: ...` at the top level. The latter creates a top-level key literally named `metadata.hermes` and the rubric's D1 check (`fm["metadata"]["hermes"]`) still scores 4 (missing). Confirm with a YAML parse (`fm = yaml.safe_load(content.split("---")[1]); fm["metadata"]["hermes"]["category"]`) before declaring D1=5.
- **Cross-profile KODA work requires `cross_profile=True`**: When the user targets a non-active profile's skills (e.g., "all of KODA's skills when active profile is indigo"), `write_file` and `patch` to `~/.hermes/profiles/<other>/skills/` trigger Hermes's cross-profile soft guard. Pass `cross_profile=True` after confirming the target profile. Reads (skill_view, search_files) are unrestricted; writes are guarded. Confirm with the user which profile owns the skills before editing — "KODA's skills" means the profile named koda, not the active profile.

- **Grind the whole scope the user authorized — don't stall the loop behind a clarify (workflow correction, 2026-07-15):** When the user explicitly scopes the op ("all ocas and util skills", "the whole library", "every skill"), that statement IS the authorization to run the full grind loop. Sequence: assess all → grind lowest → re-assess → repeat until every target is at 50/50 OR the Skip Rule genuinely trips (unmodified since last run AND heuristic ≥44). Do NOT stop after grinding a single skill and re-ask scope via `clarify` — and if a clarify times out with no answer, default to *executing the stated instruction*, not parking. The Skip Rule governs re-grinding unmodified skills; it is NOT a license to quit after one. (User: "So you scored all but only worked in on one skill?" — the gap was a stalled loop, not a scoring miss. Corrective action: keep grinding; report progress, don't gate it on a re-confirmation the user already gave.)

- **Bulk script edits across skills corrupt files; `git clean -fd` destroys untracked work (git-safety incident, 2026-07-15):** Never write one script that rewrites scripts across many skills and run it without per-file verification. A `d9_fix.py` that added `--help` guards to ~50 scripts blew up: its `__main__` regex matched only double quotes, so on single-quoted/indented mains it appended a SECOND `if __name__ == "__main__":` block — 41 scripts across 9 skills stopped parsing. Recovery MUST be `git checkout -- .` (reverts tracked files in the skill repo). It must NOT be `git clean -fd` — that deletes untracked files with no history to restore them; in this incident it irreversibly deleted 9 pre-existing untracked skill files (the fixer only writes existing files, so it never created them — `clean` did). Rules: (1) Fix scripts one skill, one file at a time; after each edit verify `ast.parse` + `<script> --help` exits 0 before the next. (2) If a bulk script corrupts, recover with `git checkout -- .` per skill repo ONLY — never `git clean -fd`. (3) Before any `clean`, list untracked first (`git clean -nd` / `git status --short`) and confirm none are legitimate work. (4) Edit-script regexes must match both quote styles and indentation: `re.search(r'if\s+__name__\s*==\s*["\']__main__["\']\s*:\s*\n', txt)`. Full safe-recovery recipe + corrected regex + files lost in the incident: `references/critique-10khr-bulk-edit-git-safety.md`.

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
5. Archive B's entire directory to `~/.hermes/profiles/indigo/skills/.archive/<B-name>/`
6. Update all references (cron jobs, SOUL.md, memory, other skills, cron prompts)

### Package Integrity
Before archiving, inspect the source as a **complete directory package** (may include `references/`, `templates/`, `scripts/`, `assets/`). If it has support files or relative links:
- Re-home every needed support file into the umbrella's canonical directories AND rewrite paths, OR
- Archive the entire original package unchanged.

**Never** flatten only SKILL.md into `references/` while leaving support files behind.

---

## 5. Rename Procedure

```bash
mv ~/.hermes/profiles/indigo/skills/<old-name> ~/.hermes/profiles/indigo/skills/<new-name>
```

Then update ALL of the following (check every box — missing any causes stale references):

**Inside the skill:**
1. `name:` field in frontmatter
2. Top-level heading (`# Old Name` → `# New Name`)
3. Any self-references in the body text
4. Support file map entries

**Cache files (critical — stale entries persist in system prompt):**
5. `~/.hermes/.skills_prompt_snapshot.json` — rename the cached key:
   ```python
   import json
   with open(os.path.expanduser("~/.hermes/.skills_prompt_snapshot.json")) as f:
       cache = json.load(f)
   cache["new-name"] = cache.pop("old-name")
   with open(os.path.expanduser("~/.hermes/.skills_prompt_snapshot.json"), "w") as f:
       json.dump(cache, f, indent=2)
   ```
6. `~/.hermes/profiles/indigo/skills/.usage.json` — rename the tracking key (same pattern)

**External references (grep across everything):**
7. `grep -r "old-name" ~/.hermes/profiles/indigo/skills/ --include="*.md"` — update all SKILL.md references
8. `grep -r "old-name" ~/.hermes/profiles/ --include="*.md"` — update profile-level references
9. Cron jobs — `cronjob action=list` and grep for the old name; update or delete referencing jobs
10. Memory — `grep -r "old-name" ~/.hermes/memories/` and update any memory entries
11. SOUL.md / AGENT.md / USER.md — update if the skill is mentioned
12. Other skills' "When NOT to Use" / "Relationship to Other Skills" sections

**Gateway restart:**
13. `hermes gateway restart` — required to clear the injected skill index. Without this, the old name persists in `/skills` autocomplete and the skill catalog.

**Lesson (May 2026):** Renaming without updating `.skills_prompt_snapshot.json` and `.usage.json` leaves stale cache entries. The old name persists in the injected system prompt until the next full session refresh.

**Lesson (June 2026):** Renaming a skill directory without also renaming the frontmatter `name:` field causes a mismatch — `skills_list` and `skill_view` match on directory name, not frontmatter content. Cron jobs that reference the skill by name will silently fail to load it.

## 5a. New Skill Addition Checklist

When adding a new skill to the library:

1. Create directory: `~/.hermes/profiles/indigo/skills/<name>/` with proper frontmatter
2. **Delete cache:** `rm ~/.hermes/.skills_prompt_snapshot.json` (regenerates on next session). Without this, the new skill won't appear in the injected skill index or `/skills` autocomplete
3. `.usage.json` auto-populates on first use — no manual step
4. If the skill replaces or overlaps with an existing skill, update the sibling's "When NOT to Use" / "Relationship to Other Skills" sections
5. If the skill should be scheduled, create cron jobs
6. If the skill is a significant addition, note it in memory
7. `hermes gateway restart` — to pick up the new skill in the catalog immediately

---

## 6. Publish Procedure

Publish skills to external registries (agentskills.io, LobeHub, Anthropic).

### agentskills.io Spec Requirements

agentskills.io **discovers skills from GitHub repos** — no direct submission API.

**Required frontmatter fields:** `name` (1-64 chars, lowercase `[a-z0-9-]`, matches directory) and `description` (1-1024 chars, includes trigger keywords).

**Non-standard Hermes extensions to remove:** `metadata.hermes`, `metadata.email` → `metadata.author`, `metadata.openclaw` (legacy), top-level `version` → `metadata.version`, `self_update`.

Full spec compliance checklist: see `references/skill-publish-spec-compliance-checklist.md`.

### Publishing Workflow

**CRITICAL: Check `source:` field before any repo operations.**

1. Read the skill's frontmatter `source:` field FIRST.
   - If `source:` points to a monorepo (e.g., `https://github.com/indigokarasu/utilities/tree/main/<name>`), the skill lives inside that monorepo. Sync to the monorepo subdirectory — do NOT create a standalone repo.
   - If `source:` points to its own repo (e.g., `https://github.com/indigokarasu/<name>`), or there is no `source:` field, proceed with standalone repo creation below.
2. Audit and fix spec compliance
3. Sanitize private data (replace PII with placeholders)
4. **Only if standalone repo:** Create GitHub repo: `gh repo create indigokarasu/skill-name --private --description "..."`
5. **If monorepo:** Clone the monorepo, sync skill files to the matching subdirectory, commit, and push. The monorepo is the single source of truth.
6. Add LICENSE, README.md, .gitignore (standalone only)
7. Commit and push
8. For public skills: `gh repo edit indigokarasu/skill-name --visibility public`

### Quality & Security Evaluation
See `references/skill-publish-agentskill-evaluation-criteria.md` for the agentskill.sh 100/100 scoring pattern.

### GitHub Mechanics
- Full push recipe: `references/skill-publish-github-push-recipe.md`
- Bulk sync workflow for existing repos: `references/skill-publish-github-sync-existing-skills.md`. Automated daily sync also runs via `/root/.hermes/profiles/indigo/scripts/skill-sync-push.sh` (cron `ocas-skilllab-sync`, 04:00) — it commits+pushes all remoted skills with changes, secret-gates each repo, and sets the Indigo Karasu identity (the host global git config defaults to `Koda`, a different profile; on manual commits set `git -C <skill> config user.name "Indigo Karasu"` / `user.email "mx.indigo.karasu@gmail.com"` too). After any local skill edit, this keeps GitHub current without manual pushes.
- **Creating a NEW private monorepo from existing skills (2026-07-15):** When the user says "make a new private monorepo with all <X> skills," COPY the skill dirs into a fresh staging dir (do NOT `mv` — leave originals in place so the agents that load them keep working). Then: (1) strip any nested `.git` inside copied trees (`rm -rf <copy>/<skill>/references/livearch/.git`) or git stores an empty **gitlink** and the real files are NOT committed — re-add and confirm with `git ls-files | grep -c livearch` > 0; (2) `git init`, set Indigo identity; (3) run `secret-scan.sh` and remediate placeholders (see masked-output pitfall above); (4) `gh repo create indigokarasu/<name> --private`; (5) `git remote add origin git@github.com:indigokarasu/<name>.git` explicitly and `git push -u origin main` — `gh repo create` does NOT auto-wire `origin` in this shell, and a bare `git push` then fails with "Could not read from remote repository." (6) Verify remote SKILL.md count == local.
- **Do NOT ask which account to use when only one GitHub account is authenticated.** When `gh` is logged in to a single account (check: `gh auth status`), create the repo under that account. Asking "which account?" when only `indigokarasu` is available is a wasted round-trip — the user's correction: "You only have your github account, indigokarasu, so what are you asking for?" Pick the authenticated account and proceed; only ask if the user explicitly names a different one.
- **Monorepo is the sync PUSH TARGET — never create per-skill repos for skills already under a monorepo (2026-07-15).** All `util-*` skills live in the single `indigokarasu/utilities` monorepo (subdirs named WITHOUT the `util-` prefix: `buy`, `draw`, …); `eng-*` skills live in `indigokarasu/eng-skills`. Each live skill's `source:` frontmatter already points to its monorepo subdir. So when syncing, the workflow is: clone the monorepo → copy live skill dir → monorepo subdir → commit → push `main`. Do NOT `git init` a standalone repo per skill, do NOT `gh repo create` per skill — that creates orphan repos the `source:` field doesn't reference (the user's redirect: "Util- skills have a monorepo, if there are new skills add them to the monorepo"). Always read `source:` first (rule at top of §6) before any repo operation.
- **Unified monorepo sync action (2026-07-15):** `bash /root/.hermes/profiles/indigo/scripts/monorepo-sync.sh` copies live `util-*` (from `indigo/skills`) and `eng-*` (from both `indigo` and `koda` profiles) into their monorepos, then pushes. It: strips nested `.git`/`.bak`/pycache from each copy; sanitizes doc-URL placeholders (`<POSTGRES_URL>` / `<GITHUB_URL_WITH_TOKEN>`) so the secret gate passes; gates on `secret-scan.sh --working-tree` (NOT full-history mode — committed doc prose in `util-github` would otherwise block the push); and pushes `main`. Cron `monorepo-skill-sync` runs it daily 05:00. Three-tier sync is now: ocas-* (per-skill repos → `skill-sync-push.sh` @ 04:00), util-* + eng-* (monorepos → `monorepo-sync.sh` @ 05:00). Both set Indigo identity (host global git defaults to `Koda`). Live skills are NOT themselves git repos; the monorepos are push targets only.
- **`secret-scan.sh --working-tree` mode (added 2026-07-15):** full-history scanning blocks legitimate pushes because pre-existing committed doc prose (example credential URLs in `util-github/credential-purge.md`, the scanner's own regex literal in `util-github/scripts/secret_scan.sh`) flags as "secret." For a SYNC gate you only care about NEW secrets in the working tree, so pass `--working-tree` (scans working tree + `.git/config`, skips `git rev-list --all`). The script excludes itself (`secret-scan.sh`/`secret_scan.sh`) from the working-tree grep. Use full mode only for pre-publish audits where history matters.

---

## 6a. Share Procedure — Submit to Nous Research Optional Skills

Use when the user says "share this skill", "submit to Nous", "publish to optional-skills", or "contribute this skill". Prerequisites: score ≥45/50, `description` ≤ 60 chars, no PII/credentials, **`scripts/secret-scan.sh` exits 0 (CLEAN)**, test file exists. Steps: prepare submission dir → copy files → clean frontmatter → verify no PII → run tests → py_compile scripts → commit to fork → create PR.  for the full procedure.

**Mandatory Configuration Policy gate (the single most common auto-close reason):** Behavioral settings (thresholds, retention windows, feature flags, display prefs, paths) MUST NOT be read from environment variables — the hermes-sweeper auto-closes such PRs under the `env-var-for-config` policy and the closed PR **cannot be reopened via API** (a maintainer must reopen, or you open a fresh PR). Correct mechanism: declare each setting in `metadata.hermes.config`, read it at runtime from `$HERMES_HOME/config.yaml` under `skills.config.<key>` (via PyYAML — `telephony.py` is the reference impl), document `skills.config.<key>` in SKILL.md (never env-var names), and let CLI flags override. Only secrets go in `.env`; only `HERMES_HOME`/`HERMES_PROFILE` locate the runtime.

Run the automated check before opening the PR:
```bash
python3 <forge>/scripts/forge_audit_skills.py --skill <ocas-name>   # 0 exit = clean
```
It flags any `GENIE_*` / non-secret env-var config read in `scripts/` or env-var config table in `SKILL.md`. Also confirm there are no drifted copies: genie, for example, had the running script, a skill-bundled script, and THREE divergent SKILL.md files — fix ALL copies, not just the one you diff. The full written standard: `references/nous-skill-requirements.md` (Configuration Policy) + `ocas-forge`'s `references/compliance-audit-checklist.md`.

---
- `research/` — Academic search, data analysis, OSINT
- `communication/` — Email, messaging, social media
- `security/` — Penetration testing, forensics, auditing
- `mlops/` — ML training, fine-tuning, inference
- `blockchain/` — Crypto, DeFi, NFTs
- `finance/` — Trading, modeling, analysis
- `gaming/` — Game servers, emulators
- `health/` — Fitness, nutrition, medical
- `payments/` — Payment processing, billing
- `web-development/` — Frontend, backend, full-stack
- `software-development/` — Code review, debugging, testing
- `mcp/` — MCP server integrations
- `dogfood/` — Agent self-improvement, testing
- `migration/` — Data migration, onboarding
- `autonomous-ai-agents/` — Subagent orchestration

### Gotchas

- **Description length is enforced:** The CONTRIBUTING.md has `assert len(description) <= 60`. A skill with a 100+ char description will be rejected. Be aggressive — cut articles, merge phrases, use short words.
- **No external dependencies:** Skills should use stdlib + existing Hermes tools. If a skill requires pip packages, it belongs in Skills Hub, not optional-skills.
- **Tests are required:** Every skill needs `tests/test_<skill>_skill.py` with at least import, help, dry-run, and frontmatter tests.
- **Author is the agent:** Use the agent's own name/GitHub, not the user's. The user directs, the agent authors.
- **No user data:** Never include the user's name, email, paths, or personal config in the submitted skill. All paths should be generic (`~/.hermes/`, `/root/`, etc.).

See `references/skill-sanitize-checklist.md` for the full sanitize procedure.

---

## 7b. Secret Scan Gate

**Policy (2026-07-07):** No secrets in local/remote skills except the private backup repo; even there, secrets belong in the correct env file, not in skills.

A skill is NOT committable or publishable until `scripts/secret-scan.sh <dir>` exits 0 (CLEAN). Run it as a gate in Audit, Sanitize, Publish, and Share.

### Run it
```bash
bash scripts/secret-scan.sh /path/to/skill            # full: working tree + .git/config + ALL history
bash scripts/secret-scan.sh --working-tree /path/to/skill   # working tree + .git/config only (skip history)
```
Scans working tree, `.git/config`, and **entire git history** (all revisions). Output is masked; exits 1 if any potential secret is found. Use `--working-tree` for sync/publish gates where pre-existing committed history would otherwise block a legitimate push (see §6 monorepo-sync note).

### Remediation
- **Working tree:** redact/remove the secret, commit the fix.
- **Token in remote URL (`.git/config`):** strip it — git authenticates via the `gh` credential helper, so `<GITHUB_URL_WITH_TOKEN>` is redundant AND a leak. `git remote set-url origin https://github.com/owner/repo.git`.
- **Secret in history:** rewrite. `git-filter-repo` is broken on this host (missing module) — use `git filter-branch`:
  ```bash
  git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch <path>' --prune-empty -- --all
  git for-each-ref --format='%(refname)' refs/original/ | xargs -n1 git update-ref -d
  git reflog expire --expire=now --all && git gc --prune=now
  git push --force
  ```
  Verify: `git log --all -p | grep -c '<secret>'` → 0.
- **Live credential still valid (PAT/API key):** scrubbing history does NOT invalidate it. Rotate/revoke at the provider (GitHub PATs: Settings → Developer settings → PATs; classic PATs can't be API-revoked).

### False positives
Instructional/example text (e.g. `<GITHUB_URL_WITH_TOKEN>` inside a *detection guide*) is secret-shaped but not a real secret. Redact the example or move it to a reference if it trips the gate repeatedly. The scanner script `scripts/secret-scan.sh` is auto-excluded (it contains detection patterns by design).

**Scanner output is MASKED — do NOT grep the masked string.** `secret-scan.sh` masks matched credential *values* as `***` in its printed output (e.g. it prints `<POSTGRES_URL>` when the file actually contains a real postgres URL with credentials). The file holds the UNMASKED value, so grepping the working tree for `***` (or `<POSTGRES_URL>`) will NOT match and you'll falsely believe the line is already sanitized. To verify or remediate, search for the REAL (unmasked) substring. Prefer a literal `str.replace()` in Python over sed/regex — sed and perl interpolate `*`/`@`/`?` as metacharacters (even with `\\Q...\\E` in perl when the delimiter is `:`), and silently fail to substitute, leaving the file unchanged while reporting success. When a substitution won't take, confirm with `cat -A` or `hexdump -C` that the literal bytes match your needle. (2026-07-15 incident: ~6 turns wasted chasing a `***` string that never existed in the file; the real content was a postgres URL with `user:pass@localhost`.)

---

## 8. Frontmatter Standards

Minimum frontmatter: `name`, `description`, `license` (immediately after `name:`). Include `includes:` if `references/` or `scripts/` dirs exist. Add `triggers:` for discoverability. Full reference — see `references/skilllab-frontmatter-standards.md`.

---

## 9. Pitfalls

See `references/skilllab-pitfalls.md` for the full pitfalls list (60+ entries covering batch replace, YAML errors, author gaps, caching, monorepo sync, and more).

---

## 10. External Tool Evaluation

Follow `references/tool-integration-pattern.md` (flow: read docs → map to existing skills → prefer delegation → only build a new skill for 24+ command systems; pitfall: over-integration).

## 11. Retired Capability Cleanup

Retire a capability by: `grep -r "old-name"` across skill dirs → classify references (prose→replace, section→remove, data/audit logs→leave) → rename support files + cache keys in `.skills_prompt_snapshot.json` → re-grep to confirm zero refs (excluding `.archive/` and audit logs).

## Support File Map

The full file index (60+ reference and script entries, with conditional **When to read** column) lives in `references/support-file-map.md` — read it **before any skilllab operation** for the per-task pointers (D1 audit, scoring, 10khr grind, publish/share, secret gate).

- `scripts/skill-sync-push.sh` — reusable sync action: commits+pushes every remoted skill with changes or unpushed commits, secret-gated, sets Indigo identity. Drives cron `ocas-skilllab-sync` (daily 04:00). `DRY_RUN=1` for a no-op report.
- `scripts/monorepo-sync.sh` — unified monorepo sync: copies live `util-*` + `eng-*` skills into the `utilities` / `eng-skills` monorepos (strips nested `.git`/`.bak`/pycache, sanitizes doc-URL placeholders, secret-gates `--working-tree`), pushes `main`. Drives cron `monorepo-skill-sync` (daily 05:00). `DRY_RUN=1` for a no-op report.
