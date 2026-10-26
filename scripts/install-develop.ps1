# Windows PowerShell 5.1+ / PowerShell 7. No Python or Git required.
[CmdletBinding()]
param(
    [ValidateSet('manual', 'codex', 'claude')]
    [string]$Target = 'manual',
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
$archivePath = $null

function Expand-SkillArchive([string]$Archive, [string]$Destination) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($Archive)
    try {
        $root = $null
        $selected = @{}
        $seen = @{}
        if ($zip.Entries.Count -gt 20000) { throw 'Archive has too many entries.' }
        foreach ($entry in $zip.Entries) {
            $name = $entry.FullName
            # Validate every entry, but only write the three required regular files.
            if ($name -match '\\|:|[\x00-\x1f]' -or $name.StartsWith('/') -or
                @($name.TrimEnd('/').Split('/') | Where-Object { $_ -eq '.' -or $_ -eq '..' -or $_ -eq '' -or $_ -match '[. ]$' }).Count) {
                throw 'Unsafe archive path.'
            }
            $parts = $name.Split('/')
            if (!$root) {
                $root = $parts[0]
                if ($root -cnotmatch '^using-AI-.+$') { throw 'Unexpected archive root.' }
            }
            if ($parts[0] -cne $root -or $parts.Count -lt 2 -or $seen.ContainsKey($name)) { throw 'Unexpected or duplicate archive structure.' }
            $seen[$name] = $true
            $unixType = ($entry.ExternalAttributes -shr 16) -band 0xF000
            if (($unixType -ne 0 -and $unixType -ne 0x8000 -and $unixType -ne 0x4000) -or
                ($entry.ExternalAttributes -band 0x400)) { throw 'Linked or special archive entry.' }
            $relative = $name.Substring($root.Length + 1)
            if ($relative -clike 'skills/develop/*') {
                $file = $relative.Substring('skills/develop/'.Length)
                if ($files -ccontains $file) {
                    if ($entry.Length -le 0 -or $entry.Length -gt 2MB -or $name.EndsWith('/') -or $unixType -eq 0x4000) { throw 'Invalid package entry size or type.' }
                    $selected[$file] = $entry
                }
            }
        }
        foreach ($file in $files) {
            if (!$selected.ContainsKey($file)) { throw "Incomplete package: $file" }
            [IO.Compression.ZipFileExtensions]::ExtractToFile($selected[$file], (Join-Path $Destination $file))
        }
    }
    finally { $zip.Dispose() }
}

function Stop-GitHubRequest([string]$Phase, [string]$Url, $Failure) {
    $status = 'unavailable (network/proxy/TLS/timeout; no HTTP response)'
    $details = @()
    $response = $Failure.Exception.Response
    if ($response) {
        if ($null -ne $response.StatusCode) { $status = [string][int]$response.StatusCode }
        # Allowlist numeric diagnostics only; never print arbitrary headers or exception text.
        foreach ($name in @('X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset', 'Retry-After')) {
            $value = [string]($response.Headers[$name] -join ',')
            if ($value -match '^\d{1,20}$') { $details += "$name=$value" }
        }
    }
    # GitHub JSON messages may contain user input. Report only recognized categories.
    if ($Failure.ErrorDetails.Message) {
        try {
            $body = $Failure.ErrorDetails.Message | ConvertFrom-Json
            if ($body.message -match 'rate limit') { $details += 'GitHub response: rate limit exceeded' }
            elseif ($body.message -match '^Not Found$') { $details += 'GitHub response: not found' }
            elseif ($body.message -match '^Bad credentials$') { $details += 'GitHub response: bad credentials' }
            elseif ($body.message -match 'access blocked') { $details += 'GitHub response: access blocked' }
        } catch { } # Non-JSON proxy responses are deliberately omitted.
    }
    throw "$Phase failed; HTTP $status; URL: $Url. $($details -join '; '). Check the selected -Ref and network/proxy policy. Existing Skill is unchanged."
}

function Assert-PlainDirectory([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    if (!$item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Not a plain directory (links are not supported): $Path"
    }
}

function Assert-UnlinkedTree([string]$Path) {
    Assert-PlainDirectory $Path
    foreach ($item in Get-ChildItem -LiteralPath $Path -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Linked content detected; left untouched: $($item.FullName)"
        }
        if ($item.PSIsContainer) { Assert-UnlinkedTree $item.FullName }
    }
}

function Assert-ExistingSkill([string]$Path) {
    # Only explicit uninstall may recognize a package without an installation record.
    if (!$Uninstall -or (Test-Path -LiteralPath (Join-Path $Path $manifestName))) {
        Assert-Managed $Path
        return
    }
    Assert-UnlinkedTree $Path
    $entryPath = Join-Path $Path 'SKILL.md'
    $rulePath = Join-Path $Path 'references/develop.md'
    $unknown = "Unknown existing Skill: $Path. Inspect it manually and move the entire directory outside skills to a backup; no files were changed."
    if (!(Test-Path -LiteralPath $entryPath -PathType Leaf) -or !(Test-Path -LiteralPath $rulePath -PathType Leaf)) { throw $unknown }
    $entry = Get-Content -LiteralPath $entryPath -Raw -Encoding UTF8
    $rules = Get-Content -LiteralPath $rulePath -Raw -Encoding UTF8
    # Escaped Chinese headings keep this script ASCII-safe for Windows PowerShell 5.1.
    if ($entry -notmatch '\A---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)' -or
        $entry -notmatch '(?m)^name: develop\s*$' -or
        $entry -notmatch '\]\(references/develop\.md\)' -or
        $rules -notmatch '(?m)^# \u901a\u7528\u7814\u53d1\u5de5\u4f5c\u6d41\s*$' -or
        $rules -notmatch '(?m)^## \u9009\u62e9\u6d41\u7a0b\s*$' -or
        $rules -notmatch '(?m)^## \u5b9e\u73b0\u4e0e\u5fc5\u8981\u68c0\u67e5\s*$' -or
        $rules -notmatch '(?m)^## \u4ea4\u4ed8\s*$' -or $rules -notmatch 'using-AI') { throw $unknown }
}

function Assert-Package([string]$Path) {
    foreach ($file in $files) {
        $full = Join-Path $Path $file
        if (!(Test-Path -LiteralPath $full -PathType Leaf) -or (Get-Item -LiteralPath $full).Length -eq 0) {
            throw "Incomplete package: $file. Retry or report the selected GitHub ref."
        }
    }
    $entry = Get-Content -LiteralPath (Join-Path $Path 'SKILL.md') -Raw -Encoding UTF8
    $metadata = [regex]::Match($entry, '\A---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)')
    if (!$metadata.Success -or $metadata.Groups[1].Value -notmatch '(?m)^name: develop\s*$' -or
        $entry -notmatch '\]\(references/develop\.md\)') {
        throw 'Invalid SKILL.md: expected develop metadata and a local references/develop.md link.'
    }
    $rules = Get-Content -LiteralPath (Join-Path $Path 'references/develop.md') -Raw -Encoding UTF8
    if ($rules -notmatch '(?m)^# \u901a\u7528\u7814\u53d1\u5de5\u4f5c\u6d41\s*$' -or
        $rules -notmatch '(?m)^## \u4ea4\u4ed8\s*$') {
        throw 'Invalid references/develop.md: expected workflow title and delivery section.'
    }
    $license = Get-Content -LiteralPath (Join-Path $Path 'LICENSE') -Raw -Encoding UTF8
    if ($license -notmatch '\AMIT License\r?\n' -or $license -notmatch 'THE SOFTWARE IS PROVIDED "AS IS"') {
        throw 'Invalid LICENSE: expected the MIT license.'
    }
}

function Assert-Managed([string]$Path) {
    Assert-PlainDirectory $Path
    Assert-UnlinkedTree $Path
    $items = @(Get-ChildItem -LiteralPath $Path -Recurse -Force)
    if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) {
        throw "Linked content detected; left untouched: $Path"
    }
    $manifestPath = Join-Path $Path $manifestName
    if (!(Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Unknown existing Skill: $Path. Move it outside the skills directories as a backup, then install again."
    }
    $record = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $validSource = ($record.schema -eq 1 -and $record.commit -match '^[a-f0-9]{40}$') -or
        ($record.schema -eq 2 -and $record.ref -is [string] -and ![string]::IsNullOrWhiteSpace($record.ref) -and
         $record.source -ceq "https://codeload.github.com/Jrencat/using-AI/zip/$([Uri]::EscapeDataString($record.ref))" -and
         $record.archiveSha256 -match '^[A-Fa-f0-9]{64}$' -and
         ($null -eq $record.commit -or ($record.ref -match '^[A-Fa-f0-9]{40}$' -and $record.commit -ceq $record.ref.ToLowerInvariant())))
    if ($record.origin -ne $origin -or !$validSource) {
        throw "Unrecognized installation record; left untouched: $Path"
    }
    if (@($items | Where-Object { !$_.PSIsContainer }).Count -ne $files.Count + 1 -or
        @($items | Where-Object { $_.PSIsContainer -and $_.FullName -ne (Join-Path $Path 'references') }).Count -ne 0 -or
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
    $agents = switch ($Target) {
        'codex' { Join-Path $userRoot '.agents' }
        'claude' {
            if ($env:CLAUDE_CONFIG_DIR) { [IO.Path]::GetFullPath($env:CLAUDE_CONFIG_DIR) }
            else { Join-Path $userRoot '.claude' }
        }
        'manual' { Join-Path $userRoot '.using-ai' }
    }
    $skills = Join-Path $agents $(if ($Target -eq 'manual') { 'workflows' } else { 'skills' })
    $destinationPath = Join-Path $skills 'develop'
    # Check ancestors before creating directories or following a relocated config path.
    $ancestor = [IO.DirectoryInfo]::new($agents)
    while ($ancestor) {
        if (Test-Path -LiteralPath $ancestor.FullName) { Assert-PlainDirectory $ancestor.FullName }
        $ancestor = $ancestor.Parent
    }
    if ($Target -eq 'claude' -and !$Uninstall -and (Test-Path -LiteralPath (Join-Path $agents 'commands/develop.md'))) {
        throw 'Existing /develop command; resolve the name conflict first.'
    }
    foreach ($directory in @($agents, $skills)) {
        if (!(Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory | Out-Null }
        Assert-PlainDirectory $directory
    }
    $lockPath = Join-Path $agents 'using-ai-develop.lock'
    try { $lock = [IO.File]::Open($lockPath, 'CreateNew', 'Write', 'None') }
    catch { throw "Another install may be running, or access is denied: $lockPath. If a previous process crashed, inspect and remove that lock before retrying." }
    $exists = Test-Path -LiteralPath $destinationPath
    if ($exists) { Assert-ExistingSkill $destinationPath }
    if ($exists -and !$Update -and !$Uninstall) {
        Write-Output "Already installed: $destinationPath. Use -Update to check for a newer version."
        return
    }
    if (!$exists -and ($Update -or $Uninstall)) { throw "No managed installation at $destinationPath. Run without -Update/-Uninstall to install." }
    if (!$Uninstall) {
        # Refuse a second user-level copy that could shadow this installation.
        $otherPaths = @()
        if ($Target -eq 'codex') {
            $otherPaths += Join-Path $userRoot '.codex/skills/develop'
            if ($env:CODEX_HOME) { $otherPaths += Join-Path $env:CODEX_HOME 'skills/develop' }
        }
        foreach ($other in $otherPaths) {
            if ([IO.Path]::GetFullPath($other) -ne $destinationPath -and (Test-Path -LiteralPath $other)) {
                throw "Another user-level develop Skill exists: $other. Back it up outside skills before installing here."
            }
        }
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        if ([string]::IsNullOrWhiteSpace($Ref) -or $Ref -match '[\x00-\x20\x7f]') { throw '-Ref must not be empty or contain whitespace/control characters.' }
        $commit = $null
        if ($Ref -match '^[a-fA-F0-9]{40}$') {
            $commit = $Ref.ToLowerInvariant()
        }
        elseif ($Ref -match '^[a-fA-F0-9]{4,39}$') {
            # Preserve short-SHA support; only this ambiguous form needs API resolution.
            $encodedRef = [Uri]::EscapeDataString($Ref)
            $url = "https://api.github.com/repos/Jrencat/using-AI/commits/$encodedRef"
            try { $commit = (Invoke-RestMethod -Uri $url -Headers @{ 'User-Agent' = 'using-ai-installer' } -TimeoutSec 30).sha }
            catch { Stop-GitHubRequest 'API ref resolution' $url $_ }
            if ($commit -isnot [string] -or $commit -cnotmatch '^[a-f0-9]{40}$') {
                throw "API ref resolution returned invalid content; URL: $url. Expected a full commit SHA. Existing Skill is unchanged."
            }
        }
        $stage = Join-Path $agents ('using-ai-stage-' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path (Join-Path $stage 'references') -Force | Out-Null
        $archiveRef = if ($commit) { $commit } else { $Ref }
        $url = "https://codeload.github.com/Jrencat/using-AI/zip/$([Uri]::EscapeDataString($archiveRef))"
        $archivePath = Join-Path $agents ('using-ai-download-' + [guid]::NewGuid().ToString('N') + '.zip')
        try { Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $archivePath -TimeoutSec 60 -MaximumRedirection 0 | Out-Null }
        catch { Stop-GitHubRequest 'Archive download' $url $_ }
        try { Expand-SkillArchive $archivePath $stage }
        catch { throw "Archive extraction failed; URL: $url. $($_.Exception.Message) Existing Skill is unchanged." }
        try { Assert-Package $stage }
        catch { throw "Package validation failed; URL: $url. $($_.Exception.Message) Existing Skill is unchanged." }
        $hashes = [ordered]@{}
        foreach ($file in $files) { $hashes[$file] = (Get-FileHash -LiteralPath (Join-Path $stage $file) -Algorithm SHA256).Hash }
        # A mutable ref archive does not prove a commit; never infer SHA from its directory name.
        @{ schema = 2; origin = $origin; commit = $commit; ref = $archiveRef; requestedRef = $Ref; source = $url;
           archiveSha256 = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash; hashes = $hashes } |
            ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $stage $manifestName) -Encoding UTF8
        Assert-Managed $stage
        if ($exists) {
            Assert-Managed $destinationPath
            $old = Get-Content -LiteralPath (Join-Path $destinationPath $manifestName) -Raw -Encoding UTF8 | ConvertFrom-Json
            $sameFiles = @($files | Where-Object { $old.hashes.PSObject.Properties[$_].Value -ne $hashes[$_] }).Count -eq 0
            if ($sameFiles -and $old.ref -ceq $archiveRef -and $old.schema -eq 2 -and $old.commit -eq $commit) {
                Write-Output "Already up to date: ref $Ref (package hashes unchanged)"; return
            }
        }
    }
    $backup = $null
    if ($exists) {
        Assert-ExistingSkill $destinationPath
        $backupRoot = Join-Path $agents 'using-ai-backups'
        if (!(Test-Path -LiteralPath $backupRoot)) { New-Item -ItemType Directory -Path $backupRoot | Out-Null }
        Assert-PlainDirectory $backupRoot
        $backup = Join-Path $backupRoot ('develop-' + [guid]::NewGuid().ToString('N'))
        [IO.Directory]::Move($destinationPath, $backup)
        Write-Output "Previous Skill preserved outside discovery paths: $backup"
    }
    if ($Uninstall) { Write-Output 'Uninstalled. Reload the selected host/context; backups were retained.'; return }
    try {
        [IO.Directory]::Move($stage, $destinationPath)
        $stage = $null
        Assert-Managed $destinationPath
    }
    catch {
        if ($backup -and !(Test-Path -LiteralPath $destinationPath)) { [IO.Directory]::Move($backup, $destinationPath) }
        throw
    }
    Write-Output "Installed: $destinationPath (ref $Ref; commit $(if ($commit) { $commit } else { 'unknown; see installation record for archive source and hashes' }))"
    switch ($Target) {
        'codex' { Write-Output 'Start a new Codex session: $develop <requirement>' }
        'claude' { Write-Output 'Start a new Claude Code session: /develop <requirement>' }
        'manual' { Write-Output 'Provide references/develop.md to your AI as project context or prompt, together with your requirement. No automatic discovery is configured.' }
    }
}
catch {
    throw "develop install failed: $($_.Exception.Message) For access errors, check directory permissions; do not run as administrator to overwrite another user's files."
}
finally {
    if ($archivePath -and (Test-Path -LiteralPath $archivePath)) { Remove-Item -LiteralPath $archivePath -Force }
    if ($stage -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force }
    if ($lock) { $lock.Dispose(); Remove-Item -LiteralPath $lockPath -Force }
}
