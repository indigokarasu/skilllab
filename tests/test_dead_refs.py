"""Regression test for the dead-reference false positive.

Two cases must hold:
  1. A fully qualified existing path written as
     ~/.hermes/.../commons/email-templates/job_search.py is NOT dead, even
     though the capture regex truncates it to templates/job_search.py.
  2. A genuinely dead references/foo.md IS still reported. The fix must not
     make the check so permissive that it stops catching anything.
"""
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, "/root/.hermes/profiles/indigo/skills/ocas-skilllab/scripts")

from critique_10khr_runner import check_dead_references


def test_existing_qualified_path_not_dead():
    d = tempfile.mkdtemp()
    text = (
        "The job_search template at\n"
        "~/.hermes/profiles/indigo/commons/email-templates/job_search.py "
        "handles rendering.\n"
        "All emails go via\n"
        "~/.hermes/profiles/indigo/commons/email-templates/send_email.py\n"
    )
    dead = check_dead_references(d, text=text)
    assert dead == [], "existing qualified paths wrongly reported dead: %r" % dead


def test_genuinely_dead_ref_still_caught():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "references"))
    io.open(os.path.join(d, "references", "real.md"), "w").close()
    text = (
        "Read `references/real.md` for the schema.\n"
        "Read `references/never-written.md` for the checklist.\n"
    )
    dead = check_dead_references(d, text=text)
    assert dead == ["references/never-written.md"], (
        "genuine dead ref not caught; got %r" % dead
    )


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS %s" % name)
            except AssertionError as e:
                print("FAIL %s: %s" % (name, e))
                failures += 1
    sys.exit(1 if failures else 0)
