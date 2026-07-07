# 10khr Runner — Heuristic Check Reference

_Exact string checks used by `critique_10khr_runner.py`'s `score_skill()` function._
_When grinding a skill to 50/50, use this to verify the runner will recognize your fix._

## D1: Frontmatter

| Check | Condition | Penalty |
|-------|-----------|---------|
| YAML parse failure | `yaml.safe_load(parts[1])` fails | -3 |
| Missing `name:` | `not fm.get("name")` | -2 |
| Missing `description:` | `not fm.get("description")` | -2 |
| `license` not in first 500 chars | `"license" not in content[:500].lower()` | -1 |
| Has `references/` but no `includes:` | `has_refs and "includes" not in str(fm)` | -1 |

**Key gotcha:** The `content[:500]` check means long YAML block-scalar descriptions push `license:` past position 500. Always place `license:` immediately after `name:`.

**Fix:** `license: MIT` on line 2, before description.

## D2: Description Quality

| Check | Condition | Bonus |
|-------|-----------|-------|
| Description > 50 chars | `len(desc) > 50` | +1 |
| Has "not for" (case-insensitive) | `"not for" in desc.lower()` | +1 |
| Has `triggers:` in frontmatter | `fm.get("triggers")` | +1 (capped at 5) |

**Baseline: 3.** Need all three bonuses for 5/5.

## D3: Conciseness (Code Ratio)

| Check | Condition | Score |
|-------|-----------|-------|
| Code ratio < 15% | `code_lines / total_lines < 0.15` | 5 |
| Code ratio < 20% | | 4 |
| Code ratio < 30% | | 3 |
| Code ratio ≥ 30% | | 2 |
| Total lines > 450 | | -1 penalty |

**Code lines** = lines where `l.strip().startswith("```")` (counts fence markers, not content between them).

## D4: Structure

| Check | Condition | Bonus |
|-------|-----------|-------|
| Has `references/` directory | `os.path.isdir(ref_dir)` | +1 |
| "when to read" in content | `"when to read" in content.lower()` | +1 |
| Total lines < 400 | `total_lines < 400` | +1 (capped at 5) |

**Baseline: 3.** Need all three for 5/5.

## D5: Instruction Clarity

| Check | Condition | Bonus |
|-------|-----------|-------|
| Has `## pipeline` or `## workflow` heading | in `content.lower()` | +1 |
| Has `## when to use` heading | in `content.lower()` | +1 |
| Has "example" anywhere | in `content.lower()` | +1 (capped at 5) |

**Baseline: 3.** Need all three for 5/5.

**Key gotcha:** The heading check is literal — `## When to Use` lowercases to `## when to use`. The word "example" anywhere in content triggers the bonus (section heading `## Examples` counts).

## D6: Freedom Calibration

| Check | Condition | Bonus |
|-------|-----------|-------|
| Has "why" or "because" | in `content.lower()` | +1 |
| Has "default" or "override" | in `content.lower()` | `min(5, d6)` (no-op if already 5) |

**Baseline: 4.** Need "why"/"because" for 5/5. The "default"/"override" check is a no-op ceiling, not a bonus.

## D7: Error Handling

| Check | Condition | Bonus |
|-------|-----------|-------|
| Has "gotcha" or "pitfall" | in `content.lower()` | +1 |
| Has "error" AND "handling" | both in `content.lower()` | +1 |

**Baseline: 3.** Need both for 5/5.

**Key gotcha:** Both words must appear — "error handling" as a phrase satisfies both checks. The section header `## Error Handling` triggers both bonuses.

## D8: Progressive Disclosure

| Check | Condition | Bonus |
|-------|-----------|-------|
| Has ≥3 `.md` files in `references/` | `len(ref_files) >= 3` | +1 |
| "when to read" in content | in `content.lower()` | +1 |

**Baseline: 3.** Need both for 5/5.

**Key gotcha:** Minimum 3 reference files required for the bonus. Two well-organized refs aren't enough.

## D9: Scripts Quality

- No scripts directory → **5/5 (N/A)**
- Has scripts but no `--help`/`usage`/`argparse` → **4/5**
- Has scripts with `--help` or `usage` or `argparse` → **5/5**

## D10: Completeness

| Check | Condition | Bonus |
|-------|-----------|-------|
| Has "gotcha" or "pitfall" | in `content.lower()` | +1 |
| Has "when not to use" | in `content.lower()` | +1 |

**Baseline: 3.** Need both for 5/5.

**Key gotcha:** "when not to use" is the exact literal string. `## When NOT to Use` lowercases to `## when not to use` and triggers the bonus.

---

## Scoring Summary Table

| Dim | Baseline | Need for 5/5 | Exact trigger |
|-----|----------|--------------|---------------|
| D1 | 5 | Fix deductions | `license` in first 500 chars, `includes:` if refs exist |
| D2 | 3 | All 3 bonuses | >50 chars, "not for", `triggers:` |
| D3 | 5 | Code ratio <15% | Under 20% is 4, under 30% is 3 |
| D4 | 3 | All 3 bonuses | Has refs, "when to read", <400 lines |
| D5 | 3 | All 3 bonuses | `## when to use` heading, "example" anywhere |
| D6 | 4 | +1 | "why" or "because" anywhere in content |
| D7 | 3 | Both bonuses | "pitfall"/"gotcha" + "error"+"handling" |
| D8 | 3 | Both bonuses | ≥3 ref files + "when to read" |
| D9 | 5 | N/A if no scripts | Else `--help`/`usage`/`argparse` |
| D10 | 3 | Both bonuses | "pitfall"/"gotcha" + "when not to use" |

## Common Failure Patterns

1. **D1 false deduction:** Long YAML description pushes `license:` past char 500 → place `license:` on line 2
2. **D5 stuck at 4:** Missing `## when to use` heading (having the content under another heading name doesn't count)
3. **D6 stuck at 4:** No "why"/"because" explanation for rigid rules
4. **D8 stuck at 4:** Only 2 reference files instead of 3
5. **D10 stuck at 4:** No "when not to use" literal phrase
