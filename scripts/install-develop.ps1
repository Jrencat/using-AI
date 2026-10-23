# Windows PowerShell 5.1+ / PowerShell 7. No Python or Git required.
[CmdletBinding()]
param(
    [switch]$Update,
    [switch]$Uninstall,
    [string]$Ref = 'main',
    [string]$UserDirectory = [Environment]::GetFolderPath('UserProfile')
)

$ErrorActionPreference = 'Stop'
$origin = 'https://github.com/Jrencat/using-AI'
$files = @('SKILL.md', 'references/develop.md', 'LICENSE')
$manifestName = '.using-ai-install.json'
$stage = $null
$lock = $null
$lockPath = $null

function Assert-PlainDirectory([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    if (!$item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Not a plain directory (links are not supported): $Path"
    }
}

function Assert-Package([string]$Path) {
    foreach ($file in $files) {
        $full = Join-Path $Path $file
        if (!(Test-Path -LiteralPath $full -PathType Leaf) -or (Get-Item -LiteralPath $full).Length -eq 0) {
            throw "Incomplete package: $file. Retry or report the selected GitHub ref."
        }
    }
    $entry = Get-Content -LiteralPath (Join-Path $Path 'SKILL.md') -Raw -Encoding UTF8
    if ($entry -notmatch '(?m)^name: develop\s*$' -or $entry -notmatch '\]\(references/develop\.md\)') {
        throw 'Invalid SKILL.md: expected develop metadata and a local references/develop.md link.'
    }
}

function Assert-Managed([string]$Path) {
    Assert-PlainDirectory $Path
    $items = @(Get-ChildItem -LiteralPath $Path -Recurse -Force)
    if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) {
        throw "Linked content detected; left untouched: $Path"
    }
    $manifestPath = Join-Path $Path $manifestName
    if (!(Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Unknown existing Skill: $Path. Move it outside the skills directories as a backup, then install again."
    }
    $record = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($record.origin -ne $origin -or $record.schema -ne 1 -or $record.commit -notmatch '^[a-f0-9]{40}$') {
        throw "Unrecognized installation record; left untouched: $Path"
    }
    if (@($items | Where-Object { !$_.PSIsContainer }).Count -ne $files.Count + 1 -or
        @($record.hashes.PSObject.Properties).Count -ne $files.Count) {
        throw "Local additions detected; move the Skill outside skills as a backup before reinstalling: $Path"
    }
    Assert-Package $Path
    foreach ($file in $files) {
        $expected = $record.hashes.PSObject.Properties[$file]
        if (!$expected -or (Get-FileHash -LiteralPath (Join-Path $Path $file) -Algorithm SHA256).Hash -ne $expected.Value) {
            throw "Local changes detected in $file. Back up the Skill outside skills and reinstall; no files were replaced."
        }
    }
}

try {
    if ($PSVersionTable.PSVersion -lt [version]'5.1') { throw 'PowerShell 5.1 or newer is required.' }
    if ($Update -and $Uninstall) { throw 'Choose either -Update or -Uninstall.' }
    if ([string]::IsNullOrWhiteSpace($UserDirectory)) { throw 'Cannot resolve the user directory.' }
    $userRoot = [IO.Path]::GetFullPath($UserDirectory)
    Assert-PlainDirectory $userRoot
    $agents = Join-Path $userRoot '.agents'
    $skills = Join-Path $agents 'skills'
    $target = Join-Path $skills 'develop'
    foreach ($directory in @($agents, $skills)) {
        if (!(Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory | Out-Null }
        Assert-PlainDirectory $directory
    }
    $lockPath = Join-Path $agents 'using-ai-develop.lock'
    try { $lock = [IO.File]::Open($lockPath, 'CreateNew', 'Write', 'None') }
    catch { throw "Another install may be running, or access is denied: $lockPath. If a previous process crashed, inspect and remove that lock before retrying." }
    $exists = Test-Path -LiteralPath $target
    if ($exists) { Assert-Managed $target }
    if ($exists -and !$Update -and !$Uninstall) {
        Write-Output "Already installed: $target. Use -Update to check for a newer version."
        return
    }
    if (!$exists -and ($Update -or $Uninstall)) { throw "No managed installation at $target. Run without -Update/-Uninstall to install." }
    if (!$Uninstall) {
        if (!(Get-Command codex -ErrorAction SilentlyContinue)) { throw 'Codex CLI was not found. Install Codex and make codex available in PATH, then retry.' }
        # Refuse a second user-level copy that could shadow this installation.
        $legacy = Join-Path $userRoot '.codex/skills/develop'
        $otherPaths = @($legacy)
        if ($env:CODEX_HOME) { $otherPaths += Join-Path $env:CODEX_HOME 'skills/develop' }
        foreach ($other in $otherPaths) {
            if ([IO.Path]::GetFullPath($other) -ne $target -and (Test-Path -LiteralPath $other)) {
                throw "Another user-level develop Skill exists: $other. Back it up outside skills before installing here."
            }
        }
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $encodedRef = [Uri]::EscapeDataString($Ref)
        try {
            $commit = (Invoke-RestMethod -Uri "https://api.github.com/repos/Jrencat/using-AI/commits/$encodedRef" -Headers @{ 'User-Agent' = 'using-ai-installer' } -TimeoutSec 30).sha
            if ($commit -notmatch '^[a-f0-9]{40}$') { throw 'Invalid GitHub commit response.' }
            $stage = Join-Path $agents ('using-ai-stage-' + [guid]::NewGuid().ToString('N'))
            New-Item -ItemType Directory -Path (Join-Path $stage 'references') -Force | Out-Null
            foreach ($file in $files) {
                Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/Jrencat/using-AI/$commit/skills/develop/$file" -OutFile (Join-Path $stage $file) -TimeoutSec 30 | Out-Null
            }
        }
        catch { throw "GitHub download failed: $($_.Exception.Message). Check network/proxy, GitHub API rate limits and -Ref, then retry. Existing Skill is unchanged." }
        Assert-Package $stage
        $hashes = [ordered]@{}
        foreach ($file in $files) { $hashes[$file] = (Get-FileHash -LiteralPath (Join-Path $stage $file) -Algorithm SHA256).Hash }
        @{ schema = 1; origin = $origin; commit = $commit; ref = $Ref; hashes = $hashes } |
            ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $stage $manifestName) -Encoding UTF8
        Assert-Managed $stage
        if ($exists) {
            Assert-Managed $target
            $old = Get-Content -LiteralPath (Join-Path $target $manifestName) -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($old.commit -eq $commit) { Write-Output "Already up to date: $commit"; return }
        }
    }
    $backup = $null
    if ($exists) {
        Assert-Managed $target
        $backupRoot = Join-Path $agents 'using-ai-backups'
        if (!(Test-Path -LiteralPath $backupRoot)) { New-Item -ItemType Directory -Path $backupRoot | Out-Null }
        Assert-PlainDirectory $backupRoot
        $backup = Join-Path $backupRoot ('develop-' + [guid]::NewGuid().ToString('N'))
        [IO.Directory]::Move($target, $backup)
        Write-Output "Previous Skill preserved outside discovery paths: $backup"
    }
    if ($Uninstall) { Write-Output 'Uninstalled. Start a new Codex session; backups were retained.'; return }
    try {
        [IO.Directory]::Move($stage, $target)
        $stage = $null
        Assert-Managed $target
    }
    catch {
        if ($backup -and !(Test-Path -LiteralPath $target)) { [IO.Directory]::Move($backup, $target) }
        throw
    }
    Write-Output "Installed: $target (commit $commit)"
    Write-Output 'Open your own project in a new Codex session, then type: $develop help me implement a requirement'
}
catch {
    throw "develop install failed: $($_.Exception.Message) For access errors, check directory permissions; do not run as administrator to overwrite another user's files."
}
finally {
    if ($stage -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force }
    if ($lock) { $lock.Dispose(); Remove-Item -LiteralPath $lockPath -Force }
}
