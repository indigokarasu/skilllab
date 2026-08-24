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
  NOT for: building or debugging a skill's own scripts (that is not a library task),
  running code autofix on skill source, or writing arbitrary code unrelated to the skill library.
metadata:
  author: Indigo Karasu (indigokarasu)
  version: "3.5.0"
  merged-from: ocas-critique
  hermes:
    category: software-development
    tags:
      - skill-maintenance
      - audit
      - critique
      - library-hygiene

source: https://github.com/<agent-handle>/skilllab
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


## 1. Skill Taxonomy

- `ocas-*` — OCAS family, authored by <agent-name> (includes library-management meta-skills).
- `util-*` — Utility skills authored by <agent-name>.
- `skilllab` — This skill; meta-skill for skill library management.
- No prefix — Base/generic skills; may have external authors or no author metadata.

**Conventions (do not skip):**
- Never rename skills to `ocas-*`/`util-*` unless the user explicitly asks.
- Active library lives at `$HERMES_HOME/../<profile>/skills/`; the default profile `~/.hermes/skills/` may hold empty hub stubs (NOT skills). `infrastructure/` is host/server infra only.
- Skills live at any depth — always discover via recursive glob `glob.glob(f"{root}/**/SKILL.md", recursive=True)` across all profiles.
- **Protected (DO NOT edit):** bundled Hermes skills, hub-installed skills (`hermes-agent`, etc.).
- **Auto-generated (DELETE):** any skill whose frontmatter has `metadata.hermes.generated_by`.
- **Author field** is in TWO places: top-level `author:` and nested `metadata.author:`.

## 2. Audit Procedure

Audit checklist: (1) Check for auto-generated skills (`generated_by` in frontmatter), (2) Check author coverage (use YAML parser, not grep), (3) Check for YAML errors (unescaped markdown, bare `---`), (4) Check for empty profile stubs, (5) Check SOUL repo install gap, (6) Check orphaned reference files, (7) Check support file map completeness, (8) Run the secret-scan gate (`scripts/secret-scan.sh <dir>` — must exit 0 / CLEAN), (9) Check public-facing prose: banned taglines, deprecated-tool references, session-log leaks, and **reference-file PII leaks**. Reference files (`references/*.md`) must abstract to general reusable knowledge — no session-specific filenames, contact names, private system architecture, or dated incident logs. Session logs belong in journals, not in skills. See `references/sanitize-public-prose-rules.md` for the public-prose ban list and `references/skill-sanitize-checklist.md` for the publish-time PII scrub procedure.

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

#### Critique Checklist

- [ ] Read full SKILL.md + all references + all scripts; measure line count (flag >500); scan for phantom refs
- [ ] Run `critique_code_ratio.py`; measure code ratio (target <20%)
- [ ] Score all 10 dimensions against `references/critique-rubric.md`; print table
- [ ] Categorize each dimension scoring <=3 as Critical / Major / Minor
- [ ] Plan fixes (location, current state, fix, impact) per issue
- [ ] Execute: Critical -> Major -> Minor; verify syntax after each edit
- [ ] Verify: re-read, re-score affected dimensions, confirm resolved; print before/after
- [ ] Fix remaining 4/5 and 3/5 gaps until every dimension is 5/5

### Procedure

**Phase 1 — Read:** Read the full SKILL.md, all reference files, all scripts. Measure line count (flag if >500). Check for phantom references AND INTERNAL CONTRADICTIONS — sections making opposite factual claims (e.g. one section says script X exists and is the canonical entry point, another says X does NOT exist; one table says Y is a thin wrapper, the Gotchas say Y was never built). The heuristic cannot detect contradictions, but they are real D10 completeness/integrity defects — fix by aligning all sections to the authoritative statement (usually the Gotchas or the most-specific section). **Scan Pitfalls/What NOT to Do sections for absolute prohibitions that may encode failed attempts rather than confirmed hard constraints** — see Pitfall "Absolute prohibitions encoding failed attempts."

**Phase 2 — Score:** Measure code ratio first (`python3 scripts/critique_code_ratio.py <path>/SKILL.md`). Target: under 20%. Evaluate each dimension 1-5 using `references/critique-rubric.md`. Print the score table. Bands: A=40-50, B=30-39, C=20-29, D=10-19, F=0-9.

**Phase 3 — Categorize:** For each dimension scoring ≤3, classify every issue:
- **Critical** — blocks loading/runtime (missing name/description, invalid YAML, broken paths, phantom references)
- **Major** — degrades effectiveness (vague description, wrong voice, SKILL.md >500 lines, missing When to Use/NOT to Use, no Gotchas, code ratio >30%)
- **Minor** — polish (style preferences, optional enhancements)

Use `references/critique-issue-categorization.md` for full rules.

**Phase 4 — Plan:** For each issue, document: Location, Current state, Fix, Impact (+N points). Group: Critical → Major → Minor. Use `references/critique-improvement-plan-template.md`.

**Phase 5 — Execute:** Critical → fix immediately. Major → fix unless documented deferral. Minor → evaluate with 3 questions (genuine improvement? false positive? helps the agent?), then apply if all pass. Use `patch` for targeted edits. Verify syntax after each change. **Full-file rewrite strategy:** When extracting multiple inline sections to references in one pass (3+ sections or >50 lines moved), prefer a `write_file` rewrite of the entire SKILL.md over sequential `patch` calls. Sequential patches cause line-number drift, eaten headings, and duplicate sections — always `grep -n '^## '` after structural patches. When moving code blocks to reference files, scan for absolute paths (`<fs-root>/`, `/home/`, `/etc/`) and replace with `{agent_root}/`. Verify cross-skill paths exist before embedding them.

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
- Active profile: `$HERMES_HOME/../indigo/skills/` (and all subdirectories)
- Default profile: `~/.hermes/skills/`
- All other profiles: `$HERMES_HOME/../*/skills/` (with `--all-profiles` flag)

It finds both `ocas-*` and `util-*` skills at any depth, resolves symlinks to avoid duplicates,
and deduplicates by skill name. Use `--report-only` to assess without outputting a grinding target.

- [ ] Run Bulk D1 Check (missing includes:, invalid license) as pre-pass
- [ ] Read every SKILL.md fully (across ALL profiles and subdirectories)
- [ ] Score all 10 dimensions for each skill
- [ ] Rank all skills by score
- [ ] Fix the single lowest-scoring skill — **to 50/50, not "most issues fixed"**
- [ ] Re-assess and repeat

The heuristic scorer (`python3 scripts/critique_10khr_runner.py`) is UNRELIABLE as a numeric score — it can over-score by 6-10 points in some cases and UNDER-score in others (e.g. `util-apibuild` reported 39/50 heuristically vs a genuine 44/50 on the manual rubric — the heuristic was harsher, not lenient). Its magnitude AND direction are not predictable from the manual score. Use it for candidate RANKING only; always do a manual rubric assessment before fixing, and trust the on-disk 5-dimension check, never the heuristic number.

**Skip rule:** Before grinding a skill, check if its SKILL.md has been modified since the last 10khr run (`stat` mtime vs `10khr-state.json` `last_run`). If not modified AND the heuristic score is >= 44, skip and move to the next lowest. If all unmodified skills score >= 44, stop — the library is as good as it gets until the next modification.

**Scope clarification:** "10khr" applies to a LIBRARY of skills (all ocas- and util- skills in the profile). It does NOT mean "run code autofix on the skill's scripts." The target is the SKILL.md + references + scripts as a documentation package, scored on the 10-dimension rubric. If the user says "10khr on ocas-skilllab," they mean critique the skilllab skill itself — not run `py_compile` on its Python files.

### Pitfalls

- **Score exactly, not "close enough"**: When scoring against the 10-dimension rubric, every dimension must be 5/5. A skill at 48/50 is NOT done. Go back and find the specific gap — a missing checklist, a missing "why" explanation, a missing error handling table — and fix it.
- **D5 demands checklists**: The rubric explicitly says "Checklists for multi-step workflows." Numbered steps are NOT a checklist. Use `- [ ]` checkbox format for any procedure with 3+ steps.
- **D6 demands "why" for rigid rules**: Any prescriptive rule ("do X, not Y") must include a "why" explanation so the agent can adapt to edge cases. Without "why", score is 3-4, not 5.
- **D9 demands `--help` on scripts**: All bundled scripts must expose `--help` (usage, flags, examples) or score 3-4. Add argparse, or for import-time side-effecting scripts inject a top-level guard: `import sys as _sys; _HELP_ARGS={"--help","-h"}; if set(_sys.argv[1:])&_HELP_ARGS: print((__doc__ or "").strip() or "Usage: python3 <script> [no flags]"); _sys.exit(0)` — **only safe if no other script imports the module** (`grep -rE "import <name>|from <name> import" scripts/` first). After patching, verify: `python3 -c "import ast; ast.parse(open('scripts/X.py').read())"` then `python3 scripts/X.py --help` (expect exit 0). Bash siblings get `if [ "$1" = "--help" ]`. Full pattern + `ocas-rally` 17/28 case: `references/critique-10khr-d9-help-injection.md`.
- **Stdio MCP server `--help` needs ALL-OPTIONAL argparse (D9, 2026-07-20):** A local MCP server launched via `mcp.server.stdio` (registered under `mcp_servers` in `config.yaml`) is started by the MCP client with NO command-line args and must boot its asyncio loop immediately. If you add `argparse` for `--help`, make EVERY argument `default=...` (from env or a constant) so `python3 server.py` with zero args still parses and starts the loop — a required positional/argument raises `error: the following arguments are required` and the server never boots. Then `--help` exits 0 and prints usage. Verify BOTH: `python3 server.py --help` (exit 0, usage printed) AND that `python3 server.py` with no args still parses/boots (no arg error) — the client does the latter, not the former. This fixed `util-apibuild`'s `mcp_server_template.py`, which previously had NO `--help` at all (0 bytes on `--help`).
- **D9 guard MUST short-circuit BEFORE module-level side effects (placement rule, 2026-07-17):** `--help` exits 0 only if the guard runs BEFORE any top-level work. Scripts that execute logic at module scope (not under `if __name__ == "__main__":`) crash on `--help` if the guard sits after a side-effecting line. Failure shapes from the 2026-07-17 grind: (a) `sys.stdin.read()` at top level — put the guard right after `import sys`; (b) `open(sys.argv[1])` at top level (repair_jsonl_corruption.py) — `--help` becomes the path and raises FileNotFoundError; gate argv before the open; (c) `from google_auth import get_gmail_service` at top level (briefing_deliver.py) — runs the import before the guard, so place the guard ABOVE it. Rule: the `--help` guard is the FIRST executable code after imports, never after any I/O or dependency import that can raise. Verify with `python3 scripts/X.py --help` (NOT just ast.parse) — a script that parses can still fail `--help` via top-level side effects.
- **Bash `--help` guard under `set -u` (D9, 2026-07-17):** For `.sh` scripts the `--help` case must (1) `exit 0`, (2) precede any positional-arg-as-root assignment, and (3) define every variable the rest of the script references, or `set -u` aborts it. Two real failures fixed in the 2026-07-17 grind of this skill: (a) `secret-scan.sh --help` printed usage then died with `TARGET: unbound variable` — the `--help|-h)` branch set nothing while later code reads `$TARGET`; fix: set `TARGET="."` inside the help branch. (b) `skill-sync-push.sh --help` ran the FULL sync (commits/pushes) instead of printing usage — no guard existed, so `--help` fell through to `SKILLS_ROOT="${1:-...}"` and the main loop; fix: add `if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then echo "Usage: ..."; exit 0; fi` BEFORE the root assignment. Rule: bash help guards need `exit 0` + must precede positional-arg logic + every `$VAR` downstream must be defined in the help branch or made unset-safe via `${VAR:-}`. The runner's D9 heuristic cannot catch a `--help` that CRASHES or a bash script with no guard — the only real check is `bash script.sh --help </dev/null; echo $?` (expect 0), run per script.
- **`from Google auth import ...` typo crashes dispatch-family scripts (recurring bug, 2026-07-17):** Several OCAS scripts import the Gmail helper as `from Google auth import get_gmail_service` — a typo (capital G, space) that is not valid Python and raises SyntaxError at module load, so `--help`, imports, and execution all fail. Correct form is `from google_auth import get_gmail_service`. Seen in ocas-dispatch/scripts/briefing_deliver.py (and historically ocas-bower, ocas-taste). When a dispatch-family script fails `--help` with a SyntaxError on its import line, fix the casing FIRST, then verify `--help`. The google_auth module lives at <hermes-home>/scripts/google_auth.py and is found via `sys.path.insert(0, HERMES_ROOT/"scripts")` at runtime — Pyright may flag it unresolved but it executes.
- **D1 demands `includes:`**: If `references/` or `scripts/` directories exist, the frontmatter must declare `includes:` listing them. Missing `includes:` is a D1-4 deduction.
- **Directory scanning must be recursive**: Never hardcode a single skills directory. Always use `glob.glob(f"{root}/**/SKILL.md", recursive=True)` across all profile directories. Skills live at any depth and in any profile.

- **Read the full skill before acting on it.** I have an 80% "guess from the name/description" rate that produces wrong moves — calling ocas-skilllab an "empty wrapper shell" (it's 350+ lines of procedure), running autofix on scripts instead of the skill itself. Before any action on a skill: read the FULL SKILL.md, all reference files, all scripts. The name and description are not the skill. (2026-06-22, from repeated pattern.)
- **Be active, not passive**: Apply fixes, don't just report
- **Verify superset BEFORE deleting parallel trees (anti-data-loss, 2026-07-22):** When deduping two copies of a skill family (e.g. old `eng-*` vs new `engineering/`), do NOT `git rm` / delete until a script proves every file in the old tree exists in the new one (same relative path). The trees had diverged: 26 github reference files + 1 review file existed ONLY in the old tree, and 29 same-named files had different content. Blind deletion = destroy real data. Back up to `_backup_<date>/` on disk first; only delete after the missing-file count is 0.
- **When listing skills for the user, be terse and verify reality (style correction, 2026-07-22):** The user rejected verbose taxonomy essays ("just list them, not verbose bs", "sounds like a lot of bs"). Give the list directly — folder/dir names, grouped if needed — no invented structure, no defensive narration. ALWAYS enumerate from the filesystem (`find` / `glob` / `search_files`), never from memory or a prior session's claim: a prior summary falsely asserted "pushed" when HEAD==remote and falsely described the trees as fully merged. Filesystem truth > prior assertions.
- **Follow the rubric procedure — don't ad-hoc critique**: Execute full Phase 1-6. Ad-hoc critiques miss dimensions
- **Read fully, don't skim-score**: Read entire SKILL.md, all references, all scripts before scoring
- **Batch speed vs. quality**: Parallel subagent fixes produce inconsistent quality. Single-agent Phase 1-6 produces better results for skills targeting 50/50
- **50/50 means 50/50 — not "most issues fixed"**: Stopping at 45-48/50 is the #1 failure mode. Every dimension must be explicitly addressed. D3 (no bloat) and D6 (explain "why") are the most commonly skipped. A skill at 48/50 with "minor" gaps is a skill that will mislead agents. Close every gap.
- **Scripts hardcode a single directory**: The `critique_10khr_runner.py` and `skilllab.py` previously hardcoded `~/.hermes/skills/` as the only search path, missing all skills in the indigo profile and subdirectories. Both scripts now use recursive glob across all profile directories. Always use `glob.glob(f"{root}/**/SKILL.md", recursive=True)` — never `os.listdir()` or flat globs.
- **`--all-profiles` discovery bug (2026-07-15):** `find_all_skills(all_profiles=True)` must resolve the profiles dir from `HERMES_ROOT` (`os.path.join(HERMES_ROOT, "profiles")`), NOT `os.path.expanduser("$HERMES_HOME/..")`. Under a profile chroot (`HOME=<hermes-home>/profiles/<profile>/home`) the latter resolves to the *active* profile's home and silently drops every other profile (e.g. `koda` — `koda/ocas-eng-debug` went unscanned). The runner was fixed; verify with `python3 scripts/critique_10khr_runner.py --all-profiles --report-only` and confirm the non-active profiles actually appear.
- **D3 line-count measurement trap (2026-07-15):** The heuristic measures `total_lines = len(content.split("\n"))`. A file ending in a trailing newline reads as `wc -l + 1` — so a 450-line file still trips the `>450` penalty (D3=4). To clear D3 by the heuristic's hard cutoff, the runner's `split("\n")` count must be **≤450**, i.e. `wc -l` must be **≤449**. When grinding to 50/50, trim to 449 by `wc -l` to be safe, then re-run the heuristic to confirm D3=5.
- **Frontmatter `---` fence deletion trap (grind edit hazard, 2026-07-16):** Programmatic SKILL.md surgery that extracts a block to clear D3 — a Python slice (`header + pointer + rest` reassembly, or a `del lines[a:b]`) — can accidentally consume the frontmatter's closing `---`. The YAML then has no terminator: `yaml.safe_load` raises `ScannerError` (or the whole body is misread as frontmatter), and the runner drops **D1 → 1** (name/description unparseable) and **D2 → 3**. Because the grind fix "succeeded" and you only re-score at the end, the regression is invisible until then — the very edit meant to improve the score tanks it. **Rule:** (1) Guard the slice to STOP before the `---` line (the boundary is the line `---` between the triggers block and the first prose paragraph). If you reassemble, re-insert `---` at that boundary if missing. (2) **Re-run the heuristic after EVERY programmatic edit** — a D1/D2 drop from 5 to ≤3 is the tell-tale sign the fence is gone; fix before moving on. (3) Final verification: `yaml.safe_load(content.split('---')[1])` must return a dict with `name` and `description`. The same hazard applies to `forge.build`/`forge.repair` edits done via `terminal()` heredoc slices. First-class pitfall recorded in `ocas-forge`'s Gotchas.

Prefer `10khr_cron_verify.py` as the single autonomous-pass entry point (operational simplification, 2026-07-19):** The manual workaround for the `--report-only` skip-rule pitfall (import the runner module, call `run_full_assessment()`, walk mtimes vs `last_run`, then run the verify script on eligible skills) is correct but REDUNDANT — `scripts/10khr_cron_verify.py` already does all of it in ONE cron-safe call: it assesses every `ocas-*`/`util-*` skill, applies the skip-rule against the runner's canonical STATE_FILE (the `ocas-critique/...` path, not the stale `ocas-skilllab` copy), and prints each below-50 skill with its mtime, the 5-dimension on-disk verdict (D1/D3/D5/D9), and an `OVER-SCORING TRAP — skip` vs real-gap determination. In the 2026-07-19 finch:work pass, running the harness alone produced the complete answer; the separate `run_full_assessment()` + mtime Python walk was duplicate effort. **Rule:** for any autonomous/cron 10khr pass, run `python3 scripts/10khr_cron_verify.py` FIRST and treat its output as authoritative. Do NOT also import `critique_10khr_runner.py` and re-derive eligibility by hand — that re-introduces the skip-rule-mutation risk (if you ever call `main()`/`save_state`) and wastes turns. Only drop to the manual `run_full_assessment()` import if you need the raw sorted score list for a reason OTHER than "what should I grind?"

`--report-only` advances `last_run` and silently breaks the skip-rule (state-write pitfall, 2026-07-18):** `critique_10khr_runner.py --report-only` STILL calls `save_state()` inside `main()`, so every assessment run rewrites `last_run` to *now*. If you then apply the skip rule by comparing each SKILL.md mtime against `last_run`, you compare against the assessment instant — not the previous grind — so every skill reads as "modified since last_run" and the skip rule never trips (you grind skills that should be skipped). **Never run `--report-only` when you need the skip-rule intact.** To assess without mutating state: import the module and call `run_full_assessment()` / `score_skill()` directly — `import importlib.util; spec=importlib.util.spec_from_file_location("runner", "scripts/critique_10khr_runner.py"); runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)` — then call `runner.run_full_assessment()` (do NOT call `save_state`); or snapshot `last_run` from the state file before the call and restore it after. The 2026-07-18 finch:work 10khr pass imported the runner WITHOUT calling `main()`, so `last_run` stayed at the prior grind timestamp and the mtime/skip-rule comparison was valid (8 eligible targets ground, 9 correctly skipped).

**Safety-critical skill D3 fix (grind judgment, 2026-07-15):** When grinding a skill whose length is driven by non-negotiable safety constraints (e.g. `ocas-dispatch` — autonomous email send rules, eval-gap verification, JSONL corruption guards), do NOT cut the hard safety rules to satisfy the D3 line-count proxy. Instead extract REDUNDANT restatements to `references/` (keeping a one-line pointer in SKILL.md so nothing is orphaned). In the `ocas-dispatch` grind, 126 lines were offloaded this way (support-file-map rows → pointer; eval-gap closure cluster → `references/wave-closure-eval-gap-cluster.md`; duplicated JSONL/path pitfalls collapsed; `## Functions` merged into `## Commands`; deployment notes / lightweight-first pattern / voice-tone / journal-format compacted) — every safety rule stayed inline, D3 reached 5/5 at 448 lines. Cutting safety content to hit a line count would regress D7/D10, which reward comprehensive gotchas.

**Extraction can leave a DUPLICATE of the following section header (structural hazard, 2026-07-17):** When you delete a block ending right before a `## ` / `### ` header to clear D3, the programmatic slice or `patch` can leave the NEXT section's header intact while you ALSO re-insert a header when pasting the pointer — producing two consecutive identical headers. In the 2026-07-17 `util-github` grind, extracting three code blocks left `### Standard README Structure`, `### Enumerating Repos`, and `### Creating a Workflow File` each appearing TWICE (the original header followed by the re-inserted one). After ANY block extraction: `grep -nE '^#{2,3} ' SKILL.md` and scan for duplicate header titles; collapse any twin before committing. The duplicate is pure noise (D5/D3 drag) and is invisible to `wc -l` but obvious on a header scan.
- **D1 `metadata.hermes` must NEST, not be a literal top-level key**: Write `metadata:\n  hermes:\n    category: ...\n    tags: [...]` — NOT `metadata.hermes:\n  category: ...` at the top level. The latter creates a top-level key literally named `metadata.hermes` and the rubric's D1 check (`fm["metadata"]["hermes"]`) still scores 4 (missing). Confirm with a YAML parse (`fm = yaml.safe_load(content.split("---")[1]); fm["metadata"]["hermes"]["category"]`) before declaring D1=5.
- **Cross-profile KODA work requires `cross_profile=True`**: When the user targets a non-active profile's skills (e.g., "all of KODA's skills when active profile is indigo"), `write_file` and `patch` to `$HERMES_HOME/../<other>/skills/` trigger Hermes's cross-profile soft guard. Pass `cross_profile=True` after confirming the target profile. Reads (skill_view, search_files) are unrestricted; writes are guarded. Confirm with the user which profile owns the skills before editing — "KODA's skills" means the profile named koda, not the active profile.

- **Edit the LIVE profile skill, NOT the indigo-repo backup copy (workflow correction, 2026-07-15):** When the task is a routine in-place update to an existing skill (add an engine, fix wording, bump version), edit the live copy at `$HERMES_HOME/../<profile>/skills/<name>/` — that is what the agent actually loads. Do NOT also propagate the same edit to the backup repo copy at `<fs-root>/indigo-repo/skills/<name>/` unless the user explicitly asks. `indigo-repo` is the bootstrap/backup mirror; edits there are redundant at best and, if pushed, diverge from the live skill. If you already touched the backup, revert it: `git -C <fs-root>/indigo-repo checkout -- skills/<name>/` and `rm -f` any new untracked files you copied in, then confirm `git status --short skills/<name>/` is clean. (User: "You were supposed to update your live local skill not the skill backup.")

- **`patch` edits to SKILL.md frontmatter are literal — re-validate after (editing discipline, 2026-07-15):** The `new_string` in a `patch` call is applied verbatim, including any leading whitespace introduced by nesting the parameter inside the tool call's markdown. A 2-space-indented `new_string` will indent the YAML frontmatter and break it (the `---` fence and `metadata:` become indented → YAML no longer parses → the skill fails to load). After ANY `patch` to frontmatter or a Changelog: (1) re-read the file and confirm the `---` fence sits at column 0 with no leading indent; (2) `yaml.safe_load` the frontmatter and confirm `name`/`description` still parse. Also: when a section repeats headers (e.g. a `## Changelog` whose `### vX.Y.Z — DATE` line recurs in multiple entries), `patch` fails with "Found N matches" — anchor on a larger unique block (header + first-entry body), not the repeated header alone.

- **Grind the whole scope the user authorized — don't stall the loop behind a clarify (workflow correction, 2026-07-15):** When the user explicitly scopes the op ("all ocas and util skills", "the whole library", "every skill"), that statement IS the authorization to run the full grind loop. Sequence: assess all → grind lowest → re-assess → repeat until every target is at 50/50 OR the Skip Rule genuinely trips (unmodified since last run AND heuristic ≥44). Do NOT stop after grinding a single skill and re-ask scope via `clarify` — and if a clarify times out with no answer, default to *executing the stated instruction*, not parking. The Skip Rule governs re-grinding unmodified skills; it is NOT a license to quit after one. (User: "So you scored all but only worked in on one skill?" — the gap was a stalled loop, not a scoring miss. Corrective action: keep grinding; report progress, don't gate it on a re-confirmation the user already gave.)

- **Bulk script edits across skills corrupt files; `git clean -fd` destroys untracked work (git-safety incident, 2026-07-15):** Never write one script that rewrites scripts across many skills and run it without per-file verification. A `d9_fix.py` that added `--help` guards to ~50 scripts blew up: its `__main__` regex matched only double quotes, so on single-quoted/indented mains it appended a SECOND `if __name__ == "__main__":` block — 41 scripts across 9 skills stopped parsing. Recovery MUST be `git checkout -- .` (reverts tracked files in the skill repo). It must NOT be `git clean -fd` — that deletes untracked files with no history to restore them; in this incident it irreversibly deleted 9 pre-existing untracked skill files (the fixer only writes existing files, so it never created them — `clean` did). Rules: (1) Fix scripts one skill, one file at a time; after each edit verify `ast.parse` + `<script> --help` exits 0 before the next. (2) If a bulk script corrupts, recover with `git checkout -- .` per skill repo ONLY — never `git clean -fd`. (3) Before any `clean`, list untracked first (`git clean -nd` / `git status --short`) and confirm none are legitimate work. (4) Edit-script regexes must match both quote styles and indentation: `re.search(r'if\s+__name__\s*==\s*["\']__main__["\']\s*:\s*\n', txt)`. Full safe-recovery recipe + corrected regex + files lost in the incident: `references/critique-10khr-bulk-edit-git-safety.md`.

### Error Handling

Common critique/grind failures and how to recover without corrupting skills:

| Failure | Symptom | Handling |
|---------|---------|----------|
| YAML frontmatter won't parse after an edit | `yaml.safe_load` raises `ScannerError`; runner drops D1->1, D2->3 | The `---` fence was consumed by a programmatic slice. Re-insert `---` at the boundary; re-run the heuristic to confirm D1/D2 recover. Validate with `yaml.safe_load(content.split('---')[1])`. |
| Degraded read mode (`DaemonThreadPoolExecutor ... _initializer`) | `read_file` / `skill_view` fail cluster-wide | Switch ALL reads to `terminal()` (`cat` / `sed -n` / `grep -n` / `find`); `patch` / `write_file` writes still work. Do NOT abort. |
| Script `--help` crashes | `python3 script.py --help` exits non-zero or raises | Ensure the `--help` guard runs BEFORE any module-level side effect (argv read, top-level I/O, dependency import). Verify with `python3 script.py --help`, not just `ast.parse`. |
| Duplicate section header after block extraction | Same `### Heading` appears twice; invisible to `wc -l` | After any extraction run `grep -nE '^#{2,3} ' SKILL.md`; collapse twin headers. |
| State file claims a skill is 50/50 but it isn't | `skill_history` / `skills_improved` say done; on-disk file still <50 | The state file is testimony, not evidence. Re-score the actual SKILL.md on disk before trusting any claim; append verified before/after line counts when you DO improve. |
| Bulk script edit across many skills corrupts files | 41 scripts stop parsing after a regex miss | Recover with `git checkout -- .` per skill repo. NEVER `git clean -fd` (deletes untracked work). Fix one file at a time, verifying `ast.parse` + `--help` after each. |

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
- [ ] Copy B's scripts/references into A's `scripts/` and `references/` directories
- [ ] Append B's SKILL.md content as a new Part/section in A's SKILL.md
- [ ] Add `metadata.merged-from: <B-name>` to A's frontmatter
- [ ] Add B's triggers to A's `triggers:` list
- [ ] Archive B's entire directory to `$HERMES_HOME/../indigo/skills/.archive/<B-name>/`
- [ ] Update all references (cron jobs, SOUL.md, memory, other skills, cron prompts)

### Package Integrity
Before archiving, inspect the source as a **complete directory package** (may include `references/`, `templates/`, `scripts/`, `assets/`). If it has support files or relative links:
- Re-home every needed support file into the umbrella's canonical directories AND rewrite paths, OR
- Archive the entire original package unchanged.

**Never** flatten only SKILL.md into `references/` while leaving support files behind.

### Parallel-copy dedupe (symlink consolidation)

When the SAME skill family exists in 3 places — a git monorepo tree, a registry copy in an active profile, and/or a second profile — collapse to ONE canonical copy and symlink the rest. The full 7-step procedure (pick canonical by freshest mtime, back up to `_backup_<date>/`, merge by content not name, VERIFY superset before deleting, fix misnamed stragglers, symlink copies, commit+push) lives in `references/merge-parallel-copy-dedupe.md` — **When to read**: before any cross-tree skill dedupe or monorepo consolidation; never delete a source tree until its Step-3 superset check reports 0 missing files.

---

## 5. Rename Procedure

```bash
mv $HERMES_HOME/../indigo/skills/<old-name> $HERMES_HOME/../indigo/skills/<new-name>
```

Then update ALL of the following (check every box — missing any causes stale references):

**Inside the skill:**
1. `name:` field in frontmatter
2. Top-level heading (`# Old Name` → `# New Name`)
3. Any self-references in the body text
4. Support file map entries

**Cache files (critical — stale entries persist in system prompt):**
5. `~/.hermes/.skills_prompt_snapshot.json` — rename the cached key:
   (Python one-liner family: load JSON, `cache["new-name"] = cache.pop("old-name")`, write back — exact snippets in `references/rename-cache-updates.md`.)
6. `$HERMES_HOME/../indigo/skills/.usage.json` — rename the tracking key (same pattern)

**External references (grep across everything):**
7. `grep -r "old-name" $HERMES_HOME/../indigo/skills/ --include="*.md"` — update all SKILL.md references
8. `grep -r "old-name" $HERMES_HOME/../ --include="*.md"` — update profile-level references
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

1. Create directory: `$HERMES_HOME/../indigo/skills/<name>/` with proper frontmatter
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
   - If `source:` points to a monorepo (e.g., `https://github.com/<agent-handle>/utilities/tree/main/<name>`), the skill lives inside that monorepo. Sync to the monorepo subdirectory — do NOT create a standalone repo.
   - If `source:` points to its own repo (e.g., `https://github.com/<agent-handle>/<name>`), or there is no `source:` field, proceed with standalone repo creation below.
2. Audit and fix spec compliance
3. Sanitize private data (replace PII with placeholders)
4. **Only if standalone repo:** Create GitHub repo: `gh repo create <agent-handle>/skill-name --private --description "..."`
5. **If monorepo:** Clone the monorepo, sync skill files to the matching subdirectory, commit, and push. The monorepo is the single source of truth.
6. Add LICENSE, README.md, .gitignore (standalone only)
7. Commit and push
8. For public skills: `gh repo edit <agent-handle>/skill-name --visibility public`

### Quality & Security Evaluation
See `references/skill-publish-agentskill-evaluation-criteria.md` for the agentskill.sh 100/100 scoring pattern.

### GitHub Mechanics
- Full push recipe: `references/skill-publish-github-push-recipe.md`
- Bulk sync workflow for existing repos: `references/skill-publish-github-sync-existing-skills.md`. Automated daily sync runs via the UNIFIED `$HERMES_HOME/../indigo/scripts/skill-sync-all.sh` (cron `skill-sync-all`, 04:00 — SUPERSEDES the now-PAUSED `ocas-skilllab-sync` + `monorepo-skill-sync` crons) — it discovers every `ocas-*`/`util-*`/`eng-*` SKILL.md across both `indigo` and `koda` profiles at any depth, secret-gates, and sets the <agent-name> identity (the host global git config defaults to `Koda`, a different profile; on manual commits set `git -C <skill> config user.name "<agent-name>"` / `user.email "<agent-email>"` too). After any local skill edit, this keeps GitHub current without manual pushes.
- - **Do NOT ask which account to use when only one GitHub account is authenticated.** When `gh` is logged in to a single account (check: `gh auth status`), create the repo under that account. Asking "which account?" when only `<agent-handle>` is available is a wasted round-trip — the user's correction: "You only have your github account, <agent-handle>, so what are you asking for?" Pick the authenticated account and proceed; only ask if the user explicitly names a different one.
- **`git push` over HTTPS needs the `gh` credential helper (setup fix, 2026-07-17):** In this environment `gh auth status` shows an authenticated token, but `git push https://github.com/...` fails with `fatal: could not read Username for 'https://github.com': No such device or address` — git isn't using the `gh` token. Fix ONCE (globally): run `gh auth setup-git`. That writes a `[credential "https://github.com"]` helper pointing at `gh` into the global git config, so every subsequent `git push`/`git pull` over HTTPS authenticates via the token with no prompt. After any batch of skill edits, this is the difference between `git push` succeeding and the whole batch stalling on credentials. If a push fails on credentials, run `gh auth setup-git` and retry — don't fall back to manual token URLs (those trip the secret-scan gate).
- **Monorepo is the sync PUSH TARGET — never create per-skill repos for skills already under a monorepo (2026-07-15).** All `util-*` skills live in the single `<agent-handle>/utilities` monorepo (subdirs named WITHOUT the `util-` prefix: `buy`, `draw`, …); `eng-*` skills live in `<agent-handle>/eng-skills`. Each live skill's `source:` frontmatter already points to its monorepo subdir. So when syncing, the workflow is: clone the monorepo → copy live skill dir → monorepo subdir → commit → push `main`. Do NOT `git init` a standalone repo per skill, do NOT `gh repo create` per skill — that creates orphan repos the `source:` field doesn't reference (the user's redirect: "Util- skills have a monorepo, if there are new skills add them to the monorepo"). Always read `source:` first (rule at top of §6) before any repo operation.


- **Unified under ONE cron `skill-sync-all` (daily 04:00) → `$HERMES_HOME/../indigo/scripts/skill-sync-all.sh`** (SUPERSEDES the two older crons `ocas-skilllab-sync` + `monorepo-skill-sync`, now PAUSED). It DISCOVERS every `ocas-*`/`util-*`/`eng-*` SKILL.md across BOTH `indigo` and `koda` profiles at ANY depth by rule (no hard-coded lists — see `references/skill-sync-discovery.md`), so a new skill is never missed. ocas-* → own repo `<agent-handle>/<name>` (NEW repos strip the `ocas-` prefix per user directive; an existing prefixed remote is detected and reused, never duplicated); util-* → monorepo `<agent-handle>/utilities` (subdir strips `util-`); eng-* → monorepo `<agent-handle>/eng-skills` (subdir keeps `eng-`). All set the agent identity; idempotent (no changes ⇒ no push). The discovery guard rejects a `SKILL.md` nested inside another skill's repo (prevents recursion/dupe).
- - **`secret-scan.sh --working-tree` mode (added 2026-07-15):** full-history scanning blocks legitimate pushes because pre-existing committed doc prose (example credential URLs in `util-github/credential-purge.md`, the scanner's own regex literal in `util-github/scripts/secret_scan.sh`) flags as "secret." For a SYNC gate you only care about NEW secrets in the working tree, so pass `--working-tree` (scans working tree + `.git/config`, skips `git rev-list --all`). The script excludes itself (`secret-scan.sh`/`secret_scan.sh`) from the working-tree grep. Use full mode only for pre-publish audits where history matters.

---

## 6a. Share Procedure — Submit to Nous Research Optional Skills

Use when the user says "share this skill", "submit to Nous", "publish to optional-skills", or "contribute this skill".

The full procedure — config-policy gate (`metadata.hermes.config` declaration is mandatory or the PR is auto-closed), `forge_audit_skills.py` checks, category table, gotchas, sanitize checklist, and the score ≥45/50 + description ≤60 chars + secret-scan CLEAN prerequisites — lives in `references/skilllab-share-procedure.md`. **When to read**: immediately before preparing any Nous optional-skills submission.

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

The full remediation playbook — working-tree redaction, token-in-remote-URL strip, git history rewrite via `git filter-branch` (git-filter-repo is broken on this host) incl. reflog expire/gc/force-push verification, live-credential rotation guidance, and the masked-output pitfall — lives in `references/secret-history-rewrite.md`. **When to read**: when `secret-scan.sh` exits 1 and a real secret must be scrubbed from tree, config, or history.

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

The full file index (60+ reference and script entries, with a conditional **When to read** column) lives in `references/support-file-map.md` — read it **before any skilllab operation** for the per-task pointers (D1 audit, scoring, 10khr grind, publish/share, secret gate).

| File | What it is | When to read |
|------|-----------|--------------|
| `references/support-file-map.md` | Full 60+ entry index (refs + scripts) with per-task "When to read" pointers | **Before any** skilllab operation — pick the row matching your task |
| `references/monorepo-bulk-restructure.md` | Bulk rename/strip-prefix/move of many skills in a monorepo (token-map, verify-vs-API, eng-skills namespace) | When restructuring >1 monorepo skill at once (prefix strip, verb rename, parent-dir move) |
| `scripts/skill-sync-push.sh` | Commit + push all local skill repos with changes / ahead-of-upstream (idempotent; secret-gates) | When syncing local skills to GitHub after edits; set `DRY_RUN=1` for a no-op report |
| `scripts/secret-scan.sh` | Secret gate (full + `--working-tree` modes). Excludes itself | During Audit, Sanitize, Publish, Share — gate before any commit/push |
| `scripts/10khr_cron_verify.py` | Cron-safe eligibility + 5-dim on-disk verification harness (skip-rule aware, no save_state). THE canonical single entry point for an autonomous/cron 10khr pass — assesses all skills, applies the skip-rule against the runner's canonical STATE_FILE, and prints exactly which below-50 skills are real gaps vs over-scoring traps. Run it ALONE; do NOT also import the runner + re-walk mtimes by hand (duplicate effort + skip-rule-mutation risk if you call save_state). | During an autonomous 10khr grind pass — run FIRST; its output is authoritative for "what (if anything) to grind" |
| `references/grind-workflow.md` | Condensed 10khr grind SOP (rank → skip rule → score → fix → re-score → bookkeeping) | Before running an autonomous grind pass |
| `references/critique-10khr-grind-pitfalls.md` | Full dated narratives behind the distilled 10khr-mode rules | When a grind misbehaves: wrong target, score disagreement, state-file drift, or a D3/D5/D8/D9 heuristic anomaly |
| `references/cron-grind-resilience.md` | Cron-environment grind properties (degraded reads, execute_code block, write_file chroot) | During any autonomous/cron grind before relying on agentic read/write tools |
| `references/critique-rubric.md` | The 10-dimension scoring rubric (D1–D10) | When manually scoring a skill (Phase 2 of Critique) |
| `references/skilllab-pitfalls.md` | Full 60+ pitfall list (batch replace, YAML, caching, monorepo sync, git safety) | When an edit fails oddly, or before any bulk edit across skills |