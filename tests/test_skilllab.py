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

import importlib.util
import _quick_rank  # noqa: E402
import critique_10khr_runner as runner  # noqa: E402
import critique_code_ratio  # noqa: E402
import heuristic_score  # noqa: E402
import skilllab  # noqa: E402

spec_cron = importlib.util.spec_from_file_location("cron_verify", os.path.join(SCRIPTS, "10khr_cron_verify.py"))
cron_verify = importlib.util.module_from_spec(spec_cron)
spec_cron.loader.exec_module(cron_verify)


class TestSanitizeSkill(unittest.TestCase):
    def test_sanitize_secrets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "config.py")
            with open(test_file, "w") as f:
                f.write('OPENAI_KEY = "sk-1234567890123456789012345"\n')  # secret-allow
                f.write('STRIPE_KEY = "sk_live_1234567890abcdef"\n')  # secret-allow
                f.write('AWS_KEY = "AKIA1234567890ABCDEF"\n')  # secret-allow

            summary = skilllab.sanitize_skill("test-skill", tmpdir)
            self.assertIn("config.py", summary)

            with open(test_file) as f:
                content = f.read()
            self.assertIn("${OPENAI_API_KEY}", content)
            self.assertIn("${STRIPE_LIVE_SECRET_KEY}", content)
            self.assertIn("${AWS_ACCESS_KEY_ID}", content)
            self.assertNotIn("sk-1234567890", content)

    def test_sanitize_non_secret_bypass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "helper.py")
            normal_code = "def add(a, b):\n    return a + b\n"
            with open(test_file, "w") as f:
                f.write(normal_code)

            summary = skilllab.sanitize_skill("test-skill", tmpdir)
            self.assertEqual(summary, {})

            with open(test_file) as f:
                content = f.read()
            self.assertEqual(content, normal_code)

    def test_sanitize_multi_files_and_empty_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test empty subfolder does not cause UnboundLocalError
            subdir = os.path.join(tmpdir, "empty_subdir")
            os.makedirs(subdir)

            # Test multiple files: non-last file has secret, last file is clean
            f1 = os.path.join(tmpdir, "a_config.py")
            f2 = os.path.join(tmpdir, "b_normal.py")
            with open(f1, "w") as f:
                f.write('OPENAI_KEY = "sk-1234567890123456789012345"\n')  # secret-allow
            with open(f2, "w") as f:
                f.write('x = 100\n')

            summary = skilllab.sanitize_skill("test-skill", tmpdir)
            self.assertIn("a_config.py", summary)

            with open(f1) as f:
                content = f.read()
            self.assertIn("${OPENAI_API_KEY}", content)

    def test_sanitize_taglines_and_tool_refs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            readme = os.path.join(tmpdir, "README.md")
            skill_md = os.path.join(tmpdir, "SKILL.md")
            with open(readme, "w") as f:
                f.write("# Skill\nTell it what you need. It does the work.\nPowered by Elephas.")
            with open(skill_md, "w") as f:
                f.write("# Skill MD\nOne clear job, done well.\n")

            summary = skilllab.sanitize_skill("test-skill", tmpdir)
            self.assertIn("README.md", summary)
            self.assertIn("SKILL.md", summary)

            with open(readme) as f:
                readme_content = f.read()
            self.assertNotIn("Tell it what you need.", readme_content)
            self.assertIn("Operational skill for the OCAS family.", readme_content)
            self.assertIn("See references/integration-notes.md", readme_content)

            with open(skill_md) as f:
                skill_content = f.read()
            self.assertNotIn("One clear job, done well.", skill_content)

    def test_sanitize_session_log_quarantine(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_file = os.path.join(tmpdir, "session-2026-01-01.md")
            with open(session_file, "w") as f:
                f.write("# Session Log\nDetails here.\n")

            summary = skilllab.sanitize_skill("test-skill", tmpdir)
            self.assertIn("session-2026-01-01.md", summary)
            self.assertFalse(os.path.exists(session_file))
            quarantined = os.path.join(tmpdir, ".archive", "session-logs-export", "session-2026-01-01.md")
            self.assertTrue(os.path.exists(quarantined))


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


class TestHeuristicScore(unittest.TestCase):
    def test_check_frontmatter_parses_with_and_without_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = os.path.join(tmpdir, "SKILL.md")
            content = "---\nname: test\ndescription: A test skill\n---\n# Body"
            with open(skill_md, "w") as f:
                f.write(content)

            # Test passing pre-read text (optimized fast path)
            self.assertTrue(heuristic_score.check_frontmatter_parses(tmpdir, text=content))
            # Test default disk-read path (text=None)
            self.assertTrue(heuristic_score.check_frontmatter_parses(tmpdir))

    def test_check_dead_references_with_and_without_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = os.path.join(tmpdir, "SKILL.md")
            content = "Check [doc](references/missing.md) and [ok](references/existing.md)"
            with open(skill_md, "w") as f:
                f.write(content)

            refs_dir = os.path.join(tmpdir, "references")
            os.makedirs(refs_dir)
            with open(os.path.join(refs_dir, "existing.md"), "w") as f:
                f.write("existing")

            # Test passing pre-read text (optimized fast path)
            dead_fast = heuristic_score.check_dead_references(tmpdir, text=content)
            self.assertEqual(dead_fast, ["references/missing.md"])

            # Test default disk-read path (text=None)
            dead_disk = heuristic_score.check_dead_references(tmpdir)
            self.assertEqual(dead_disk, ["references/missing.md"])

    def test_score_skill_uses_pre_read_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = os.path.join(tmpdir, "SKILL.md")
            content = "---\nname: test-skill\ndescription: A test skill\nlicense: MIT\n---\n# Test\n"
            with open(skill_md, "w") as f:
                f.write(content)

            res = heuristic_score.score_skill("test-skill", skill_md)
            self.assertEqual(res["skill"], "test-skill")
            self.assertIn("D1", res["dims"])


class TestRunnerHeuristics(unittest.TestCase):
    def test_score_skill_missing_file(self):
        import critique_10khr_runner as runner
        res = runner.score_skill("nope", "/nonexistent/SKILL.md")
        self.assertEqual(res["total"], 0)

    def test_state_roundtrip_no_mutation(self):
        # load_state must not create or write the canonical state file
        import critique_10khr_runner as runner
        if os.path.exists(runner.STATE_FILE):
            with open(runner.STATE_FILE) as f:
                before = f.read()
            runner.load_state()
            with open(runner.STATE_FILE) as f:
                after = f.read()
            self.assertEqual(after, before)

    def test_check_correctness_destructive_case_insensitive(self):
        import critique_10khr_runner as runner
        for stmt in ("Drop Table users;", "dROp tABle users;", "DROP TABLE users;"):
            with tempfile.TemporaryDirectory() as tmpdir:
                scripts_dir = os.path.join(tmpdir, "scripts")
                os.makedirs(scripts_dir)
                with open(os.path.join(scripts_dir, "bad.py"), "w") as f:
                    f.write(f'cur.execute("{stmt}")\n')

                score, findings = runner.check_correctness(tmpdir)
                has_drop = any("DROP TABLE" in f for f in findings)
                self.assertTrue(has_drop, f"Failed to catch destructive statement: {stmt!r} (findings: {findings})")

    def test_ref_resolves_and_sibling_cache(self):
        import critique_10khr_runner as runner
        with tempfile.TemporaryDirectory() as tmpdir:
            s1 = os.path.join(tmpdir, "ocas-one")
            s2 = os.path.join(tmpdir, "ocas-two")
            os.makedirs(os.path.join(s1, "references"))
            os.makedirs(os.path.join(s2, "references"))

            with open(os.path.join(s1, "references", "doc1.md"), "w") as f:
                f.write("doc1")
            with open(os.path.join(s2, "references", "doc2.md"), "w") as f:
                f.write("doc2")

            # Local reference resolves
            self.assertTrue(runner._ref_resolves(s1, "references/doc1.md"))
            # Sibling reference resolves via cached sibling basenames
            self.assertTrue(runner._ref_resolves(s1, "references/doc2.md"))
            # Missing reference returns False
            self.assertFalse(runner._ref_resolves(s1, "references/nonexistent.md"))


class TestSkillDirectoryPruning(unittest.TestCase):
    """Verify that skill discovery functions prune subdirectories upon finding SKILL.md."""

    def test_find_all_skills_prunes_subdirectories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            s1 = os.path.join(tmpdir, "ocas-alpha")
            s2 = os.path.join(tmpdir, "util-beta")
            os.makedirs(os.path.join(s1, "references", "subfolder"))
            os.makedirs(os.path.join(s1, "scripts"))
            os.makedirs(os.path.join(s2, "assets"))

            with open(os.path.join(s1, "SKILL.md"), "w") as f:
                f.write("---\nname: ocas-alpha\ndescription: Alpha skill\n---\n")
            with open(os.path.join(s1, "references", "subfolder", "doc.md"), "w") as f:
                f.write("doc")
            with open(os.path.join(s2, "SKILL.md"), "w") as f:
                f.write("---\nname: util-beta\ndescription: Beta skill\n---\n")

            # Test runner's find_all_skills
            skills = runner.find_all_skills(skills_dir=tmpdir)
            skill_names = [name for name, _ in skills]
            self.assertIn("ocas-alpha", skill_names)
            self.assertIn("util-beta", skill_names)
            self.assertEqual(len(skills), 2)

            # Test quick_rank's find_skills
            orig_skills_dir = _quick_rank.SKILLS_DIR
            try:
                _quick_rank.SKILLS_DIR = tmpdir
                found = _quick_rank.find_skills()
                self.assertEqual(len(found), 2)
            finally:
                _quick_rank.SKILLS_DIR = orig_skills_dir

            # Test heuristic_score's find_all_skills
            orig_hs_dir = heuristic_score.SKILLS_DIR
            try:
                heuristic_score.SKILLS_DIR = tmpdir
                found_hs = heuristic_score.find_all_skills()
                hs_names = [name for name, _ in found_hs]
                self.assertIn("ocas-alpha", hs_names)
                self.assertIn("util-beta", hs_names)
            finally:
                heuristic_score.SKILLS_DIR = orig_hs_dir


class TestCronVerify(unittest.TestCase):
    """Unit tests for 10khr_cron_verify.py."""

    def test_import_survives_missing_pyyaml(self):
        """Regression: a module-scope `import yaml` raised ModuleNotFoundError on
        CI (no venv to re-exec into), which failed the whole test module at import
        time before a single assertion ran. Re-import the module with yaml blocked
        and assert it loads, and that D1 degrades instead of exploding."""
        import importlib.util as _ilu

        class _YamlBlocker:
            """A meta_path finder that makes `import yaml` fail the way a runner
            without pyyaml does. Returning None is NOT enough — the import
            system would fall through to the next finder and succeed anyway."""

            def find_spec(self, name, path=None, target=None):
                if name == "yaml" or name.startswith("yaml."):
                    raise ModuleNotFoundError(f"No module named {name!r}", name=name)
                return None  # defer to every other finder

        blocker = _YamlBlocker()
        spec = _ilu.spec_from_file_location(
            "cron_verify_noyaml", os.path.join(SCRIPTS, "10khr_cron_verify.py"))
        mod = _ilu.module_from_spec(spec)
        saved = {k: v for k, v in sys.modules.items() if k == "yaml" or k.startswith("yaml.")}
        for k in saved:
            del sys.modules[k]
        sys.meta_path.insert(0, blocker)
        try:
            env_no_reexec = os.environ.get("SKILLLAB_NO_REEXEC")
            os.environ["SKILLLAB_NO_REEXEC"] = "1"  # never exec a host venv
            try:
                spec.loader.exec_module(mod)  # the failure was HERE
            finally:
                if env_no_reexec is None:
                    os.environ.pop("SKILLLAB_NO_REEXEC", None)
                else:
                    os.environ["SKILLLAB_NO_REEXEC"] = env_no_reexec
        finally:
            sys.meta_path.remove(blocker)
            sys.modules.update(saved)

        self.assertIsNone(mod._yaml)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = os.path.join(tmpdir, "SKILL.md")
            with open(skill_md, "w") as f:
                f.write("---\nname: t\ndescription: d\n---\n# T\n- [ ] c\n")
            chk = mod.ondisk_check("t", skill_md, runner)
            self.assertIn("SKIP", chk["D1"])
            # D3/D5 must still be real assertions, not silently skipped.
            self.assertTrue(chk.get("D3", "").startswith("pass"))
            self.assertEqual(chk.get("D5"), "OK")

    def test_ondisk_check(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = os.path.join(tmpdir, "SKILL.md")
            content = (
                "---\n"
                "name: test-skill\n"
                "description: A test skill\n"
                "metadata:\n"
                "  hermes:\n"
                "    category: software-development\n"
                "---\n"
                "# Test Skill\n"
                "- [ ] Checklist item 1\n"
            )
            with open(skill_md, "w") as f:
                f.write(content)

            chk = cron_verify.ondisk_check("test-skill", skill_md, runner)
            # "SKIP" is the third legitimate outcome: the module must import on an
            # interpreter with no pyyaml (CI, sandbox), degrading D1 instead of
            # raising. With pyyaml present D1 is a real OK/YAML ERR assertion.
            self.assertTrue(
                chk.get("D1") == "OK"
                or "YAML ERR" in chk.get("D1", "")
                or "SKIP" in chk.get("D1", "")
            )
            self.assertTrue(chk.get("D3", "").startswith("pass"))
            self.assertEqual(chk.get("D5"), "OK")
            self.assertIn("wc_lines", chk)


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
