#!/usr/bin/env bash
# Sanitize gate for a single skill (or plugin) directory.
# Companion to secret-scan.sh: that one looks for CREDENTIALS, this one looks for
# IDENTITY and HOST leaks — real names, personal email, absolute paths that expose
# the operator's machine layout, and bare host/IP addresses.
#
# This script lives in a PUBLIC repo, so it must not contain the very strings it
# hunts for. Operator-specific terms are read from a terms file kept OUTSIDE the
# repo (default: $HOME/.hermes/.sanitize-terms, one extended-regex per line,
# '#' comments allowed). Generic checks still run when that file is absent.
#
# Exits 0 if CLEAN, 1 if a potential leak is found, 2 if no .git present.
set -u

MODE="full"
case "${1:-}" in
  --help|-h)
    echo "Usage: sanitize-skill-push-gate.sh [--working-tree] <dir>"
    echo "Scans <dir> for identity/host leaks. Default: working tree + full git history."
    echo "  --working-tree : scan the working tree only — use to gate sync/publish of NEW changes."
    echo "Operator terms: \${SANITIZE_TERMS_FILE:-\$HOME/.hermes/.sanitize-terms}"
    echo "Exits 0 if CLEAN, 1 if a leak is found, 2 if no .git present."
    exit 0 ;;
  --working-tree) MODE="wt"; TARGET="${2:-.}";;
  *) MODE="full"; TARGET="${1:-.}";;
esac

[ -d "$TARGET/.git" ] || { echo "No .git in $TARGET — nothing to scan"; exit 2; }

SELF="$(basename "$0")"
TERMS_FILE="${SANITIZE_TERMS_FILE:-$HOME/.hermes/.sanitize-terms}"

# Absolute paths that reveal the host's layout, and bare host identifiers.
# Deliberately NOT matching /usr, /etc, /opt, /var — those are generic and appear
# in legitimate documentation.
PATH_RE='/root/[A-Za-z0-9._-]|/home/[a-z][A-Za-z0-9._-]+|/Users/[a-z][A-Za-z0-9._-]+'
HOST_RE='\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
EMAIL_RE='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

# Addresses and hosts that are meant to be public or are obvious placeholders.
ALLOW_RE='@example\.(com|org|net)|noreply@|no-reply@|you@|user@|someone@|name@|<[a-z-]+>|\
127\.0\.0\.1|0\.0\.0\.0|localhost|1\.2\.3\.4|192\.0\.2\.|198\.51\.100\.|203\.0\.113\.|\
\b0\.0\.0\b|\b[0-9]+\.[0-9]+\.[0-9]+\b(?![0-9.])'

EXC=(--exclude-dir=.git "--exclude=$SELF" --exclude=secret-scan.sh --exclude='*.lock')

found=0
echo "=== Sanitize scan: $TARGET ==="

report() { # label, payload
  [ -n "$2" ] || return 0
  echo "--- $1 ---"; echo "$2" | head -20; found=1
}

# 1. absolute host paths
report "HOST PATHS" "$(grep -rInP "${EXC[@]}" "$PATH_RE" "$TARGET" 2>/dev/null | head -20)"

# 2. email addresses that are not placeholders
emails=$(grep -rInoP "${EXC[@]}" "$EMAIL_RE" "$TARGET" 2>/dev/null \
         | grep -vP "$ALLOW_RE" | head -20)
report "EMAIL" "$emails"

# 3. IPv4 literals that are not loopback/documentation ranges
ips=$(grep -rInoP "${EXC[@]}" "$HOST_RE" "$TARGET" 2>/dev/null \
      | grep -vP "$ALLOW_RE" | head -20)
report "IP ADDRESS" "$ips"

# 4. operator-specific terms, kept out of this repo on purpose
if [ -f "$TERMS_FILE" ]; then
  terms=$(grep -vE '^\s*(#|$)' "$TERMS_FILE" 2>/dev/null | paste -sd'|' -)
  if [ -n "$terms" ]; then
    hits=$(grep -rInEi "${EXC[@]}" "$terms" "$TARGET" 2>/dev/null | head -20 \
           | sed -E 's/(.{100}).*/\1…/')
    report "OPERATOR IDENTITY" "$hits"
  fi
else
  echo "note: no terms file at $TERMS_FILE — generic checks only"
fi

# 5. same checks across history, so a scrubbed working tree cannot hide an old leak
if [ "$MODE" = "full" ]; then
  revs=$(git -C "$TARGET" rev-list --all 2>/dev/null)
  if [ -n "$revs" ]; then
    hist=$(timeout 120 git -C "$TARGET" grep -I -n -P "$PATH_RE" $revs \
             -- ":(exclude)scripts/$SELF" 2>/dev/null | head -10)
    report "HISTORY (host paths)" "$hist"
  fi
fi

if [ "$found" -eq 0 ]; then echo "CLEAN: no identity/host leaks detected."; exit 0; fi
echo "LEAK DETECTED — do NOT publish until remediated."
exit 1
