# Comparative Evaluation Methodology

Use when asked to evaluate/compare two repos, tools, skills, or approaches against each other.
Proven pattern from Ponytail vs 10xEng comparison (2026-10-07).

## 1. Fetch Both Repo Structures

```bash
# Get full file tree for each repo
gh api repos/<owner>/<repo>/git/trees/main?recursive=1 --jq '.tree[] | select(.type=="blob") | .path'

# Get repo metadata
gh api repos/<owner>/<repo> --jq '{name, description, defaultBranchRef, updatedAt, forkCount, parent}'
```

Why: the file tree reveals architecture (monorepo vs multi-skill, hooks vs no hooks,
test coverage, i18n, packaging) before reading a single file.

## 2. Read Core Files in Parallel

Batch reads — never sequential. For each repo, fetch:
- `README.md` — positioning, claims, benchmarks
- `SKILL.md` or equivalent — actual rules and workflow
- Key reference files — depth and structure
- Test files — verification rigor
- Hooks/integration files — portability

```bash
# Batch fetch via gh api + base64 decode
gh api repos/<owner>/<repo>/contents/<path> --jq '.content' | base64 -d
```

## 3. Compare Across Fixed Dimensions

Use these dimensions — they consistently reveal the real differences:

| Dimension | What to look for |
|-----------|------------------|
| **Structure** | Monorepo vs multi-file, skill count, reference organization |
| **Workflow** | Passive suggestion vs mandatory enforcement, convergence loops |
| **Automation** | Autonomous loops vs one-shot reports, compile-check integration |
| **Prioritization** | Severity systems, ranking criteria, anti-pattern guides |
| **Evidence** | Benchmarks, measured results, test coverage |
| **Portability** | Agent integrations, hooks, packaging, i18n |
| **Scripts** | CI-gateable tools, unit tests, --help support |
| **Documentation** | Examples, docs, support file maps |

## 4. Identify What Each Has That the Other Lacks

Two-column table. Be specific — name the file or feature, not a category.

```
| Area | A has | B has | Impact |
|------|-------|-------|--------|
| Hooks | 12 hooks | None | No session persistence |
| Benchmark | 39 tasks × 5 runs | None | No evidence it works |
```

## 5. Identify the Core Philosophical Difference

One sentence. This is the verdict that matters — the tables support it.

Examples:
- "A is passive, B is active — B enforces through workflow"
- "A is portable, B is deep — B trades reach for enforcement"
- "A has evidence, B has design — B is unproven but better structured"

## 6. Render the Verdict

Structure:
1. **What B improves over A** — table with specific features
2. **What A has that B lacks** — table with specific gaps
3. **Core philosophical difference** — one sentence
4. **Bottom line** — 2-3 sentences: is the improvement real, what's the gap, what would close it

## Pitfalls

- **Don't read files sequentially** — batch via `gh api` in parallel. Sequential reads waste 5+ round-trips.
- **Don't skip the file tree** — reading only SKILL.md misses hooks, tests, packaging, i18n. The tree reveals architecture.
- **Don't compare categories** — compare specific files and features. "Better structure" is meaningless; "6 skills → 1 skill with modes" is actionable.
- **Don't ignore the evidence gap** — a better design without benchmarks is unproven. Note it explicitly.
- **Don't flatten the verdict** — the philosophical difference (passive vs active, portable vs deep) is the decision-relevant insight. Tables support it, not replace it.
