# Changelog

## [3.7.0] - 2026-09-16

### Added
- **Local skillgrade eval runner** — integrate `skillgrade` CLI for local offline evaluation of a skill's `eval.yaml` suite before submitting variants; gates candidate patches prior to formal `ocas-fellow` benchmarking. Note a missing `eval.yaml` in the critique rather than skipping evaluation.

## [3.7.1] - 2026-09-24

### Fixed
- Skillgrade note no longer points at non-existent paths (dead-reference finding cleared; tooling marked as pending until a `skillgrade` CLI exists).
- Deduplicated the interactive-menu references — unique sentence merged into `interactive-menu.md`; redundant `interactive-menu-pattern.md` removed (git history preserves it).
- Support file map completeness — indexed 9 previously-orphaned references + 6 scripts.

### Changed
- `scripts/_quick_rank.py` gained a proper `--help` guard (previously `--help` ran the full ranking).
- `references/scripts.md` script index brought up to date.

## [3.7.2] - 2026-09-25

### Fixed
- `critique_10khr_runner.py` module-scope import check no longer misclassifies: stdlib detection now uses `sys.stdlib_module_names` (zoneinfo/fcntl were missing from the regex whitelist), and bundled sibling modules whose own import chains stay within the bundle are not flagged (recursive, cycle-safe). Surfaced while verifying `ocas-rally` (49/50 → 50/50); genuine third-party module-scope imports are still flagged.
