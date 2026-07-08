#!/usr/bin/env bash
# Secret-scan gate for a single skill (or plugin) directory.
# Scans: working tree, .git/config, and ENTIRE git history (all revisions).
# Output is masked — full secrets are never printed.
# Exits 0 if CLEAN, 1 if any potential secret is found (use to gate commit/publish).
set -u
TARGET="${1:-.}"
if [ ! -d "$TARGET/.git" ]; then echo "No .git in $TARGET — nothing to scan"; exit 2; fi
RE='AKIA[0-9A-Z]{16}|gh[pousr]_[0-9A-Za-z]{36}|github_pat_[0-9A-Za-z_]{20,}|xox[baprs]-[0-9A-Za-z-]{10,}|sk-[0-9A-Za-z]{20,}|AIza[0-9A-Za-z_-]{35}|sk_live_[0-9A-Za-z]+|pk_live_[0-9A-Za-z]+|SK[0-9a-fA-F]{32}|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.|BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY|ssh-rsa AAAAB3NzaC1|://[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]{4,}@[A-Za-z0-9.-]+'
mask() { sed -E 's/([A-Za-z0-9_]{6})[A-Za-z0-9_-]{10,}([A-Za-z0-9_]{4})/\1***\2/g'; }
found=0
echo "=== Secret scan: $TARGET ==="
wt=$(grep -rInP --exclude-dir=.git --exclude=secret-scan.sh "$RE" "$TARGET" 2>/dev/null | mask)
[ -n "$wt" ] && { echo "--- WORKING TREE ---"; echo "$wt"; found=1; }
cfg=$(grep -P "$RE" "$TARGET/.git/config" 2>/dev/null | mask)
[ -n "$cfg" ] && { echo "--- .git/config ---"; echo "$cfg"; found=1; }
revs=$(git -C "$TARGET" rev-list --all 2>/dev/null)
if [ -n "$revs" ]; then
  hist=$(timeout 120 git -C "$TARGET" grep -I -n -P "$RE" $revs -- ':(exclude)scripts/secret-scan.sh' 2>/dev/null | mask)
  [ -n "$hist" ] && { echo "--- HISTORY ---"; echo "$hist"; found=1; }
fi
if [ "$found" -eq 0 ]; then echo "CLEAN: no secrets detected."; exit 0; fi
echo "SECRETS DETECTED — do NOT commit/publish until remediated."; exit 1
