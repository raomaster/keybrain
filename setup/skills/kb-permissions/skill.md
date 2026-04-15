---
description: "Add a Bash permission to settings.json for KeyBrain"
---

Add the specified permission to `~/.claude/settings.json`.

**Input:** $ARGUMENTS

**Process:**

1. If no input, ask the user what command needs permission
2. Add the permission pattern to the `permissions.allow` array in `~/.claude/settings.json`
3. Confirm what was added and where
4. Remind that Claude Code needs to be restarted for changes to take effect

**Usage examples:**
- `/kb-permissions Bash(cp $KB_VAULT*)`
- `/kb-permissions Bash(mv $KB_VAULT*)`
- `/kb-permissions Bash(mkdir $KB_VAULT*)`
- `/kb-permissions Bash(rm $KB_VAULT*)`
