# Isolated installer checks using local package fixtures; no network or real user writes.
$ErrorActionPreference = 'Stop'
$installer = Join-Path $PSScriptRoot 'install-develop.ps1'
$package = Join-Path (Split-Path $PSScriptRoot -Parent) 'skills/develop'
$sandbox = Join-Path ([IO.Path]::GetTempPath()) ('using-ai-install-test-' + [guid]::NewGuid().ToString('N'))
$savedCodexHome = $env:CODEX_HOME
$savedClaudeConfig = $env:CLAUDE_CONFIG_DIR
$env:CLAUDE_CONFIG_DIR = $null
$fixtureState = @{ revision = 'a' * 40; networkFailure = $false; incomplete = $false; requests = 0; passed = 0 }
$passed = 0


function Invoke-RestMethod {
    param($Uri, $Headers, $TimeoutSec)
    $fixtureState.requests++
    if ($fixtureState.networkFailure) { throw 'Simulated network failure' }
    return @{ sha = $fixtureState.revision }
}
function Invoke-WebRequest {
    param([switch]$UseBasicParsing, $Uri, $OutFile, $TimeoutSec)
    $relative = ($Uri -split '/skills/develop/', 2)[1]
    if ($fixtureState.incomplete -and $relative -eq 'LICENSE') { return }
    Copy-Item -LiteralPath (Join-Path $package $relative) -Destination $OutFile
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
    # Exercise the README's scriptblock invocation without fetching executable code.
    & ([scriptblock]::Create((Get-Content -LiteralPath $installer -Raw))) -Target codex -UserDirectory $testUser | Out-Null
    foreach ($file in @('SKILL.md', 'references/develop.md', 'LICENSE')) {
        Assert ((Get-FileHash -LiteralPath (Join-Path $target $file)).Hash -eq (Get-FileHash -LiteralPath (Join-Path $package $file)).Hash) "Installed bytes: $file"
    }
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser 'AGENTS.md'))) 'No project config written'
    $passed++

    $requestsBefore = $fixtureState.requests
    & $installer -Target codex -UserDirectory $testUser | Out-Null
    Assert ($fixtureState.requests -eq $requestsBefore) 'Repeated install avoids network'
    $passed++
    & $installer -Update -Target codex -UserDirectory $testUser | Out-Null
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser '.agents/using-ai-backups'))) 'Same commit avoids replacement'
    $passed++

    $fixtureState.revision = 'b' * 40
    & $installer -Update -Target codex -UserDirectory $testUser | Out-Null
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $testUser '.agents/using-ai-backups'))
    Assert ($backups.Count -eq 1) 'Update retains one backup outside skills'
    Assert ((Get-Content -LiteralPath (Join-Path $target '.using-ai-install.json') -Raw | ConvertFrom-Json).commit -eq $fixtureState.revision) 'Updated commit'
    $passed++

    $fixtureState.networkFailure = $true
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'GitHub download failed'
    $fixtureState.networkFailure = $false
    Assert (Test-Path -LiteralPath (Join-Path $target 'SKILL.md')) 'Download failure preserves install'
    $fixtureState.incomplete = $true
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Incomplete package'
    $fixtureState.incomplete = $false

    Add-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'Custom content'
    Expect-Failure { & $installer -Update -Target codex -UserDirectory $testUser } 'Local changes detected'
    Expect-Failure { & $installer -Uninstall -Target codex -UserDirectory $testUser } 'Local changes detected'
    Copy-Item -LiteralPath (Join-Path $package 'SKILL.md') -Destination (Join-Path $target 'SKILL.md')
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
