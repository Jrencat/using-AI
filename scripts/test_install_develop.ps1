# Isolated installer checks using local package fixtures; no network or real user writes.
$ErrorActionPreference = 'Stop'
$installer = Join-Path $PSScriptRoot 'install-develop.ps1'
$package = Join-Path (Split-Path $PSScriptRoot -Parent) 'skills/develop'
$sandbox = Join-Path ([IO.Path]::GetTempPath()) ('using-ai-install-test-' + [guid]::NewGuid().ToString('N'))
$savedCodexHome = $env:CODEX_HOME
$savedClaudeConfig = $env:CLAUDE_CONFIG_DIR
$env:CLAUDE_CONFIG_DIR = $null
$fixtureState = @{ revision = 'a' * 40; incomplete = $false; requests = 0; passed = 0; failureStage = ''; urls = @(); invalid = $false }
$passed = 0
Add-Type -AssemblyName System.IO.Compression.FileSystem
$fixtureState.archiveFault = ''
$fixtureState.status = 403


function Invoke-RestMethod {
    param($Uri, $Headers, $TimeoutSec)
    $fixtureState.requests++
    $fixtureState.urls += $Uri
    if ($fixtureState.failureStage -eq 'API') { Throw-HttpFailure }
    return @{ sha = $fixtureState.revision }
}
function Invoke-WebRequest {
    param([switch]$UseBasicParsing, $Uri, $OutFile, $TimeoutSec, $MaximumRedirection, $ErrorAction)
    $fixtureState.urls += $Uri
    if ($Uri -eq 'https://raw.githubusercontent.com/Jrencat/using-AI/main/scripts/install-develop.ps1') {
        if ($fixtureState.failureStage -eq 'Bootstrap') { throw 'Bootstrap download failed' }
        return [pscustomobject]@{ Content = [IO.File]::ReadAllText($installer) }
    }
    if ($fixtureState.failureStage -eq 'Archive') { Throw-HttpFailure }
    if ($fixtureState.failureStage -eq 'transport') { throw [Net.WebException]::new('fixture-secret', [Net.WebExceptionStatus]::Timeout) }
    if ($fixtureState.archiveFault -eq 'corrupt') { Set-Content -LiteralPath $OutFile -Value 'not a zip'; return }
    $zip = [IO.Compression.ZipFile]::Open($OutFile, 'Create')
    try {
        foreach ($file in @('SKILL.md', 'references/develop.md', 'LICENSE')) {
            if ($fixtureState.incomplete -and $file -eq 'LICENSE') { continue }
            $entry = $zip.CreateEntry("using-AI-fixture/skills/develop/$file")
            $stream = $entry.Open()
            try {
                $bytes = [IO.File]::ReadAllBytes((Join-Path $package $file))
                if ($fixtureState.invalid -eq $file) { $bytes = [Text.Encoding]::UTF8.GetBytes('<html>invalid</html>') }
                elseif ($fixtureState.invalid -eq 'metadata' -and $file -eq 'SKILL.md') {
                    $bytes = [Text.Encoding]::UTF8.GetBytes(([Text.Encoding]::UTF8.GetString($bytes).Replace('name: develop', 'name: wrong')) + "`nname: develop`n")
                }
                elseif ($file -eq 'SKILL.md' -and $fixtureState.revision -ne ('a' * 40)) {
                    $bytes = [Text.Encoding]::UTF8.GetBytes([Text.Encoding]::UTF8.GetString($bytes) + "`n" + $fixtureState.revision)
                }
                $stream.Write($bytes, 0, $bytes.Length)
            } finally { $stream.Dispose() }
        }
        $fault = $fixtureState.archiveFault
        if ($fault -eq 'traversal') { $null = $zip.CreateEntry('using-AI-fixture/../../escaped.txt') }
        if ($fault -eq 'absolute') { $null = $zip.CreateEntry('/escaped.txt') }
        if ($fault -eq 'backslash') { $null = $zip.CreateEntry('using-AI-fixture/..\escaped.txt') }
        if ($fault -eq 'root') { $null = $zip.CreateEntry('other-root/file') }
        if ($fault -eq 'duplicate') { $null = $zip.CreateEntry('using-AI-fixture/skills/develop/SKILL.md') }
        if ($fault -eq 'link') {
            $link = $zip.CreateEntry('using-AI-fixture/link')
            $link.ExternalAttributes = -1577123840 # Unix symlink (0xA1FF0000).
        }
    } finally { $zip.Dispose() }
}
function Throw-HttpFailure {
    $exception = [Exception]::new('Do not expose Authorization: Bearer fixture-secret')
    $exception | Add-Member -NotePropertyName Response -NotePropertyValue ([pscustomobject]@{
        StatusCode = $fixtureState.status; Headers = @{ 'X-RateLimit-Remaining' = '0'; 'X-RateLimit-Reset' = '1234567890'; 'Authorization' = 'fixture-secret' }
    })
    $record = [Management.Automation.ErrorRecord]::new($exception, 'Http403', [Management.Automation.ErrorCategory]::InvalidOperation, $null)
    $record.ErrorDetails = [Management.Automation.ErrorDetails]::new('{"message":"API rate limit exceeded; fixture-secret"}')
    throw $record
}
function Assert($Condition, [string]$Message) {
    if (!$Condition) { throw "Assertion failed: $Message" }
}
function Expect-Failure([scriptblock]$Action, [string]$Message) {
    $failed = $false
    try { & $Action | Out-Null } catch { $failed = $_.Exception.Message -like "*$Message*" }
    Assert $failed "Expected failure containing: $Message"
    $fixtureState.passed++
}

try {
    New-Item -ItemType Directory -Path $sandbox | Out-Null
    $env:CODEX_HOME = Join-Path $sandbox 'codex-config'
    $testUser = Join-Path $sandbox 'user'
    New-Item -ItemType Directory -Path $testUser | Out-Null
    $target = Join-Path $testUser '.agents/skills/develop'
    # Execute the README command text with mocked script acquisition and isolated user path.
    $readme = [IO.File]::ReadAllText((Join-Path (Split-Path $PSScriptRoot -Parent) 'README.md'))
    $command = [regex]::Match($readme, '(?m)^& \(\[scriptblock\]::Create\(.*$').Value.Trim()
    Assert (![string]::IsNullOrWhiteSpace($command)) 'README bootstrap command exists'
    & ([scriptblock]::Create($command + ' -UserDirectory $testUser')) | Out-Null
    Assert ($fixtureState.requests -eq 0) 'Default installation does not request API'
    foreach ($file in @('SKILL.md', 'references/develop.md', 'LICENSE')) {
        Assert ((Get-FileHash -LiteralPath (Join-Path $target $file)).Hash -eq (Get-FileHash -LiteralPath (Join-Path $package $file)).Hash) "Installed bytes: $file"
    }
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser 'AGENTS.md'))) 'No project config written'
    $passed++

    $fixtureState.failureStage = 'Bootstrap'
    $urlCount = $fixtureState.urls.Count
    Expect-Failure { & ([scriptblock]::Create($command + ' -UserDirectory $testUser')) } 'Bootstrap download failed'
    Assert ($fixtureState.urls.Count -eq ($urlCount + 1)) 'Bootstrap failure never enters installer'
    $fixtureState.failureStage = ''

    $requestsBefore = $fixtureState.requests
    & $installer -Target codex -UserDirectory $testUser | Out-Null
    Assert ($fixtureState.requests -eq $requestsBefore) 'Repeated install avoids network'
    $passed++
    & $installer -Update -Target codex -UserDirectory $testUser | Out-Null
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser '.agents/using-ai-backups'))) 'Same package avoids replacement'
    $passed++

    $fixtureState.revision = 'b' * 40
    & $installer -Update -Target codex -UserDirectory $testUser | Out-Null
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $testUser '.agents/using-ai-backups'))
    Assert ($backups.Count -eq 1) 'Update retains one backup outside skills'
    Assert (!(Get-Content -LiteralPath (Join-Path $target '.using-ai-install.json') -Raw | ConvertFrom-Json).commit) 'Mutable ref does not invent a commit'
    $passed++

    $before = @{}
    foreach ($file in @('SKILL.md', 'references/develop.md', 'LICENSE', '.using-ai-install.json')) {
        $before[$file] = (Get-FileHash -LiteralPath (Join-Path $target $file)).Hash
    }
    foreach ($status in @(403, 404)) {
        $fixtureState.status = $status
        $fixtureState.failureStage = 'Archive'
        $message = ''
        try { & $installer -Update -Target codex -UserDirectory $testUser | Out-Null } catch { $message = $_.Exception.Message }
        Assert ($message.Contains("HTTP $status")) 'HTTP status reported'
        Assert ($message.Contains('https://codeload.github.com/Jrencat/using-AI/zip/main')) 'Archive URL reported'
        Assert ($message.Contains('X-RateLimit-Remaining=0')) 'Available rate-limit header preserved'
        Assert (!$message.Contains('fixture-secret')) 'Secrets omitted'
        $passed++
    }
    $fixtureState.failureStage = 'transport'
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Archive download failed; HTTP unavailable'
    $fixtureState.failureStage = ''
    foreach ($fault in @('corrupt', 'traversal', 'absolute', 'backslash', 'root', 'duplicate', 'link')) {
        $fixtureState.archiveFault = $fault
        Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Archive extraction failed'
    }
    $fixtureState.archiveFault = ''
    $fixtureState.incomplete = $true
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Incomplete package'
    $fixtureState.incomplete = $false
    foreach ($invalidFile in @('SKILL.md', 'references/develop.md', 'LICENSE', 'metadata')) {
        $fixtureState.invalid = $invalidFile
        Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Package validation failed'
    }
    $fixtureState.invalid = $false
    foreach ($file in $before.Keys) { Assert ((Get-FileHash -LiteralPath (Join-Path $target $file)).Hash -eq $before[$file]) 'Failed updates preserve all installed bytes' }
    # Default, branches, tags and full SHA must work even with API unavailable.
    $fixtureState.failureStage = 'API'
    foreach ($refName in @('main', 'release/test', 'v1.0', ('a' * 40))) {
        $fixtureState.urls = @()
        & $installer -Update -Target codex -Ref $refName -UserDirectory $testUser | Out-Null
        Assert ($fixtureState.urls.Count -eq 1) 'Exactly one archive request, no API'
        Assert ($fixtureState.urls[0] -eq "https://codeload.github.com/Jrencat/using-AI/zip/$([Uri]::EscapeDataString($refName))") 'Requested ref archive'
        $passed++
    }
    Expect-Failure { & $installer -Update -Target codex -Ref abcdef0 -UserDirectory $testUser } 'API ref resolution failed'
    $fixtureState.failureStage = ''
    $fixtureState.urls = @()
    & $installer -Update -Target codex -Ref abcdef0 -UserDirectory $testUser | Out-Null
    Assert ($fixtureState.urls.Count -eq 2) 'Short SHA resolves once then downloads one archive'
    Assert ($fixtureState.urls[1].EndsWith('/' + $fixtureState.revision)) 'Short SHA archive pinned'
    $savedRevision = $fixtureState.revision
    $fixtureState.revision = 'invalid-api-content'
    Expect-Failure { & $installer -Update -Target codex -Ref abcdef0 -UserDirectory $testUser } 'API ref resolution returned invalid content'
    $fixtureState.revision = $savedRevision
    $pinned = 'A281393E9F024B7FC72AAD9AC80ABC8327EAAB78'
    & $installer -Update -Target codex -Ref $pinned -UserDirectory $testUser | Out-Null
    Assert ((Get-Content -LiteralPath (Join-Path $target '.using-ai-install.json') -Raw | ConvertFrom-Json).commit -ceq $pinned.ToLowerInvariant()) 'Full SHA recorded'
    # Convert a valid record to the old schema to exercise migration, then uninstall protection below.
    $recordPath = Join-Path $target '.using-ai-install.json'
    $record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    @{ schema = 1; origin = $record.origin; commit = $record.commit; ref = $pinned; hashes = $record.hashes } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $recordPath -Encoding UTF8
    & $installer -Update -Target codex -Ref $pinned -UserDirectory $testUser | Out-Null
    Assert ((Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json).schema -eq 2) 'Old managed record updated'
    $oldUser = Join-Path $sandbox 'old-schema-uninstall'
    New-Item -ItemType Directory -Path $oldUser | Out-Null
    & $installer -Target manual -Ref $pinned -UserDirectory $oldUser | Out-Null
    $oldRecordPath = Join-Path $oldUser '.using-ai/workflows/develop/.using-ai-install.json'
    $oldRecord = Get-Content -LiteralPath $oldRecordPath -Raw | ConvertFrom-Json
    @{ schema = 1; origin = $oldRecord.origin; commit = $oldRecord.commit; ref = $pinned; hashes = $oldRecord.hashes } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $oldRecordPath -Encoding UTF8
    & $installer -Target manual -Uninstall -UserDirectory $oldUser | Out-Null
    Assert (!(Test-Path -LiteralPath (Split-Path $oldRecordPath -Parent))) 'Old schema uninstall supported'
    $freshUser = Join-Path $sandbox 'failed-fresh-install'
    New-Item -ItemType Directory -Path $freshUser | Out-Null
    $fixtureState.failureStage = 'Archive'
    Expect-Failure { & $installer -Target codex -Ref $pinned -UserDirectory $freshUser } 'Archive download failed'
    Assert (!(Test-Path -LiteralPath (Join-Path $freshUser '.agents/skills/develop'))) 'Failed fresh install never published'
    Assert (@(Get-ChildItem -LiteralPath (Join-Path $freshUser '.agents') -Filter 'using-ai-stage-*').Count -eq 0) 'Failed staging cleaned'
    Assert (@(Get-ChildItem -LiteralPath (Join-Path $freshUser '.agents') -Filter 'using-ai-download-*').Count -eq 0) 'Failed archive cleaned'
    $fixtureState.failureStage = ''

    $savedRecord = [IO.File]::ReadAllBytes($recordPath)
    $badRecord = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    $badRecord.hashes.'LICENSE' = '0' * 64
    $badRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $recordPath -Encoding UTF8
    Expect-Failure { & $installer -Target codex -Update -UserDirectory $testUser } 'Local changes detected'
    [IO.File]::WriteAllBytes($recordPath, $savedRecord)
    $heldLock = Join-Path $testUser '.agents/using-ai-develop.lock'
    Set-Content -LiteralPath $heldLock -Value 'Other installer'
    Expect-Failure { & $installer -Target codex -Update -UserDirectory $testUser } 'Another install may be running'
    Assert (Test-Path -LiteralPath $heldLock) 'Other process lock preserved'
    Remove-Item -LiteralPath $heldLock

    Add-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'Custom content'
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Local changes detected'
    Expect-Failure { & $installer -Uninstall -Target codex -UserDirectory $testUser } 'Local changes detected'
    Copy-Item -LiteralPath (Join-Path $package 'SKILL.md') -Destination (Join-Path $target 'SKILL.md')
    [IO.File]::WriteAllText((Join-Path $target 'SKILL.md'), [IO.File]::ReadAllText((Join-Path $package 'SKILL.md')) + "`n" + $fixtureState.revision, [Text.UTF8Encoding]::new($false))
    Set-Content -LiteralPath (Join-Path $target 'personal.txt') -Value 'Keep'
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Local additions detected'
    Remove-Item -LiteralPath (Join-Path $target 'personal.txt')

    & $installer -Uninstall -Target codex -UserDirectory $testUser | Out-Null
    Assert (!(Test-Path -LiteralPath $target)) 'Uninstall moves Skill outside discovery'
    $passed++
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'No managed installation'
    New-Item -ItemType Directory -Path $target | Out-Null
    Set-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'Unknown origin'
    Expect-Failure { & $installer -Target codex -UserDirectory $testUser } 'Unknown existing Skill'
    Assert ((Get-Content -LiteralPath (Join-Path $target 'SKILL.md') -Raw).Trim() -eq 'Unknown origin') 'Unknown Skill preserved'
    Expect-Failure { & $installer -Target codex -Uninstall -UserDirectory $testUser } 'Unknown existing Skill'

    $legacyUser = Join-Path $sandbox 'legacy-user'
    $legacy = Join-Path $legacyUser '.agents/skills/develop'
    New-Item -ItemType Directory -Path (Split-Path $legacy -Parent) -Force | Out-Null
    Copy-Item -LiteralPath $package -Destination $legacy -Recurse
    Set-Content -LiteralPath (Join-Path $legacy 'personal.txt') -Value 'Keep legacy customization'
    New-Item -ItemType Directory -Path (Join-Path $legacy 'personal-empty') | Out-Null
    $legacyHash = (Get-FileHash -LiteralPath (Join-Path $legacy 'references/develop.md')).Hash
    Expect-Failure { & $installer -Target codex -UserDirectory $legacyUser } 'Unknown existing Skill'
    Expect-Failure { & $installer -Target codex -Update -UserDirectory $legacyUser } 'Unknown existing Skill'
    # A present but invalid manifest must never fall back to legacy recognition.
    Set-Content -LiteralPath (Join-Path $legacy '.using-ai-install.json') -Value '{"schema":0}'
    Expect-Failure { & $installer -Target codex -Uninstall -UserDirectory $legacyUser } 'Unrecognized installation record'
    Remove-Item -LiteralPath (Join-Path $legacy '.using-ai-install.json')
    # Directory junctions work without the Windows symlink privilege.
    $external = Join-Path $sandbox 'external'
    New-Item -ItemType Directory -Path $external | Out-Null
    Set-Content -LiteralPath (Join-Path $external 'keep.txt') -Value 'Untouched'
    $junction = Join-Path $legacy 'linked'
    New-Item -ItemType Junction -Path $junction -Target $external | Out-Null
    try {
        Expect-Failure { & $installer -Target codex -Uninstall -UserDirectory $legacyUser } 'Linked content detected'
        Assert ((Get-Content -LiteralPath (Join-Path $external 'keep.txt')).Trim() -eq 'Untouched') 'Linked external data preserved'
    }
    finally { [IO.Directory]::Delete($junction) }
    $messages = @(& $installer -Target codex -Uninstall -UserDirectory $legacyUser)
    Assert (!(Test-Path -LiteralPath $legacy)) 'Legacy removed from discovery'
    $legacyBackups = @(Get-ChildItem -LiteralPath (Join-Path $legacyUser '.agents/using-ai-backups'))
    Assert ($legacyBackups.Count -eq 1) 'Legacy backup outside skills'
    $legacyBackup = $legacyBackups[0].FullName
    Assert (($messages -join "`n").Contains($legacyBackup)) 'Backup path reported'
    Assert ((Get-Content -LiteralPath (Join-Path $legacyBackup 'personal.txt')).Trim() -eq 'Keep legacy customization') 'Legacy personal file preserved'
    Assert (Test-Path -LiteralPath (Join-Path $legacyBackup 'personal-empty') -PathType Container) 'Legacy empty directory preserved'
    Assert ((Get-FileHash -LiteralPath (Join-Path $legacyBackup 'references/develop.md')).Hash -eq $legacyHash) 'Legacy rules preserved byte for byte'
    $passed++
    New-Item -ItemType Junction -Path $legacy -Target $external | Out-Null
    try { Expect-Failure { & $installer -Target codex -Uninstall -UserDirectory $legacyUser } 'Not a plain directory' }
    finally { [IO.Directory]::Delete($legacy) }
    $linkedUser = Join-Path $sandbox 'linked-user'
    New-Item -ItemType Directory -Path $linkedUser | Out-Null
    $linkedAgents = Join-Path $linkedUser '.agents'
    New-Item -ItemType Junction -Path $linkedAgents -Target $external | Out-Null
    try { Expect-Failure { & $installer -Target codex -Uninstall -UserDirectory $linkedUser } 'Not a plain directory' }
    finally { [IO.Directory]::Delete($linkedAgents) }
    Assert (!(Test-Path -LiteralPath (Join-Path $external 'skills'))) 'Linked ancestor never written'

    foreach ($hostTarget in @('manual', 'claude')) {
        $hostUser = Join-Path $sandbox $hostTarget
        New-Item -ItemType Directory -Path $hostUser | Out-Null
        Set-Content -LiteralPath (Join-Path $hostUser 'personal.txt') -Value 'Keep'
        if ($hostTarget -eq 'manual') { & $installer -UserDirectory $hostUser | Out-Null }
        else { & $installer -Target $hostTarget -UserDirectory $hostUser | Out-Null }
        $relativePath = if ($hostTarget -eq 'manual') { '.using-ai/workflows/develop' } else { '.claude/skills/develop' }
        $hostPath = Join-Path $hostUser $relativePath
        Assert (Test-Path -LiteralPath (Join-Path $hostPath 'references/develop.md')) 'Non-Codex package installed'
        New-Item -ItemType Directory -Path (Join-Path $hostPath 'personal') | Out-Null
        Expect-Failure { & $installer -Target $hostTarget -Uninstall -UserDirectory $hostUser } 'Local additions detected'
        Remove-Item -LiteralPath (Join-Path $hostPath 'personal')
        $fixtureState.revision = 'c' * 40
        & $installer -Target $hostTarget -Update -UserDirectory $hostUser | Out-Null
        if ($hostTarget -eq 'claude') {
            $commands = Join-Path $hostUser '.claude/commands'
            New-Item -ItemType Directory -Path $commands | Out-Null
            Set-Content -LiteralPath (Join-Path $commands 'develop.md') -Value 'Keep command'
        }
        & $installer -Target $hostTarget -Uninstall -UserDirectory $hostUser | Out-Null
        Assert (!(Test-Path -LiteralPath $hostPath)) 'Non-Codex uninstall'
        if ($hostTarget -eq 'claude') {
            Assert ((Get-Content -LiteralPath (Join-Path $commands 'develop.md')).Trim() -eq 'Keep command') 'Uninstall preserves conflicting command'
        }
        Assert ((Get-Content -LiteralPath (Join-Path $hostUser 'personal.txt')).Trim() -eq 'Keep') 'Unrelated user file preserved'
        $passed++
    }
    Expect-Failure { & $installer -Target unknown -UserDirectory $sandbox } 'ValidateSet'
    $overrideUser = Join-Path $sandbox 'override-user'
    New-Item -ItemType Directory -Path $overrideUser | Out-Null
    $env:CLAUDE_CONFIG_DIR = Join-Path $sandbox 'override-config'
    & $installer -Target claude -UserDirectory $overrideUser | Out-Null
    Assert (Test-Path -LiteralPath (Join-Path $env:CLAUDE_CONFIG_DIR 'skills/develop/SKILL.md')) 'CLAUDE_CONFIG_DIR respected'
    & $installer -Target claude -Uninstall -UserDirectory $overrideUser | Out-Null
    $env:CLAUDE_CONFIG_DIR = $null
    $commandUser = Join-Path $sandbox 'command-user'
    New-Item -ItemType Directory -Path (Join-Path $commandUser '.claude/commands') -Force | Out-Null
    $commandPath = Join-Path $commandUser '.claude/commands/develop.md'
    Set-Content -LiteralPath $commandPath -Value 'Custom command'
    Expect-Failure { & $installer -Target claude -UserDirectory $commandUser } 'Existing /develop command'
    Assert ((Get-Content -LiteralPath $commandPath).Trim() -eq 'Custom command') 'Existing command preserved'

    $otherUser = Join-Path $sandbox 'other-user'
    New-Item -ItemType Directory -Path (Join-Path $otherUser '.codex/skills/develop') -Force | Out-Null
    Expect-Failure { & $installer -Target codex -UserDirectory $otherUser } 'Another user-level develop Skill'
    Assert (@(Get-ChildItem -LiteralPath (Join-Path $testUser '.agents') -Filter 'using-ai-stage-*').Count -eq 0) 'Staging cleaned'
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser '.agents/using-ai-develop.lock'))) 'Lock released'
    Write-Output "PASS: $($passed + $fixtureState.passed) isolated installer checks; network mocked, real user configuration untouched."
}
finally {
    $env:CODEX_HOME = $savedCodexHome
    $env:CLAUDE_CONFIG_DIR = $savedClaudeConfig
    if ((Test-Path -LiteralPath $sandbox) -and $sandbox.StartsWith([IO.Path]::GetTempPath())) {
        Remove-Item -LiteralPath $sandbox -Recurse -Force
    }
}
