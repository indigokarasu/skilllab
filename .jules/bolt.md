## 2026-10-27 - Prioritize In-Memory Set Lookups Over Filesystem Stat Operations in Reference Resolution
**Learning:** Checking `os.path.exists(skill_ref)` prior to checking cached sibling basenames executes redundant filesystem `stat` syscalls for every valid reference. Moving the O(1) in-memory `base in sibling_files` check ahead of `os.path.exists` completely eliminates `stat` syscall overhead for valid local and sibling references during dead reference audits.
**Action:** Always place O(1) in-memory set and cache lookups before `os.path.exists` filesystem stat calls in path resolution helper functions.

## 2026-10-26 - Fast-Path Keyword Pre-Checks for Multiline Verbose Regexes in Outbound Safety Guards
**Learning:** Running multiline verbose case-insensitive regexes (`_OUTBOUND.search` and `_OUTBOUND_SKIP.search`) across every script in skill assessment loops incurs heavy CPU execution overhead on safe scripts. Pre-checking candidate keyword tuples (`_OUTBOUND_KWS`) in lowercase script source short-circuits regex evaluation for safe scripts (~36x speedup). Additionally, replacing `content.split("---", 2)` with regex pattern matching avoids allocating large document tail slices during frontmatter parsing across batch skill scans.
**Action:** Always add fast candidate keyword tuple pre-checks before executing verbose multiline regexes, and use regex matching instead of `split()` when parsing header blocks from long documents.

## 2026-10-25 - Fast-Path String Pre-Checks for Multiline Regexes & Direct Open over os.path.exists in Safety Guards
**Learning:** Running multiline regexes (`_REF_PATTERN.findall` and `_MERGE_CONFLICT_PATTERN.search`) across every skill file without checking if trigger keywords exist creates unnecessary regex execution overhead on safe/clean files. Pre-checking trigger substrings (`any(k in text ...)` / `<<<<<<<` in text) skips regex scans on files without match candidates (~30-40% faster). Additionally, pre-checking `os.path.exists` in `_can_send` before opening files issues redundant stat syscalls; relying directly on `OSError` handling in `try...with open()` eliminates unnecessary file existence checks.
**Action:** Always add fast substring pre-checks before executing multiline regex searches and replace `os.path.exists` with direct file opening inside `try...except OSError` blocks.

## 2026-10-24 - Pre-Read File Filtering in Quarantine and Sanitization Loops
**Learning:** Opening and reading file contents into memory (`open(path).read()`) before evaluating relocation or quarantine conditions causes redundant disk I/O, memory allocations, and `UnicodeDecodeError` exceptions on non-text artifacts. Evaluating quarantine pattern matches on file names before opening files avoids unnecessary disk I/O and prevents decoding failures on binary session artifacts.
**Action:** Always evaluate file-relocation and quarantine criteria before opening and reading file contents in file traversal loops.

## 2026-10-23 - Fast-Path Directory Entry Pre-Check Before Sibling Package __init__.py stat Calls
**Learning:** Checking `os.path.exists(os.path.join(script_dir, base, "__init__.py"))` for every imported module issues hundreds of redundant filesystem stat syscalls for non-sibling 3rd-party dependencies. Pre-checking `base in dir_files` (where `dir_files` is `set(os.listdir(script_dir))`) short-circuits stat syscalls for all non-sibling imports, yielding a ~24x speedup in `check_module_scope_imports`.
**Action:** Always verify `base in dir_files` before calling `os.path.exists(os.path.join(script_dir, base, "__init__.py"))`.

## 2026-10-22 - Fast-Path Entrypoint Pre-Filtering Before Script Execution
**Learning:** In verification harnesses checking script execution (`--help`), spawning Python/Bash subprocesses (`subprocess.run`) on test entrypoints or non-CLI helper modules incurs ~50ms process creation overhead per file and triggers false-positive failures. Filtering scripts with fast static entrypoint checks (`_is_cli_entrypoint` & `_is_test_entrypoint`) and outbound safety guards (`_can_send`) before spawning subshells eliminates non-CLI subprocess execution completely while preserving safety.
**Action:** Always pre-filter script lists with static CLI entrypoint and outbound safety checks before running `--help` subprocess execution loops.

## 2026-10-21 - mtime-Keyed LRU Caching for Script Source Reads, Compilation, and AST Parsing
**Learning:** In multi-check skill rubric assessments (D8/D9 correctness, script help, and import checks), opening script files repeatedly without context managers (`io.open().read()`), re-compiling bytecodes (`compile()`), and re-parsing ASTs (`ast.parse()`) across separate dimension checkers creates thousands of redundant disk reads, unclosed file descriptor leaks, and CPU-bound compiles. Caching file reads and compilation checks with `@functools.lru_cache(maxsize=256)` keyed on `(path, mtime)` eliminates disk I/O and CPU overhead while guaranteeing automatic cache invalidation when scripts are modified (~2.4x speedup across assessment loops).
**Action:** Wrap repeated script file reads, compilation checks, and AST parsing in `(path, mtime)`-keyed LRU cache helpers using context managers (`with io.open(...) as f:`).

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
