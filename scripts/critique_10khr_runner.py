#!/usr/bin/env python3
"""
10khr_runner.py — Autonomous skill improvement engine.

Grinds on the lowest-scoring ocas-* skill until it hits 50/50,
then moves to the next one. After every 5 skills improved, re-runs
the full library assessment.

Usage:
    python3 10khr_runner.py [--skills-dir <dir>] [--report-only]

Workflow:
    1. Find all ocas-* skills
    2. Score each using the critique rubric (via agent invocation)
    3. Sort by score (lowest first)
  4. For each skill below 50/50:
        a. Run critique.iterate until 50/50
        b. Log learnings to journal
  5. After every 5 skills, re-assess entire library
    6. Update the learning journal with new patterns discovered

State tracked in:
    ~/.hermes/skills/ocas-critique/commons/data/ocas-critique/10khr-state.json
"""

import json
import os
import sys
import glob
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────────────────────

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")
OCAS_PREFIX = "ocas-"
TARGET_SCORE = 50
REASSESS_INTERVAL = 5  # re-score full library after N skills improved
STATE_FILE = os.path.expanduser(
    "~/.hermes/skills/ocas-critique/commons/data/ocas-critique/10khr-state.json"
)

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


def find_ocas_skills(skills_dir: str = None) -> list[str]:
    """Return sorted list of ocas-* skill directory paths."""
    if skills_dir is None:
        skills_dir = SKILLS_DIR
    skills = []
    # Top-level ocas-* dirs
    for d in sorted(glob.glob(os.path.join(skills_dir, f"{OCAS_PREFIX}*/SKILL.md"))):
        skills.append(os.path.dirname(d))
    # Subdirectory ocas-* dirs (infrastructure/, ocas/)
    for d in sorted(glob.glob(os.path.join(skills_dir, "*/", f"{OCAS_PREFIX}*/SKILL.md"))):
        skills.append(os.path.dirname(d))
    return skills


def score_skill(skill_path: str) -> dict:
    """
    Score a skill by reading its SKILL.md and evaluating the 10 rubric dimensions.
    Returns a dict with scores per dimension and total.
    This is a local heuristic score — the agent does the real scoring via critique.assess.
    """
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return {"total": 0, "dimensions": {}, "error": "SKILL.md not found"}

    with open(skill_md) as f:
        content = f.read()
    lines = content.split("\n")

    scores = {}
    skill_name = os.path.basename(skill_path)

    # ── D1: Frontmatter ──
    d1 = 5
    if "name:" not in content[:500]:
        d1 -= 2
    if "description:" not in content[:500]:
        d1 -= 2
    if "license:" not in content[:500]:
        d1 -= 1
    if "includes:" not in content[:2000] and os.path.isdir(os.path.join(skill_path, "references")):
        d1 -= 1
    if "metadata:" not in content[:2000]:
        d1 -= 0  # optional
    scores["D1"] = max(1, d1)

    # ── D2: Description quality ──
    d2 = 3  # baseline: has description
    desc_match = None
    for line in lines[:20]:
        if "description:" in line.lower():
            # Check if it's a block scalar
            if ">" in line or "|" in line:
                d2 += 1
            break
    # Check for NOT clause
    if "not for" in content[:1000].lower():
        d2 += 1
    # Check for trigger keywords
    if "trigger" in content[:1000].lower():
        d2 += 1
    scores["D2"] = min(5, d2)

    # ── D3: Conciseness (code ratio) ──
    from critique_code_ratio import measure_code_ratio
    ratio_result = measure_code_ratio(skill_md)
    ratio = ratio_result["ratio"]
    total = ratio_result["total_lines"]
    if ratio < 15:
        d3 = 5
    elif ratio < 20:
        d3 = 4
    elif ratio < 30:
        d3 = 3
    else:
        d3 = 2
    # Line count penalty
    if total > 450:
        d3 = max(1, d3 - 1)
    scores["D3"] = d3

    # ── D4: Structure ──
    d4 = 3
    if os.path.isdir(os.path.join(skill_path, "references")):
        d4 += 1
    if "support file map" in content.lower() or "when to read" in content.lower():
        d4 += 1
    if total < 400:
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
    d6 = 4  # most skills are well-calibrated
    if "rules:" in content.lower() and "exact" in content.lower():
        d6 = 5
    scores["D6"] = d6

    # ── D7: Error handling ──
    d7 = 3
    if "gotcha" in content.lower() or "pitfall" in content.lower():
        d7 += 1
    if "error" in content.lower() and "handling" in content.lower():
        d7 += 1
    scores["D7"] = min(5, d7)

    # ── D8: Progressive disclosure ──
    d8 = 3
    ref_dir = os.path.join(skill_path, "references")
    if os.path.isdir(ref_dir):
        ref_files = [f for f in os.listdir(ref_dir) if f.endswith(".md")]
        if len(ref_files) >= 3:
            d8 += 1
        if "when to read" in content.lower():
            d8 += 1
    scores["D8"] = min(5, d8)

    # ── D9: Scripts quality ──
    script_dir = os.path.join(skill_path, "scripts")
    if os.path.isdir(script_dir):
        scripts = [f for f in os.listdir(script_dir) if f.endswith((".py", ".sh"))]
        if scripts:
            d9 = 4  # has scripts, assume decent
            # Check for --help or usage
            for s in scripts[:3]:
                sp = os.path.join(script_dir, s)
                with open(sp) as sf:
                    sc = sf.read()
                if "--help" in sc or "usage" in sc.lower() or "argparse" in sc:
                    d9 = 5
                    break
            scores["D9"] = d9
        else:
            scores["D9"] = 4  # empty scripts dir
    else:
        scores["D9"] = 5  # N/A — no scripts needed

    # ── D10: Completeness ──
    d10 = 3
    if "gotcha" in content.lower() or "pitfall" in content.lower():
        d10 += 1
    if "when not to use" in content.lower():
        d10 += 1
    if "update" in content.lower() and "command" in content.lower():
        d10 = min(5, d10 + 1)
    scores["D10"] = min(5, d10)

    total_score = sum(scores.values())
    return {
        "skill": skill_name,
        "path": skill_path,
        "total": total_score,
        "dimensions": scores,
        "line_count": total,
        "code_ratio": round(ratio, 1),
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def run_full_assessment(skills_dir: str = None) -> list[dict]:
    """Score all ocas-* skills and return sorted list (lowest first)."""
    skills = find_ocas_skills(skills_dir)
    results = []
    for sp in skills:
        result = score_skill(sp)
        results.append(result)
    results.sort(key=lambda r: r["total"])
    return results



def generate_report(assessment: list[dict], state: dict) -> str:
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
    parser.add_argument("--skills-dir", default=os.path.expanduser("~/.hermes/skills"),
                        help="Path to skills directory")
    parser.add_argument("--report-only", action="store_true",
                        help="Only assess, don't output grinding target")
    args = parser.parse_args()

    report_only = args.report_only
    skills_dir = args.skills_dir
    state = load_state()

    if not state.get("started_at"):
        state["started_at"] = datetime.now(timezone.utc).isoformat()

    # Step 1: Full assessment
    assessment = run_full_assessment(skills_dir)
    state["last_run"] = datetime.now(timezone.utc).isoformat()

    # Step 2: Find lowest-scoring skill below target
    below_target = [r for r in assessment if r["total"] < TARGET_SCORE]

    if not below_target:
        print("All ocas-* skills are at 50/50. Nothing to grind.")
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
    # The actual fix work is done by the agent via critique.iterate
    # This script identifies WHAT to work on; the agent does the HOW
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
