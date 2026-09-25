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
