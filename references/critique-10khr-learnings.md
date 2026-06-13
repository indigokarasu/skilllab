# 10khr Grind — Cumulative Learnings

_This file accumulates reusable fix patterns across all 10khr sessions. Session-specific detail lives in `10khr-YYYY-MM-DD.md` files._

## Scoring Inflation Patterns

1. **Structural heuristic scoring**: Checking for headings and counting references, then mapping to rubric scores. Over-estimates by 5-10 points.
2. **Template content scoring**: Generic When to Use / When NOT to Use bullets score 2-3 on D2/D5, not 4-5.
3. **Clustering detection**: If most skills score 44-47/50, scoring is inflated.

## Fix Patterns That Consistently Work

1. **Inline content to references/**: Moving storage layouts, OKR YAML, init sequences improves D3/D4/D8 by 1-2 points each.
2. **Code ratio**: Under 20% target.
3. **Description NOT clause**: Specific exclusions score 5, generic score 3.
4. **Duplicate section consolidation**: Removing duplicate When to Use sections with inconsistent casing (`## When to Use` + `## When to use`) improves D4 and D10.

## Process Corrections

- Assess ALL before fixing ANY
- Quality over speed
- Show the work
- Don't declare victory prematurely
- Run Bulk D1 Check as pre-pass before manual scoring

## Technical Gotchas

1. YAML block scalar truncation
2. Patch tool long-match failures
3. Code fence pairing verification
4. Subagent batch sizing (max 3)
5. Duplicate heading detection (check for both standard and lowercase variants)
6. `license: proprietary` is a D1 error — flag immediately
7. Second person in descriptions ("you", "your") is a D2 error
8. **Sequential patch fragility**: Multiple patches on one SKILL.md cause line-number drift and heading corruption. Prefer full-file rewrite for >3 section extractions. Always grep for `##` duplicates after any structural patch.
9. **Absolute path hygiene**: When moving code to references, scan for `/root/`, `/home/`, `/etc/` and replace with `{agent_root}/`
10. **Cross-skill reference verification**: Verify paths to other skills' files exist before embedding them

## Session: 2026-05-30 — ocas-custodian (43 → 47/50)

### What was fixed
1. **Light scan procedure** — One-liner expanded to 5 numbered inline steps with file paths and thresholds (D5: 4→5)
2. **Gotchas restructured** — 13 flat bullets reorganized into 4 subsections: Safety rules, Error patterns → actions (table), Operational notes, Cron script path troubleshooting. Removed duplicate cron script path content that was also in body (D7: 4→5)
3. **Duplicate body sections** — Two standalone body warnings ("⚠️ Cron script path rule" + "🛑 Escalation runner: do NOT oscillate") merged into one concise pointer (D10: 4→5, D3: maintained)
4. **Script agentic design** — `backup_system.sh` rewritten with `--help`, `--json`, `--dry-run`, meaningful exit codes (0/1/2), `set -euo pipefail`, error counting, and JSON output mode (D9: 3→4)

### Score impact
| Dim | Before | After | Delta |
|-----|--------|-------|-------|
| D5 | 4 | 5 | +1 |
| D7 | 4 | 5 | +1 |
| D9 | 3 | 4 | +1 |
| D10 | 4 | 5 | +1 |
| **Total** | **43** | **47** | **+4** |

### Key learning: Patch tool partial-read loss
When `read_file` is called with offset/limit pagination, the patch tool may report success but silently not persist the change. Always verify the file content after a patch — especially when the warning "was last read with offset/limit pagination" appears. Re-read the full file, then re-apply the patch.

### Key learning: Gotcha consolidation pattern
The most effective D7 fix is restructuring flat bullet lists into an **error-pattern → action** table for the top 5 recurring errors, plus subsections for safety rules and operational notes. This gives the agent a quick-scan reference instead of a wall of bullets.

### Remaining gap
D9 at 4 (not 5): `backup_all_hermes_data.sh` is still a 2-line wrapper with no `--help`. Could be improved but scored N/A since the primary script is now well-designed. To reach D9=5, the wrapper would need its own `--help`/flags.

---

## Session: 2026-05-31 — ocas-custodian (39 → 47/50)

### What was fixed
1. **Known Code Fixes section (~50 lines)** — Python code patches and escalation workflow moved to `references/known-code-fixes-and-cascade.md` (D3: 3→5, D8: 3→5)
2. **Duplicate Self-Update procedure** — 7-step inline copy removed; reference pointer only retained (D3: +delta)
3. **MCP Cascade section** — Bash snippet with absolute path moved to reference file; phantom cross-skill path (`util-ustodian/` — doesn't exist) fixed to `util-hermes-ops/` (D5: 4→5)
4. **Structural damage** — Patch tool ate `## Escalation Path` heading and created duplicate `## OKRs` heading. Both fixed. (D10: 4→5)
5. **Support file map** — Added 9 missing entries; updated 1 description (D4: 3→4)

### Score impact
| Dim | Before | After | Delta |
|-----|--------|-------|-------|
| D3 | 3 | 5 | +2 |
| D4 | 3 | 4 | +1 |
| D5 | 4 | 5 | +1 |
| D8 | 3 | 5 | +2 |
| D10 | 4 | 5 | +1 |
| **Total** | **39** | **47** | **+8** |

### Key learning: Sequential patch fragility
Sequential `patch` calls on the same SKILL.md are HIGHLY fragile. This session needed 6 patches to accomplish what should have been 2 operations. After fixing one patch's damage, the next patch would hit shifted content.

**Rule:** When extracting multiple inline sections to references in one pass, consider a **full-file rewrite** via `write_file` instead of sequential patches. Write the complete new SKILL.md content in memory (all sections accounted for), then write_file the result. This eliminates line-number drift and cross-patch interference.

**Rule:** After any patch that moves/removes content, always `grep -n '^## '` the file immediately to detect duplicate or orphaned headings.

### Key learning: Path hygiene in moved code
When moving code blocks to reference files:
1. Scan for absolute paths (`/root/`, `/home/`, `/etc/`) → replace with `{agent_root}/`
2. Scan for cross-skill paths → verify existence before embedding
3. Replace interactive commands with hardcoded paths with template-based equivalents

See `critique-10khr-2026-05-31.md` for full session details.
