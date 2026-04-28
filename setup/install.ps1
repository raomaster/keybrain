# ============================================================
# KeyBrain — Setup Script (Windows)
# ============================================================
# Usage: Set-ExecutionPolicy RemoteSigned; .\setup\install.ps1
# Installs and configures the complete KeyBrain system.
# Requires PowerShell 5+ and Windows 10/11.
# ============================================================

param(
    [string]$VaultPath = "$env:USERPROFILE\Knowledge",
    [string]$RuntimePath = "$env:LOCALAPPDATA\KeyBrain",
    [ValidateSet("opencode", "claude")]
    [string]$ProcessAgent = "",
    [switch]$SkipObsidian,
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"
$GREEN  = "Green"
$YELLOW = "Yellow"
$RED    = "Red"

function Log   { param($msg) Write-Host "[KB] $msg" -ForegroundColor $GREEN }
function Warn  { param($msg) Write-Host "[KB WARN] $msg" -ForegroundColor $YELLOW }
function Step  { param($msg) Write-Host "`n━━━ $msg ━━━" -ForegroundColor $GREEN }
function Abort { param($msg) Write-Host "[KB ERROR] $msg" -ForegroundColor $RED; exit 1 }

# ── Check admin (optional but recommended) ──
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Warn "Not running as Administrator. Some steps may fail."
}

# ── 1. winget ────────────────────────────────────────────────
Step "Verify winget"
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Abort "winget not found. Install 'App Installer' from Microsoft Store and try again."
}
Log "winget available."

# ── 2. Git ───────────────────────────────────────────────────
Step "Git"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Log "Installing Git..."
    winget install --id Git.Git -e --source winget --silent
    $env:PATH += ";C:\Program Files\Git\bin"
} else {
    Log "Git already installed: $(git --version)"
}

# ── 3. Node.js ───────────────────────────────────────────────
Step "Node.js"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Log "Installing Node.js LTS..."
    winget install --id OpenJS.NodeJS.LTS -e --source winget --silent
    $env:PATH += ";$env:PROGRAMFILES\nodejs"
} else {
    Log "Node.js already installed: $(node --version)"
}

# ── 4. Claude Code CLI ──────────────────────────────────────
Step "Claude Code CLI"
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Log "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code
} else {
    Log "Claude Code already installed."
}

# ── 5. Obsidian ─────────────────────────────────────────────
if (-not $SkipObsidian) {
    Step "Obsidian"
    $obsidianPath = "$env:LOCALAPPDATA\Programs\Obsidian\Obsidian.exe"
    if (-not (Test-Path $obsidianPath)) {
        Log "Installing Obsidian..."
        winget install --id Obsidian.Obsidian -e --source winget --silent
    } else {
        Log "Obsidian already installed."
    }
}

# ── 6. markitdown (YouTube + document processing) ────────────
# markitdown is installed via requirements.txt in the Python venv (see step 7)
Log "markitdown: will be installed via pip install -r requirements.txt"

# ── 6b. Processing agent ────────────────────────────────────
Step "KeyBrain processing agent"
$hasOpenCode = [bool](Get-Command opencode -ErrorAction SilentlyContinue)
$hasClaude = [bool](Get-Command claude -ErrorAction SilentlyContinue)

if (-not $ProcessAgent) {
    if ($NonInteractive) {
        if ($hasOpenCode) { $ProcessAgent = "opencode" }
        elseif ($hasClaude) { $ProcessAgent = "claude" }
        else { $ProcessAgent = "opencode" }
    } else {
        Write-Host "Which agent should process KeyBrain inbox files?"
        Write-Host "  1) OpenCode (recommended) — $(if ($hasOpenCode) { 'detected' } else { 'not detected yet' })"
        Write-Host "  2) Claude Code — $(if ($hasClaude) { 'detected' } else { 'not detected yet' })"
        $choice = Read-Host "Agent [Enter for opencode]"
        switch ($choice) {
            "2" { $ProcessAgent = "claude" }
            "claude" { $ProcessAgent = "claude" }
            default { $ProcessAgent = "opencode" }
        }
    }
}
Log "Using $ProcessAgent for kb process."

# ── 7. Python 3.12 + venv + deps ────────────────────────────
Step "Python 3.12 + dependencies"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Log "Installing Python 3.12..."
    winget install --id Python.Python.3.12 -e --source winget --silent
    $env:PATH += ";$env:LOCALAPPDATA\Programs\Python\Python312"
}

$venvDir = if ($env:KB_VENV) { $env:KB_VENV } else { "$RuntimePath\venv" }
$chromadbDir = if ($env:KB_CHROMADB) { $env:KB_CHROMADB } else { "$RuntimePath\chromadb" }

New-Item -ItemType Directory -Path $RuntimePath -Force | Out-Null
if (-not (Test-Path $venvDir)) {
    Log "Creating venv in $venvDir..."
    python -m venv $venvDir
}
New-Item -ItemType Directory -Path $chromadbDir -Force | Out-Null

Log "Installing Python dependencies..."
$scriptDir = Split-Path -Parent $PSScriptRoot
& "$venvDir\Scripts\pip.exe" install -r "$scriptDir\requirements.txt" --quiet
Log "Dependencies installed."

# ── 8. Configure vault ─────────────────────────────────────
Step "Setting up vault at $VaultPath"
$scriptDir = Split-Path -Parent $PSScriptRoot
if ($scriptDir -ne $VaultPath) {
    if (Test-Path $VaultPath) {
        Warn "$VaultPath already exists. Not overwriting."
    } else {
        Log "Copying vault to $VaultPath..."
        Copy-Item -Recurse $scriptDir $VaultPath
    }
} else {
    Log "Already at the vault."
}

# ── 9. kb PowerShell command ────────────────────────────────
Step "Creating kb command for PowerShell"
$kbScript = @"
# kb — KeyBrain capture for Windows PowerShell
param([string]`$Command, [Parameter(ValueFromRemainingArguments=`$true)][string[]]`$KbArgs)
`$VAULT = `$env:KB_VAULT
if (-not `$VAULT) { `$VAULT = "`$env:USERPROFILE\Knowledge" }
`$VENV = `$env:KB_VENV
if (-not `$VENV) { `$VENV = "$venvDir" }
`$CHROMADB = `$env:KB_CHROMADB
if (-not `$CHROMADB) { `$CHROMADB = "$chromadbDir" }
`$env:KB_VAULT = `$VAULT
`$env:KB_VENV = `$VENV
`$env:KB_CHROMADB = `$CHROMADB
if (-not `$env:KB_PROCESS_AGENT) { `$env:KB_PROCESS_AGENT = "$ProcessAgent" }
`$INBOX = "`$VAULT\inbox"
`$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"
`$ArgText = (`$KbArgs -join " ").Trim()

switch (`$Command) {
    "add" {
        if (-not `$ArgText) { Write-Host "Usage: kb add <file>"; exit 1 }
        Copy-Item `$ArgText `$INBOX\
        Write-Host "Added: `$(Split-Path -Leaf `$ArgText) → inbox/"
    }
    "process" {
        Write-Host "Processing inbox..."
        bash "`$VAULT\bin\process-inbox.sh"
    }
    "index" {
        & "`$VENV\Scripts\python.exe" "`$VAULT\bin\kb-index.py" @KbArgs
    }
    "search" {
        if (-not `$ArgText) { Write-Host "Usage: kb search <query>"; exit 1 }
        & "`$VENV\Scripts\python.exe" "`$VAULT\bin\kb-search-semantic.py" @KbArgs
    }
    "status" {
        `$count = (Get-ChildItem `$INBOX -File | Where-Object Name -ne ".gitkeep").Count
        Write-Host "Inbox: `$count pending file(s)"
        Push-Location `$VAULT; `$last = git log -1 --format="%ar — %s" 2>`$null; Pop-Location
        Write-Host "Last commit: `$last"
    }
    "open" { Start-Process explorer.exe `$VAULT }
    default {
        if (-not `$Command) { Write-Host "Usage: kb <text> | kb add <file> | kb process | kb status"; exit 1 }
        `$content = `$Command
        if (`$ArgText) { `$content += " `$ArgText" }
        `$content | Out-File -FilePath "`$INBOX\`$TIMESTAMP.md" -Encoding utf8
        Write-Host "Saved to inbox: `$TIMESTAMP.md"
    }
}
"@

$kbPath = "$VaultPath\bin\kb.ps1"
New-Item -ItemType Directory -Path "$VaultPath\bin" -Force | Out-Null
$kbScript | Out-File -FilePath $kbPath -Encoding utf8
Log "kb.ps1 created at $kbPath"

# Alias in PowerShell profile
$profileDir = Split-Path $PROFILE
New-Item -ItemType Directory -Path $profileDir -Force | Out-Null

$aliasLine = "function kb { & `"$VaultPath\bin\kb.ps1`" @args }"
if (-not (Test-Path $PROFILE) -or -not (Select-String -Path $PROFILE -Pattern "KeyBrain" -Quiet)) {
    Add-Content -Path $PROFILE -Value "`n# KeyBrain"
    Add-Content -Path $PROFILE -Value "`$env:KB_VAULT = `"$VaultPath`""
    Add-Content -Path $PROFILE -Value "`$env:KB_VENV = `"$venvDir`""
    Add-Content -Path $PROFILE -Value "`$env:KB_CHROMADB = `"$chromadbDir`""
    Add-Content -Path $PROFILE -Value "`$env:KB_PROCESS_AGENT = `"$ProcessAgent`""
    Add-Content -Path $PROFILE -Value $aliasLine
    Log "Alias 'kb', KB_VAULT, KB_VENV, KB_CHROMADB, and KB_PROCESS_AGENT added to PowerShell profile."
} else {
    Log "Alias already exists."
}

# ── 10. Claude Code skills ──────────────────────────────────
Step "Installing Claude Code skills"
$commandsDir = "$env:USERPROFILE\.claude\commands"
New-Item -ItemType Directory -Path $commandsDir -Force | Out-Null

$skillsSrc = "$VaultPath\setup\skills"
if (Test-Path $skillsSrc) {
    Copy-Item "$skillsSrc\*" $commandsDir -Force
    Log "Skills installed to $commandsDir"
}

# ── 11. Claude Code global CLAUDE.md ───────────────────────
Step "Configuring global Claude Code instructions"
$claudeDir = "$env:USERPROFILE\.claude"
New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
$claudeMd = "$claudeDir\CLAUDE.md"

$kbInstructions = @"

# Global

When making an important technical decision, save it without asking: ``kb "Decision: [what] — Why: [reason] — Rejected: [alternatives]"``
After executing a Superpowers plan, export the file: ``kb add docs/superpowers/plans/[plan].md``
KeyBrain KB at ``$env:KB_VAULT`` with ChromaDB — use ``kb-search-semantic "query"`` before answering technical questions that might be in the vault.
"@

if (-not (Test-Path $claudeMd) -or -not (Select-String -Path $claudeMd -Pattern "KeyBrain" -Quiet)) {
    Add-Content -Path $claudeMd -Value $kbInstructions
    Log "Global CLAUDE.md configured."
} else {
    Log "Global CLAUDE.md already has KeyBrain instructions."
}

# ── 12. settings.json ──────────────────────────────────────
Step "Configuring automatic permissions for the vault"
$settingsFile = "$claudeDir\settings.json"
$vaultEscaped = $VaultPath -replace '\\', '/'

if (-not (Test-Path $settingsFile)) {
    @"
{
  "permissions": {
    "allow": [
      "Edit($vaultEscaped/**)",
      "Write($vaultEscaped/**)",
      "Read($vaultEscaped/**)",
      "Bash(cd $vaultEscaped*)",
      "Bash(git -C $vaultEscaped*)"
    ]
  }
}
"@ | Out-File -FilePath $settingsFile -Encoding utf8
    Log "settings.json created with vault permissions."
} elseif (-not (Select-String -Path $settingsFile -Pattern "permissions" -Quiet)) {
    Warn "settings.json exists but has no vault permissions. Add them manually."
} else {
    Log "settings.json already has permissions configured."
}

# ── 13. Git setup ────────────────────────────────────────────
Step "Git repo"
Push-Location $VaultPath
if (-not (Test-Path ".git")) {
    git init
    git add -A
    git commit -m "init: KeyBrain knowledge vault"
    Log "Git initialized."
    Warn "To connect with GitHub:"
    Warn "  1. gh auth login"
    Warn "  2. gh repo create keybrain-vault --private --source=. --remote=origin --push"
} else {
    Log "Git already initialized."
}
Pop-Location

# ── Open Obsidian ───────────────────────────────────────────
if (-not $SkipObsidian) {
    $obsidianPath = "$env:LOCALAPPDATA\Programs\Obsidian\Obsidian.exe"
    if (Test-Path $obsidianPath) {
        Start-Process $obsidianPath $VaultPath
    }
}

# ── Summary ────────────────────────────────────────────────
Write-Host ""
Write-Host "┌─────────────────────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│  KeyBrain installed and ready                           │" -ForegroundColor Green
Write-Host "│                                                          │" -ForegroundColor Green
Write-Host "│  Commands (open new PowerShell):                        │" -ForegroundColor Green
Write-Host "│    kb `"text or URL`"    → save to inbox                  │" -ForegroundColor Green
Write-Host "│    kb add <file>      → copy file to inbox              │" -ForegroundColor Green
Write-Host "│    kb process         → process inbox now               │" -ForegroundColor Green
Write-Host "│    kb status          → vault status                    │" -ForegroundColor Green
Write-Host "│                                                          │" -ForegroundColor Green
Write-Host "│  Slash commands in Claude Code:                         │" -ForegroundColor Green
Write-Host "│    /kb-add /kb-process /kb-search /kb-health /kb-compile│" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Green
