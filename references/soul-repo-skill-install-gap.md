# SOUL Repo Skill Install Gap

_Skills written to `/root/soul/skills/` are invisible to the agent unless also installed in the active profile skills directory._

## Problem

The SOUL repo (`/root/soul/` or `/indigokarasu/SOUL/`) has a `skills/` directory where new skills are authored. But the agent only scans `~/.hermes/profiles/indigo/skills/` for active skills. A skill that exists in `/root/soul/skills/<name>/` will never appear in `skills_list` or `skill_view` until it's copied to the active profile.

This is distinct from the "orphan skills" pattern (skills in the active directory that are unused). This is an **install gap** — the skill is fully authored but never deployed.

## How It Manifests

- User says "run X skill" → agent says "skill not found" → user says "but we wrote it"
- Agent searches only `~/.hermes/profiles/indigo/skills/` and misses the `/root/soul/skills/` copy
- The skill was written in a previous session (often during a long skill-writing session) but never installed

## Detection

During audit, check BOTH locations:
```bash
# Active profile skills
ls ~/.hermes/profiles/indigo/skills/
# SOUL repo skills
ls /root/soul/skills/
```

Any skill directory in `/root/soul/skills/` that is NOT in `~/.hermes/profiles/indigo/skills/` is an install gap.

## Fix

Copy the skill to the active profile:
```bash
cp -r /root/soul/skills/<name> ~/.hermes/profiles/indigo/skills/<name>
```

Then verify it appears in `skills_list`.

## Prevention

When writing a new skill to the SOUL repo, ALWAYS also install it to the active profile skills directory in the same session. Don't assume "we'll install it later."

## Real Case

`ocas-actualization` was written to `/root/soul/skills/ocas-actualization/` on June 14. It was never installed in the active profile. For 4 days, any attempt to invoke it returned "skill not found." It was only discovered when Jared asked about it and I searched the SOUL repo directory directly.
