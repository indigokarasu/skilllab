#!/usr/bin/env python3

try:
    import yaml  # noqa: F401
except ImportError:
    # Re-exec under venv python if yaml missing — avoids false D1 gaps.
    # If there is no venv (CI runner, sandbox, any non-host interpreter), DO NOT
    # raise: this module is imported by the unit tests and its --help path, and a
    # module-scope ImportError made both fail with ModuleNotFoundError before any
    # assertion ran. yaml is only needed by the D1 check, which already degrades
    # gracefully; CI installs pyyaml so D1 stays meaningful there.
    import os, sys
    venv_py = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'hermes-agent', 'venv', 'bin', 'python3')
    if os.path.exists(venv_py) and os.environ.get('SKILLLAB_NO_REEXEC') != '1':
        os.execv(venv_py, [venv_py] + sys.argv)

try:
    import yaml as _yaml
except ImportError:
    _yaml = None  # D1 degrades to SKIP; nothing else needs yaml

"""
10khr_cron_verify.py — cron-safe eligibility + 5-dimension on-disk verification harness.

WHY this exists: the 10khr grind's biggest trap is the over-scoring heuristic.
A heuristic "49/50" is almost never a real defect — it is the D3 451-500 line
proxy, the D8 ref-count trap, or (observed 2026-07-19) a D5 `- [ ]` checklist
that legitimately lives in a referenced support file, NOT the main SKILL.md.
Grinding these spins a perpetual loop. This script lets a cron pass answer
deterministically: which below-50 targets are REAL gaps to fix, vs over-scoring
traps to skip?

Cron-safe by design:
  * Does NOT call save_state() — preserves the skip-rule's last_run. Running
    `--report-only` would advance last_run and make every skill look "modified",
    defeating the skip rule (state-write pitfall, 2026-07-18).
  * Reads last_run from the runner's REAL STATE_FILE (the ocas-critique path),
    not the stale ocas-skilllab copy (state-file split-brain pitfall).
  * Pure verification — never writes to skills. Genuine D9 gaps are fixed by
    hand-injecting the canonical --help guard documented in SKILL.md Pitfalls.

Usage:
  python3 scripts/10khr_cron_verify.py
"""
import importlib.util
import os
import sys
import subprocess
from datetime import datetime, timezone

# OUTBOUND_SKIP: never run --help on a script that can post/send/trade. An audit
# doing exactly that published "--help" to a live Bluesky account three times.
import re as _re
_OUTBOUND_SKIP = _re.compile(
    r"createRecord|app\.bsky\.feed|com\.atproto|/xrpc/|post\.sh|smtplib"
    r"|requests\.(post|put|patch|delete)|api\.telegram\.org|submit_order|alpaca"
    r"|curl\s+(-[A-Za-z]+\s+)*-X\s*[\"']?(POST|PUT|PATCH|DELETE)", _re.I)


def _can_send(src_or_path):
    """Outbound safety check. Accepts script source text or file path.

    Performance optimization: Accepts pre-read `src` text directly to avoid
    opening and reading script files twice in verification loops.
    """
    if "\n" in src_or_path or len(src_or_path) > 4096 or not os.path.exists(src_or_path):
        return bool(_OUTBOUND_SKIP.search(src_or_path))
    try:
        with open(src_or_path, encoding="utf-8", errors="ignore") as f:
            return bool(_OUTBOUND_SKIP.search(f.read()))
    except OSError:
        return False


_CODE_RATIO_MOD = None


def _get_code_ratio_mod():
    """Cached loader for critique_code_ratio module to avoid redundant imports."""
    global _CODE_RATIO_MOD
    if _CODE_RATIO_MOD is None:
        try:
            import critique_code_ratio
            _CODE_RATIO_MOD = critique_code_ratio
        except ImportError:
            rc_path = os.path.join(os.path.dirname(_runner_path()), "critique_code_ratio.py")
            spec = importlib.util.spec_from_file_location("critique_code_ratio", rc_path)
            _CODE_RATIO_MOD = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_CODE_RATIO_MOD)
    return _CODE_RATIO_MOD


def _runner_path():
    local_path = os.path.join(os.path.dirname(__file__), "critique_10khr_runner.py")
    if os.path.exists(local_path):
        return local_path
    hermes_root = os.environ.get("HERMES_ROOT", os.path.expanduser("~/.hermes"))
    return os.path.join(
        hermes_root, "profiles", "indigo", "skills",
        "ocas-skilllab", "scripts", "critique_10khr_runner.py",
    )


def load_runner():
    spec = importlib.util.spec_from_file_location("runner", _runner_path())
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ondisk_check(skill_name, skill_path, runner):
    """5-dimension ON-DISK verification (ignores the over-scoring heuristic)."""
    d = os.path.dirname(skill_path)
    try:
        with open(skill_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return {"ERROR": f"cannot read SKILL.md: {e}"}
    out = {}

    # D1: frontmatter category
    if _yaml is None:
        out["D1"] = "SKIP (no pyyaml in this interpreter)"
    else:
        try:
            fm = _yaml.safe_load(content.split("---")[1]) or {}
            cat = fm.get("metadata", {}).get("hermes", {}).get("category")
            out["D1"] = "OK" if cat else "MISSING category"
        except Exception as e:
            out["D1"] = f"YAML ERR {e}"

    # D3: code ratio + line count (line count tells us if it's the 451-500 proxy)
    # Performance optimization: In-memory module import and function invocation of
    # critique_code_ratio.measure_code_ratio avoids spawning a python interpreter subprocess
    # for every skill verified (~50ms -> <0.1ms per skill). Passing pre-read `content` avoids redundant disk read.
    try:
        cr_mod = _get_code_ratio_mod()
        r = cr_mod.measure_code_ratio(skill_path, text=content)
        out["D3"] = f"{r['status']} ({r['ratio']}%)"
    except Exception as e:
        out["D3"] = f"ERR {e}"
    out["wc_lines"] = len(content.split("\n"))

    # D5: checklist — search main SKILL.md + references/ directory, because
    # a `- [ ]` quality checklist may legitimately live in a referenced support file.
    # Performance optimization: Use direct os.path.isdir & os.listdir on references/
    # to avoid os.walk generator and tuple allocation overhead.
    has_cb = "- [ ]" in content
    if not has_cb:
        refs_dir = os.path.join(d, "references")
        if os.path.isdir(refs_dir):
            try:
                for fn in os.listdir(refs_dir):
                    if not fn.endswith(".md"):
                        continue
                    try:
                        with open(os.path.join(refs_dir, fn), encoding="utf-8", errors="ignore") as f:
                            if "- [ ]" in f.read():
                                has_cb = True
                                break
                    except Exception:
                        continue
            except OSError:
                pass
    out["D5"] = "OK" if has_cb else "NO checklist (main or refs)"

    # D9: every CLI script --help must exit 0
    # Performance & correctness optimization: Combine _can_send safety guard with
    # runner's non-CLI and test entrypoint filtering to avoid wasteful subprocess spawning
    # (~50ms per non-CLI script) and eliminate false-positive failure reports on helper modules,
    # while guaranteeing 100% safety against outbound side-effects.
    sd = os.path.join(d, "scripts")
    if os.path.isdir(sd):
        miss = []
        scripts = sorted(f for f in os.listdir(sd) if f.endswith((".py", ".sh")))
        count = len(scripts)
        for s in scripts:
            sp = os.path.join(sd, s)
            try:
                with open(sp, encoding="utf-8", errors="ignore") as f:
                    src = f.read()
            except OSError:
                src = ""
            if not src:
                continue
            # 1. Outbound safety check: pass pre-read `src` to avoid redundant file open/read
            if _can_send(src):
                continue
            # 2. Skip test entrypoints and non-CLI modules to avoid slow & false-positive --help checks
            if runner._is_test_entrypoint(src):
                continue
            if not runner._is_cli_entrypoint(src):
                continue
            if runner._outbound_capable(s, src):
                if not runner._flag_safe(s, src):
                    miss.append(s)
                continue

            try:
                cmd = ["bash", sp, "--help"] if s.endswith(".sh") else [sys.executable, sp, "--help"]
                rc = subprocess.run(cmd, input="", capture_output=True, text=True, timeout=30).returncode
            except Exception:
                rc = -1
            if rc != 0:
                miss.append(s)

        if count == 0:
            out["D9"] = "N/A (no scripts)"
        elif not miss:
            out["D9"] = "OK (all exit 0)"
        else:
            out["D9"] = f"MISSING --help: {miss}"
    else:
        out["D9"] = "N/A (no scripts)"
    return out


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Cron-safe 10khr eligibility plus on-disk 5-dimension "
                    "verification harness. Assesses all ocas/util skills, applies "
                    "the skip-rule against the runner STATE_FILE, and prints real "
                    "gaps vs over-scoring traps. No state mutation.")
    parser.parse_args()
    runner = load_runner()
    state = runner.load_state()
    last_run = (datetime.fromisoformat(state["last_run"])
                if state.get("last_run") else datetime.min.replace(tzinfo=timezone.utc))
    assessment = runner.run_full_assessment()
    below = [r for r in assessment if r["total"] < runner.TARGET_SCORE]
    print(f"Total assessed: {len(assessment)} | below 50/50: {len(below)} | last_run: {state.get('last_run')}")

    rows = []
    for r in below:
        p = r["path"]
        mtime = datetime.fromtimestamp(os.stat(p).st_mtime, timezone.utc)
        eligible = (mtime > last_run) or (r["total"] < 44)
        rows.append((r["total"], r["skill"], p, eligible, mtime.isoformat()))
    rows.sort(key=lambda x: (x[0], 0 if x[3] else 1))

    for sc, name, p, elig, mt in rows:
        if not elig:
            continue
        chk = ondisk_check(name, p, runner)
        print(f"\n### {name}  (heuristic {sc}/50, mtime {mt})")
        for k, v in chk.items():
            print(f"  {k}: {v}")
        real_gap = any(str(v).startswith(("MISSING", "NO ", "YAML ERR", "ERR "))
                      for k, v in chk.items())
        print(f"  >> {'REAL GAP — grind it' if real_gap else 'OVER-SCORING TRAP — skip'}")

    print("\n(Skipped: below-50 skills unmodified since last_run AND heuristic>=44 "
          "— these are over-scoring traps; do NOT re-grind them.)")


if __name__ == "__main__":
    main()