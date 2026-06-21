#!/usr/bin/env python3
"""skill lab — interactive keyboard-navigable skill library management"""

import curses
import os
import sys
import yaml

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")
ARCHIVE_DIR = os.path.expanduser("~/.hermes/skills/.archive")

MENU_ITEMS = [
    ("audit",      "Audit skill library — find orphans, author gaps, frontmatter issues"),
    ("merge",      "Merge/consolidate — combine overlapping skills"),
    ("rename",     "Rename — move skill directory, update references"),
    ("delete",     "Delete — archive a skill"),
    ("publish",    "Publish — push skill to GitHub for agentskills.io"),
    ("sanitize",   "Sanitize — extract inline credentials to reference files"),
    ("hygiene",    "Hygiene check — grep false-positives, broken frontmatter"),
    ("quit",       "Exit skill lab"),
]


# ─── Shared curses helpers ──────────────────────────────────────────────────

def init_colors():
    """Initialize color pairs once for the session."""
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)     # title
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)     # normal
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)      # selected
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # key hint
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)     # success
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)       # warning


def scroll_navigate(key, row, scroll, visible, total_items):
    """Handle arrow keys for scroll navigation. Returns (row, scroll)."""
    if key == curses.KEY_UP:
        row = max(0, row - 1)
        if row < scroll:
            scroll = row
    elif key == curses.KEY_DOWN:
        row = min(total_items - 1, row + 1)
        if row >= scroll + visible:
            scroll = row - visible + 1
    return row, scroll


def draw_title_row(stdscr, title, hint=""):
    """Draw a title row with optional right-aligned hint."""
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, title, curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(0, len(title), "─" * max(0, w - len(title)), curses.color_pair(1))
    if hint:
        stdscr.addstr(0, max(0, w - len(hint)), hint, curses.color_pair(4))


def draw_scroll_indicators(stdscr, row, scroll, visible, total_items):
    """Draw scroll indicators if there are more items than visible."""
    h, w = stdscr.getmaxyx()
    if scroll > 0:
        stdscr.addstr(5, w - 3, "▲", curses.color_pair(4))
    if scroll + visible < total_items:
        stdscr.addstr(5 + visible - 1, w - 3, "▼", curses.color_pair(4))


# ─── Core logic ──────────────────────────────────────────────────────────────

def scan_skills():
    """Return list of (name, path, has_author, has_license, has_triggers, is_archive)"""
    results = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        if entry.startswith(".") or entry == "__pycache__":
            continue
        skill_md = os.path.join(SKILLS_DIR, entry, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        info = parse_frontmatter(skill_md)
        results.append((entry, skill_md, info, False))
    for entry in sorted(os.listdir(ARCHIVE_DIR)):
        skill_md = os.path.join(ARCHIVE_DIR, entry, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        info = parse_frontmatter(skill_md)
        results.append((entry, skill_md, info, True))
    return results


def parse_frontmatter(path):
    """Parse YAML frontmatter from SKILL.md"""
    info = {"name": "", "description": "", "author": "", "license": "", "triggers": []}
    try:
        with open(path) as f:
            content = f.read()
        if not content.startswith("---"):
            return info
        parts = content.split("---", 2)
        if len(parts) < 3:
            return info
        fm = yaml.safe_load(parts[1])
        if not fm:
            return info
        info["name"] = str(fm.get("name", ""))
        info["description"] = str(fm.get("description", ""))[:80]
        meta = fm.get("metadata") or {}
        info["author"] = str(meta.get("author", fm.get("author", "")))
        info["license"] = str(fm.get("license", ""))
        triggers = fm.get("triggers") or []
        info["triggers"] = [str(t) for t in triggers] if isinstance(triggers, list) else []
    except Exception:
        pass
    return info


# ─── TUI screens ─────────────────────────────────────────────────────────────

def draw_menu(stdscr):
    """Main menu screen. Returns selected action string or None."""
    curses.curs_set(0)
    init_colors()

    row = 0
    scroll = 0
    message = ""
    message_color = 5

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        draw_title_row(stdscr, " ocas-skilllab ", " ↑↓: navigate  ⏎: select  q: quit ")

        stdscr.addstr(2, 2, "skill library management", curses.color_pair(2))
        stdscr.addstr(3, 2, "use arrow keys to navigate, enter to select", curses.color_pair(4))

        visible = min(len(MENU_ITEMS), h - 8)
        for i in range(visible):
            idx = scroll + i
            if idx >= len(MENU_ITEMS):
                break
            label, desc = MENU_ITEMS[idx]
            y = 5 + i
            if idx == row:
                sel = f" ▸ {label:<12} {desc}"
                stdscr.addstr(y, 0, sel[:w-1], curses.color_pair(3) | curses.A_BOLD)
            else:
                sel = f"   {label:<12} {desc}"
                stdscr.addstr(y, 0, sel[:w-1], curses.color_pair(2))

        if message:
            stdscr.addstr(h-2, 2, message[:w-4], curses.color_pair(message_color))

        draw_scroll_indicators(stdscr, row, scroll, visible, len(MENU_ITEMS))

        stdscr.refresh()

        key = stdscr.getch()
        row, scroll = scroll_navigate(key, row, scroll, visible, len(MENU_ITEMS))

        if key == ord('q') or key == 27:
            return None
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            return MENU_ITEMS[row][0]


def draw_skill_list(stdscr, skills, title, filter_fn=None):
    """Browse skill list, return selected skill name or None."""
    curses.curs_set(0)

    row = 0
    scroll = 0

    filtered = [(n, p, i, a) for n, p, i, a in skills if filter_fn is None or filter_fn(n, p, i, a)]

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        t = f" {title} ({len(filtered)} skills) "
        draw_title_row(stdscr, t, " ↑↓: navigate  ⏎: inspect  b: back ")

        visible = min(len(filtered), h - 6)
        for i in range(visible):
            idx = scroll + i
            if idx >= len(filtered):
                break
            name, path, info, is_archive = filtered[idx]
            y = 2 + i

            author_flag = "✓" if info["author"] else "✗"
            lic_flag = "✓" if info["license"] else "✗"
            arch_tag = " [ARCHIVE]" if is_archive else ""

            flags = f"  a:{author_flag} l:{lic_flag}{arch_tag}"
            line = f"  {name}{flags}"

            if idx == row:
                stdscr.addstr(y, 0, line[:w-1], curses.color_pair(3) | curses.A_BOLD)
                if y + 1 < h - 1 and info["description"]:
                    desc = f"    {info['description'][:w-6]}"
                    stdscr.addstr(y + 1, 0, desc, curses.color_pair(4))
            else:
                color = curses.color_pair(6) if not info["author"] and not is_archive else curses.color_pair(2)
                stdscr.addstr(y, 0, line[:w-1], color)

        stdscr.refresh()

        key = stdscr.getch()
        row, scroll = scroll_navigate(key, row, scroll, visible, len(filtered))

        if key == ord('q') or key == 27 or key == ord('b'):
            return None
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            return filtered[row][0] if filtered else None


def inspect_skill(stdscr, name, path, info):
    """Show skill details"""
    curses.curs_set(0)

    lines = [
        f"Name:        {info['name'] or name}",
        f"Path:        {path}",
        f"Author:      {info['author'] or '(missing)'}",
        f"License:     {info['license'] or '(missing)'}",
        f"Triggers:    {', '.join(info['triggers']) or '(missing)'}",
        f"Description: {info['description']}",
    ]

    scroll = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        draw_title_row(stdscr, f" {name} ", " q: back ")

        visible = min(len(lines), h - 2)
        for i in range(visible):
            idx = scroll + i
            if idx >= len(lines):
                break
            stdscr.addstr(2 + i, 2, lines[idx][:w-4], curses.color_pair(1))

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q') or key == 27 or key == ord('b'):
            return
        elif key == curses.KEY_UP:
            scroll = max(0, scroll - 1)
        elif key == curses.KEY_DOWN:
            scroll += 1


def confirm(stdscr, prompt):
    """Yes/no confirmation dialog."""
    curses.curs_set(0)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 1, 2, prompt, curses.COLOR_WHITE)
    stdscr.addstr(h//2 + 1, 2, "  y / n ", curses.COLOR_YELLOW)
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == ord('y'):
            return True
        elif key == ord('n') or key == ord('q') or key == 27:
            return False


# ─── Actions ─────────────────────────────────────────────────────────────────

def run_action(action, stdscr):
    """Execute selected action"""
    skills = scan_skills()

    if action == "quit":
        return False

    if action == "audit":
        draw_skill_list(stdscr, skills, "Audit — skills missing author",
            lambda n, p, i, a: not i["author"] and not a)

    elif action == "hygiene":
        selected = draw_skill_list(stdscr, skills, "Hygiene — all skills",
            lambda n, p, i, a: True)
        if selected:
            for name, path, info, is_arch in skills:
                if name == selected:
                    inspect_skill(stdscr, name, path, info)

    elif action == "merge":
        selected = draw_skill_list(stdscr, skills, "Merge — select source skill",
            lambda n, p, i, a: not a)
        if selected:
            if confirm(stdscr, f"Select target for {selected}"):
                curses.endwin()
                print(f"\nUse: skill_manage to merge {selected} into target")
                print("Then archive the source directory.")

    elif action == "rename":
        selected = draw_skill_list(stdscr, skills, "Rename — select skill", lambda n, p, i, a: not a)
        if selected:
            curses.endwin()
            new_name = input(f"New name for {selected}: ").strip()
            if new_name:
                src = os.path.join(SKILLS_DIR, selected)
                dst = os.path.join(SKILLS_DIR, new_name)
                if os.path.isdir(dst):
                    print(f"  ERROR: {new_name} already exists")
                else:
                    os.rename(src, dst)
                    print(f"  Renamed {selected} -> {new_name}")
                    print(f"  Update SKILL.md name: and heading manually")
            curses.initscr()

    elif action == "delete":
        selected = draw_skill_list(stdscr, skills, "Delete — select skill to archive",
            lambda n, p, i, a: not a)
        if selected and not selected.startswith("."):
            if confirm(stdscr, f"Archive {selected}?"):
                src = os.path.join(SKILLS_DIR, selected)
                dst = os.path.join(ARCHIVE_DIR, selected)
                os.makedirs(ARCHIVE_DIR, exist_ok=True)
                os.rename(src, dst)
                curses.endwin()
                print(f"  Archived {selected}")
                print(f"  Update all references to {selected}")
                curses.initscr()

    elif action == "publish":
        selected = draw_skill_list(stdscr, skills, "Publish — select skill",
            lambda n, p, i, a: not a and i["author"])
        if selected:
            curses.endwin()
            print(f"\nPublishing {selected}:")
            print(f"  Use skill-publish reference files in ocas-skilllab/references/")
            print(f"  1. Audit spec compliance")
            print(f"  2. Sanitize private data")
            print(f"  3. gh repo create indigokarasu/{selected} --private --description '...'")
            print(f"  4. Clone, copy, commit, push")
            input("\n  Press Enter to continue...")
            curses.initscr()

    elif action == "sanitize":
        selected = draw_skill_list(stdscr, skills, "Sanitize — select skill",
            lambda n, p, i, a: not a)
        if selected:
            curses.endwin()
            print(f"\nSanitizing {selected}:")
            print(f"  Scan for: _KEY, _SECRET, TOKEN, OAuth fields, absolute paths")
            print(f"  Create references/<purpose>.md with credential details")
            print(f"  Replace inline with: See references/<file>.md for <description>.")
            input("\n  Press Enter to continue...")
            curses.initscr()

    return True


def main():
    if not os.path.isdir(SKILLS_DIR):
        print(f"ERROR: skills directory not found: {SKILLS_DIR}")
        sys.exit(1)

    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    def run(stdscr):
        running = True
        while running:
            action = draw_menu(stdscr)
            if action is None or action == "quit":
                break
            running = run_action(action, stdscr)

    curses.wrapper(run)


if __name__ == "__main__":
    main()
