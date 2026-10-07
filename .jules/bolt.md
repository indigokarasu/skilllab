## 2026-10-20 - Direct os.listdir with Exception Handling Over os.path.isdir Pre-Checks
**Learning:** Pre-checking `os.path.isdir()` before calling `os.listdir()` issues unnecessary `stat` system calls. In loops scanning known subdirectories (e.g. `references`, `scripts`, `assets`), calling `os.listdir()` directly inside a `try...except OSError` block relies on the underlying filesystem syscall failure (e.g. `ENOTDIR` or `ENOENT`), eliminating ~5 redundant `stat` syscalls per directory entry.
**Action:** Replace `if os.path.isdir(path): for f in os.listdir(path)` with direct `try: for f in os.listdir(path)` in directory traversal loops.

## 2026-10-19 - Fast-Path os.path.isdir & os.listdir Over glob.glob in Verification Loops
**Learning:** `glob.glob()` on optional skill subdirectories (like `.github/workflows/*.yml` or `scripts/*`) initializes regex pattern matchers and attempts directory listings even when subdirectories do not exist. Guarding with `os.path.isdir()` and using `os.listdir()` completely skips missing subdirectories without glob pattern matching overhead.
**Action:** Replace `glob.glob()` in batch verification loops with `os.path.isdir()` checks and `os.listdir()` iterations.

## 2026-10-18 - In-Memory Helper Invocation in Cron Verification Loops
**Learning:** Invoking sibling CLI scripts (like `critique_code_ratio.py`) via `subprocess.run([sys.executable, ...])` inside iteration loops incurs ~50ms Python process startup overhead per skill. Importing the module directly and invoking its underlying function in-memory eliminates interpreter startup and achieves <0.1ms per item execution (~500x speedup).
**Action:** Always import sibling tools or load their modules in-memory (`importlib.util`) rather than spawning subprocesses during verification/cron loops.

## 2026-10-15 - Prune Skill Subdirectories in os.walk Discovery
**Learning:** `os.walk` in skill discovery functions continues descending into `references/`, `scripts/`, `assets/`, `templates/`, and `tests/` after finding a `SKILL.md`. Since skill directories never contain nested sub-skills, continuing directory traversal creates hundreds of redundant filesystem syscalls.
**Action:** Immediately clear `dirs[:] = []` upon finding `SKILL.md` in `files` during `os.walk` skill scanning loops (~5x speedup).

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
