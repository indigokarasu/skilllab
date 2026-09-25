## 2026-09-30 - In-Memory compile() & Pre-Read Pass-Through in Multi-Check Audits
**Learning:** Using `py_compile.compile()` in script validation loops creates unnecessary `__pycache__` disk I/O overhead, and re-opening the same `SKILL.md` file in multiple check functions causes redundant filesystem reads.
**Action:** Use in-memory `compile(raw, sp, "exec")` during single-pass script iteration and pass pre-read `text` to auxiliary check functions to eliminate disk I/O (~1.5x speedup across batch assessments).

## 2026-08-29 - Cache Sibling Directory Basenames for Dead Reference Resolution
**Learning:** Re-traversing all sibling directories and checking `os.path.exists()` for every subfolder on unresolved references creates O(N * S * K) filesystem stat syscalls, slowing down batch skill assessments by hundreds of milliseconds.
**Action:** Cache the set of sibling directory file basenames per skills root using `@functools.lru_cache` to reduce filesystem syscalls to O(S) dir listings during dead reference checks (~60x speedup).

## 2026-08-28 - Precise Token Prefixes in Fast-Path Keyword Pre-Filters
**Learning:** Using overly broad 2-letter substring keywords (like `'gh'`) in pre-filter tuples before regex search negates fast-path skipping for prose/markdown files due to common English words (`github`, `through`, `height`, etc.), causing ~26% unnecessary regex checks.
**Action:** Always use specific token prefixes (`ghp_`, `gho_`, etc.) for token pre-filtering rather than generic substrings.

## 2026-08-25 - Fix Unindented File Processing in Directory Traversals
**Learning:** An unindented block after `for file in files:` inside an `os.walk` loop causes `UnboundLocalError` on empty directories and silently drops modifications for all files except the last file in each directory, leading to wasted computation and broken sanitization.
**Action:** Always verify that per-file processing and file-saving operations in `os.walk` loops are indented strictly inside the inner `for file in files:` block.
