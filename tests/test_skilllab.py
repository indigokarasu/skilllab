"""Unit tests for ocas-skilllab scripts (run: python3 -m unittest discover -s tests)."""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL_DIR, "scripts")
sys.path.insert(0, SCRIPTS)

import critique_code_ratio  # noqa: E402


class TestCodeRatio(unittest.TestCase):
    def test_empty_file_passes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# nothing\n")
            path = f.name
        try:
            r = critique_code_ratio.measure_code_ratio(path)
            self.assertLess(r["ratio"], 20)
        finally:
            os.unlink(path)

    def test_all_code_fails(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            for _ in range(30):
                f.write("```\nx = 1\n```\n")
            path = f.name
        try:
            r = critique_code_ratio.measure_code_ratio(path)
            self.assertGreaterEqual(r["ratio"], 30)
        finally:
            os.unlink(path)


class TestRunnerHeuristics(unittest.TestCase):
    def test_score_skill_missing_file(self):
        import critique_10khr_runner as runner
        res = runner.score_skill("nope", "/nonexistent/SKILL.md")
        self.assertEqual(res["total"], 0)

    def test_state_roundtrip_no_mutation(self):
        # load_state must not create or write the canonical state file
        import critique_10khr_runner as runner
        if os.path.exists(runner.STATE_FILE):
            before = open(runner.STATE_FILE).read()
            runner.load_state()
            self.assertEqual(open(runner.STATE_FILE).read(), before)


class TestScriptHelp(unittest.TestCase):
    """D9: every bundled script answers --help with exit 0."""

    def test_python_scripts_help(self):
        broken = []
        for name in sorted(os.listdir(SCRIPTS)):
            if not name.endswith(".py"):
                continue
            p = subprocess.run([sys.executable, os.path.join(SCRIPTS, name), "--help"],
                               capture_output=True, timeout=60)
            if p.returncode != 0:
                broken.append(name)
        self.assertEqual(broken, [])

    def test_bash_scripts_help(self):
        broken = []
        for name in sorted(os.listdir(SCRIPTS)):
            if not name.endswith(".sh"):
                continue
            p = subprocess.run(["bash", os.path.join(SCRIPTS, name), "--help"],
                               capture_output=True, timeout=60)
            if p.returncode != 0:
                broken.append(name)
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
