#!/usr/bin/env python3
"""
10khr_runner.py — Autonomous skill improvement engine.

Grinds on the lowest-scoring ocas-* / util-* skill until it hits 50/50,
then moves to the next one. After every 5 skills improved, re-runs
the full library assessment.

Usage:
    python3 10khr_runner.py [--skills-dir <dir>] [--report-only] [--all-profiles]

Workflow:
    1. Find all ocas-* and util-* skills across the entire skill library
    2. Score each using the critique rubric (via agent invocation)
    3. Sort by score (lowest first)
    4. For each skill below 50/50:
        a. Run critique.iterate until 50/50
        b. Log learnings to journal
    5. After every 5 skills, re-assess entire library
    6. Update the learning journal with new patterns discovered

Directory discovery:
    By default, scans the active profile's skills directory and all subdirectories.
    With --all-profiles, scans all profiles under ~/.hermes/profiles/.
    Always uses recursive glob — skills may live at any depth (e.g.,
    infrastructure/util-vps-cleanup, software-development/ocas-10xeng).
"""

import json
import os
import sys
import glob
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────────────────────

# Default: scan the indigo profile (active profile) recursively
# Resolve against HERMES_ROOT or /root/.hermes to avoid broken ~ expansion
# when HOME is set to a profile chroot (e.g., /root/.hermes/profiles/indigo/home)
_HERMES_ROOT = os.environ.get("HERMES_ROOT", "/root/.hermes")
DEFAULT_SKILLS_DIR = os.path.join(_HERMES_ROOT, "profiles", "indigo", "skills")
DEFAULT_PROFILE_SKILLS_DIR = os.path.join(_HERMES_ROOT, "skills")
TARGET_SCORE = 50
REASSESS_INTERVAL = 5  # re-score full library after N skills improved
STATE_FILE = os.path.join(_HERMES_ROOT, "skills", "ocas-critique", "commons", "data", "ocas-critique", "10khr-state.json")

# ─── Helpers ─────────────────────────────────────────────────────────────────


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "version": 1,
        "started_at": None,
        "last_run": None,
        "skills_improved": 0,
        "total_iterations": 0,
        "skill_history": [],
        "current_target": None,
    }


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def find_all_skills(skills_dir: str = None, all_profiles: bool = False) -> list:
    """
    Return sorted list of (name, path) tuples for all ocas-* and util-* skills.

    Uses recursive glob to find skills at any depth:
      - ~/.hermes/profiles/indigo/skills/ocas-foo/SKILL.md
      - ~/.hermes/profiles/indigo/skills/infrastructure/util-bar/SKILL.md
      - ~/.hermes/profiles/koda/skills/software-development/ocas-baz/SKILL.md

    Deduplicates by skill name (first found wins).
    """
    search_roots = []

    if all_profiles:
        # Scan all profiles under <HERMES_ROOT>/profiles/
        # Use HERMES_ROOT (NOT expanduser("~/.hermes/profiles")): under a profile
        # chroot (HOME=/root/.hermes/profiles/<profile>/home) expanduser resolves to
        # the active profile's home, silently dropping every OTHER profile (e.g. koda).
        # Confirmed bug 2026-07-15 — --all-profiles reported 60 skills and missed
        # koda/ocas-eng-debug until this was fixed.
        profiles_dir = os.path.join(_HERMES_ROOT, "profiles")
        if os.path.isdir(profiles_dir):
            for profile in sorted(os.listdir(profiles_dir)):
                profile_skills = os.path.join(profiles_dir, profile, "skills")
                if os.path.isdir(profile_skills):
                    search_roots.append(profile_skills)
        # Also include the default profile
        if os.path.isdir(DEFAULT_PROFILE_SKILLS_DIR):
            search_roots.append(DEFAULT_PROFILE_SKILLS_DIR)
    elif skills_dir:
        search_roots.append(skills_dir)
    else:
        # Default: active profile + default profile
        search_roots.append(DEFAULT_SKILLS_DIR)
        if os.path.isdir(DEFAULT_PROFILE_SKILLS_DIR):
            search_roots.append(DEFAULT_PROFILE_SKILLS_DIR)

    seen = set()
    seen_realpaths = set()
    results = []

    for root in search_roots:
        # Resolve the root to its real path to avoid symlink duplicates
        real_root = os.path.realpath(root)
        if real_root in seen_realpaths:
            continue
        seen_realpaths.add(real_root)

        # Recursive glob: finds SKILL.md at any depth
        for path in sorted(glob.glob(f"{root}/**/SKILL.md", recursive=True)):
            real_path = os.path.realpath(path)
            name = os.path.basename(os.path.dirname(real_path))
            # Only include ocas-* and util-* prefixed skills
            if not (name.startswith("ocas-") or name.startswith("util-")):
                continue
            if name in seen:
                continue
            if ".archive" in real_path:
                continue
            seen.add(name)
            results.append((name, real_path))

    return results


def score_skill(skill_name: str, skill_path: str) -> dict:
    """
    Score a skill by reading its SKILL.md and evaluating the 10 rubric dimensions.
    Returns a dict with scores per dimension and total.
    This is a local heuristic score — the agent does the real scoring via critique.assess.
    """
    if not os.path.exists(skill_path):
        return {"total": 0, "dimensions": {}, "error": "SKILL.md not found"}

    with open(skill_path) as f:
        content = f.read()
    lines = content.split("\n")

    scores = {}

    # ── D1: Frontmatter ──
    d1 = 5
    try:
        import yaml
        parts = content.split("---")
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
        else:
            fm = {}
            d1 -= 2
    except Exception:
        fm = {}
        d1 -= 3

    if not fm.get("name"):
        d1 -= 2
    if not fm.get("description"):
        d1 -= 2
    if "license" not in content[:500].lower():
        d1 -= 1
    skill_dir = os.path.dirname(skill_path)
    has_refs = os.path.isdir(os.path.join(skill_dir, "references"))
    if has_refs and "includes" not in str(fm):
        d1 -= 1
    scores["D1"] = max(1, d1)

    # ── D2: Description quality ──
    d2 = 3
    desc = str(fm.get("description", ""))
    if len(desc) > 50:
        d2 += 1
    if "not for" in desc.lower() or "NOT for" in desc:
        d2 += 1
    if fm.get("triggers"):
        d2 = min(5, d2 + 1)
    scores["D2"] = min(5, d2)

    # ── D3: Conciseness (code ratio) ──
    total_lines = len(lines)
    code_lines = sum(1 for l in lines if l.strip().startswith("```"))
    ratio = (code_lines / total_lines * 100) if total_lines > 0 else 0
    if ratio < 15:
        d3 = 5
    elif ratio < 20:
        d3 = 4
    elif ratio < 30:
        d3 = 3
    else:
        d3 = 2
    if total_lines > 450:
        d3 = max(1, d3 - 1)
    scores["D3"] = d3

    # ── D4: Structure ──
    d4 = 3
    if has_refs:
        d4 += 1
    if "when to read" in content.lower():
        d4 += 1
    if total_lines < 400:
        d4 = min(5, d4 + 1)
    scores["D4"] = min(5, d4)

    # ── D5: Instruction clarity ──
    d5 = 3
    if "## pipeline" in content.lower() or "## workflow" in content.lower():
        d5 += 1
    if "## when to use" in content.lower():
        d5 += 1
    if "example" in content.lower():
        d5 = min(5, d5 + 1)
    scores["D5"] = min(5, d5)

    # ── D6: Freedom calibration ──
    d6 = 4
    content_lower = content.lower()
    if "why" in content_lower or "because" in content_lower:
        d6 += 1
    if "default" in content_lower or "override" in content_lower:
        d6 = min(5, d6)
    scores["D6"] = min(5, d6)

    # ── D7: Error handling ──
    d7 = 3
    if "gotcha" in content.lower() or "pitfall" in content.lower():
        d7 += 1
    if "error" in content.lower() and "handling" in content.lower():
        d7 += 1
    scores["D7"] = min(5, d7)

    # ── D8: Progressive disclosure ──
    d8 = 3
    ref_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(ref_dir):
        ref_files = [f for f in os.listdir(ref_dir) if f.endswith(".md")]
        if len(ref_files) >= 3:
            d8 += 1
        if "when to read" in content.lower():
            d8 += 1
    scores["D8"] = min(5, d8)

    # ── D9: Scripts quality ──
    script_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(script_dir):
        scripts = [f for f in os.listdir(script_dir) if f.endswith((".py", ".sh"))]
        if scripts:
            # Scan ALL scripts (not just the first 3) for --help/usage/argparse.
            # Sampling only the first 3 hides real gaps when most scripts lack --help
            # (e.g. a 19-script skill with 7 missing --help still scored D9=5 because
            # the first 3 happened to have it). Confirmed gap 2026-07-14.
            missing_help = []
            for s in scripts:
                sp = os.path.join(script_dir, s)
                try:
                    with open(sp) as sf:
                        sc = sf.read()
                except Exception:
                    continue
                if "--help" not in sc and "usage" not in sc.lower() and "argparse" not in sc:
                    missing_help.append(s)
            if not missing_help:
                d9 = 5
            elif len(missing_help) < len(scripts) / 2:
                d9 = 4
            else:
                d9 = 3
            scores["D9"] = d9
        else:
            scores["D9"] = 4
    else:
        scores["D9"] = 5  # N/A — no scripts needed

    # ── D10: Completeness ──
    d10 = 3
    if "gotcha" in content.lower() or "pitfall" in content.lower():
        d10 += 1
    if "when not to use" in content.lower():
        d10 += 1
    scores["D10"] = min(5, d10)

    total_score = sum(scores.values())
    return {
        "skill": skill_name,
        "path": skill_path,
        "total": total_score,
        "dimensions": scores,
        "line_count": total_lines,
        "code_ratio": round(ratio, 1),
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def run_full_assessment(skills_dir: str = None, all_profiles: bool = False) -> list:
    """Score all ocas-* / util-* skills and return sorted list (lowest first)."""
    skills = find_all_skills(skills_dir, all_profiles)
    results = []
    for name, path in skills:
        result = score_skill(name, path)
        results.append(result)
    results.sort(key=lambda r: r["total"])
    return results


def generate_report(assessment: list, state: dict) -> str:
    """Generate a text report of current library state."""
    lines = [
        f"# 10khr Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"",
        f"Skills assessed: {len(assessment)}",
        f"Skills improved this session: {state.get('skills_improved', 0)}",
        f"Total iterations: {state.get('total_iterations', 0)}",
        f"",
        f"| Rank | Skill | Score | Band |",
        f"|------|-------|-------|------|",
    ]
    for i, r in enumerate(assessment, 1):
        band = "A" if r["total"] >= 40 else "B" if r["total"] >= 30 else "C"
        marker = " ← current target" if r["skill"] == state.get("current_target") else ""
        lines.append(f"| {i} | {r['skill']} | {r['total']}/50 | {band} |{marker}")

    below_target = [r for r in assessment if r["total"] < TARGET_SCORE]
    lines.extend([
        f"",
        f"Skills below {TARGET_SCORE}/50: {len(below_target)}",
    ])
    if state.get("current_target"):
        lines.append(f"Current grinding target: {state['current_target']}")

    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    import argparse
    parser = argparse.ArgumentParser(description="10khr skill improvement engine")
    parser.add_argument("--skills-dir", default=None,
                        help="Path to skills directory (default: active profile)")
    parser.add_argument("--all-profiles", action="store_true",
                        help="Scan all profiles under ~/.hermes/profiles/")
    parser.add_argument("--report-only", action="store_true",
                        help="Only assess, don't output grinding target")
    args = parser.parse_args()

    report_only = args.report_only
    skills_dir = args.skills_dir
    all_profiles = args.all_profiles
    state = load_state()

    if not state.get("started_at"):
        state["started_at"] = datetime.now(timezone.utc).isoformat()

    # Step 1: Full assessment
    assessment = run_full_assessment(skills_dir, all_profiles)
    state["last_run"] = datetime.now(timezone.utc).isoformat()

    # Step 2: Find lowest-scoring skill below target
    below_target = [r for r in assessment if r["total"] < TARGET_SCORE]

    if not below_target:
        print("All ocas-* / util-* skills are at 50/50. Nothing to grind.")
        print(generate_report(assessment, state))
        save_state(state)
        return

    # Pick the lowest
    target = below_target[0]
    state["current_target"] = target["skill"]

    if report_only:
        print(generate_report(assessment, state))
        save_state(state)
        return

    # Step 3: Output the target for the agent to work on
    print(f"TARGET: {target['skill']} ({target['total']}/50)")
    print(f"PATH: {target['path']}")
    print(f"DIMENSIONS: {json.dumps(target['dimensions'], indent=2)}")
    print(f"\n--- FULL ASSESSMENT ---")
    print(generate_report(assessment, state))

    # Check if we need a re-assessment (every 5 skills)
    improved = state.get("skills_improved", 0)
    if improved > 0 and improved % REASSESS_INTERVAL == 0:
        print(f"\n*** RE-ASSESSMENT TRIGGERED ({improved} skills improved) ***")
        print("Re-running full library assessment before continuing...")

    save_state(state)


if __name__ == "__main__":
    main()
