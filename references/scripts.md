# Skill Lab Scripts

Scripts for skill library maintenance: audit, critique, merge, sanitize.

| Script | Purpose |
|---|---|
| `scripts/skilllab.py` | Interactive skill library shell — audit, critique, merge, rename, delete, publish, sanitize |
| `scripts/_quick_rank.py` | One-shot heuristic ranking — prints the 10 lowest ocas-*/util-* skills (ranking only) |
| `scripts/heuristic_score.py` | Heuristic scoring of all ocas/util skills — ranking only, not a verdict |
| `scripts/critique_code_ratio.py` | Measure code-to-prose ratio in a SKILL.md file |
| `scripts/critique_10khr_runner.py` | Heuristic batch scorer for 10khr autonomous grinding (over-scores by 6-10pt) |
| `scripts/10khr_cron_verify.py` | Cron-safe eligibility + on-disk verification harness (run first in any autonomous pass) |
| `scripts/secret-scan.sh` | Secret-scan gate — exits 1 if secrets found (working tree, .git/config, history) |
| `scripts/skill-sync-push.sh` | Publish sync — pushes one skill repo to GitHub |
| `scripts/sanitize-skill-push-gate.sh` | Sanitize gate wrapper for pushes |
