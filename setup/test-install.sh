#!/usr/bin/env bash
# test-install.sh — Smoke tests for KeyBrain installation
# Run: bash setup/test-install.sh

set -euo pipefail

VAULT="${KB_VAULT:-$HOME/Knowledge}"
PASS=0
FAIL=0

check() {
  if eval "$2" &>/dev/null; then
    echo "  PASS: $1"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $1"
    FAIL=$((FAIL + 1))
  fi
}

echo "KeyBrain Smoke Tests"
echo "  Vault: $VAULT"
echo ""

echo "1. Structure"
check "inbox/ exists"       "[ -d '$VAULT/inbox' ]"
check "raw/ exists"         "[ -d '$VAULT/raw' ]"
check "wiki/ exists"        "[ -d '$VAULT/wiki' ]"
check "decisions/ exists"   "[ -d '$VAULT/decisions' ]"
check "bin/ exists"         "[ -d '$VAULT/bin' ]"
check "templates/ exists"   "[ -d '$VAULT/templates' ]"

echo ""
echo "2. Scripts"
check "kb is executable"    "[ -x '$VAULT/bin/kb' ]"
check "kb-index exists"     "[ -f '$VAULT/bin/kb-index.py' ]"
check "kb-search exists"    "[ -f '$VAULT/bin/kb-search-semantic.py' ]"
check "process-inbox exists" "[ -x '$VAULT/bin/process-inbox.sh' ]"

echo ""
echo "3. Configuration"
check "CLAUDE.md exists"    "[ -f '$VAULT/CLAUDE.md' ]"
check "VERSION exists"      "[ -f '$VAULT/VERSION' ]"
check "wiki/_index.md exists" "[ -f '$VAULT/wiki/_index.md' ]"

echo ""
echo "4. CLI"
check "kb shows usage"      "bash -c '$VAULT/bin/kb 2>&1 | grep -qi usage'"
check "kb status works"     "bash -c '$VAULT/bin/kb status 2>&1 | grep -qi inbox'"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
