#!/usr/bin/env python3
"""Heuristic scoring of all ocas-* / util-* skills."""
import os, sys, json, yaml, re
from datetime import datetime, timezone

HERMES_ROOT = os.path.expanduser("~/.hermes")
SKILLS_DIR = os.path.join(HERMES_ROOT, "profiles", "indigo", "skills")

def find_all_skills():
    results = []
    seen = set()
    for root, dirs, files in os.walk(SKILLS_DIR):
        for d in sorted(dirs):
            if (d.startswith("ocas-") or d.startswith("util-")) and not d.startswith("_"):
                skill_path = os.path.join(root, d, "SKILL.md")
                if os.path.exists(skill_path) and d not in seen:
                    seen.add(d)
                    results.append((d, skill_path))
    return results

def check_scripts_help(script_dir):
    if not os.path.isdir(script_dir):
        return 5, [], 0
    scripts = [f for f in os.listdir(script_dir) 
               if f.endswith(('.py', '.sh')) and not f.startswith('_')]
    if not scripts:
        return 5, [], 0
    broken = []
    for s in scripts:
        path = os.path.join(script_dir, s)
        with open(path) as f:
            content = f.read().lower()
        has_help = '--help' in content or 'argparse' in content or '-h' in content or 'usage' in content
        if not has_help and s != 'test_helpers.py':
            broken.append(s)
    count = len(scripts)
    if count == 0 or not broken:
        return 5, [], count
    elif len(broken) < count / 2:
        return 3, broken, count
    else:
        return 1, broken, count

def check_correctness(skill_dir):
    findings = []
    d8 = 4
    refs_dir = os.path.join(skill_dir, "references")
    if not os.path.isdir(refs_dir):
        d8 = max(0, d8 - 1)
    return d8, findings

def check_frontmatter_parses(skill_dir):
    skill_md = os.path.join(skill_dir, "SKILL.md")
    with open(skill_md) as f:
        content = f.read()
    parts = content.split("---")
    if len(parts) < 3:
        return False
    try:
        fm = yaml.safe_load(parts[1])
        return fm is not None
    except Exception:
        return False

def check_dead_references(skill_dir):
    skill_md = os.path.join(skill_dir, "SKILL.md")
    with open(skill_md) as f:
        content = f.read()
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    dead = []
    for text, url in links:
        if url.startswith('references/'):
            ref_path = os.path.join(skill_dir, url)
            if not os.path.exists(ref_path):
                dead.append(url)
    return dead

def score_skill(name, path):
    with open(path) as f:
        content = f.read()
    lines = content.split("\n")
    skill_dir = os.path.dirname(path)
    
    # D1
    d1 = 5
    try:
        parts = content.split("---")
        fm = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    except:
        fm = {}
        d1 -= 3
    fm = fm or {}
    if not fm.get("name"): d1 -= 2
    if not fm.get("description"): d1 -= 2
    if "license" not in content[:500].lower(): d1 -= 1
    has_refs = os.path.isdir(os.path.join(skill_dir, "references"))
    if has_refs and "includes" not in str(fm): d1 -= 1
    
    # D2
    d2 = 3
    desc = str(fm.get("description", ""))
    if len(desc) > 50: d2 += 1
    if "not for" in desc.lower() or "NOT for" in desc: d2 += 1
    if fm.get("triggers"): d2 = min(5, d2 + 1)
    
    # D3
    total_lines = len(lines)
    code_lines = sum(1 for l in lines if l.strip().startswith("```"))
    ratio = (code_lines / total_lines * 100) if total_lines > 0 else 0
    if ratio < 15: d3 = 5
    elif ratio < 20: d3 = 4
    elif ratio < 30: d3 = 3
    else: d3 = 2
    approx_tokens = len(content) / 4
    if approx_tokens > 5000: d3 = max(1, d3 - 2)
    elif approx_tokens > 3500: d3 = max(1, d3 - 1)
    
    # D4
    d4 = 3
    if has_refs: d4 += 1
    if "when to read" in content.lower(): d4 += 1
    if approx_tokens < 5000: d4 = min(5, d4 + 1)
    else: d4 = max(1, d4 - 1)
    
    # D5
    d5 = 3
    if "## pipeline" in content.lower() or "## workflow" in content.lower(): d5 += 1
    if "## when to use" in content.lower(): d5 += 1
    if "example" in content.lower(): d5 = min(5, d5 + 1)
    
    # D6
    cl = content.lower()
    d6 = 4
    if "why" in cl or "because" in cl: d6 += 1
    if "default" in cl or "override" in cl: d6 = min(5, d6)
    
    # D7
    d7 = 3
    if "gotcha" in cl or "pitfall" in cl: d7 += 1
    if "error" in cl and "handling" in cl: d7 += 1
    
    # D8
    d8, cf = check_correctness(skill_dir)
    fm_valid = check_frontmatter_parses(skill_dir)
    if fm_valid is False: d8 = max(0, d8 - 2)
    dead = check_dead_references(skill_dir)
    if dead: d8 = max(0, d8 - min(2, len(dead)))
    
    # D9
    script_dir = os.path.join(skill_dir, "scripts")
    d9, broken_help, n_scripts = check_scripts_help(script_dir)
    
    # D10
    d10 = 3
    if "gotcha" in cl or "pitfall" in cl: d10 += 1
    if "when not to use" in cl: d10 += 1
    
    total = d1+d2+d3+d4+d5+d6+d7+d8+d9+d10
    
    return {
        "skill": name, "path": path, "total": total,
        "dims": {"D1": max(1,d1), "D2": min(5,d2), "D3": d3, "D4": min(5,d4),
                 "D5": min(5,d5), "D6": min(5,d6), "D7": min(5,d7), "D8": d8, "D9": d9, "D10": min(5,d10)},
        "lines": total_lines, "tokens": int(approx_tokens),
        "ratio": round(ratio, 1), "broken_scripts": broken_help, "dead_refs": dead,
        "n_scripts": n_scripts, "fm": fm, "has_refs": has_refs, "desc": desc
    }

# Main
skills = find_all_skills()
results = [score_skill(n, p) for n, p in skills]
results.sort(key=lambda x: x["total"])

print(f"\n{'Rank':<6}{'Skill':<45}{'Score':<10}{'Band'}")
print("-" * 75)
for i, r in enumerate(results, 1):
    band = "A" if r["total"] >= 40 else "B" if r["total"] >= 30 else "C"
    print(f"{i:<6}{r['skill']:<45}{r['total']}/50    {band}")

below_target = [r for r in results if r["total"] < 50]
print(f"\nSkills below 50/50: {len(below_target)}")
if below_target:
    lowest = below_target[0]
    print(f"\nLowest: {lowest['skill']} ({lowest['total']}/50)")
    print(f"Dimensions: {json.dumps(lowest['dims'], indent=2)}")
    print(f"Lines: {lowest['lines']}, Tokens: ~{lowest['tokens']}, Code ratio: {lowest['ratio']}%")
    print(f"Broken scripts: {lowest['broken_scripts']}")
    print(f"Dead refs: {lowest['dead_refs']}")
else:
    print("All at 50/50!")
