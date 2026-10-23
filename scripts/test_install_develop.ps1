# Isolated installer checks using local package fixtures; no network or real user writes.
$ErrorActionPreference = 'Stop'
$installer = Join-Path $PSScriptRoot 'install-develop.ps1'
$package = Join-Path (Split-Path $PSScriptRoot -Parent) 'skills/develop'
$sandbox = Join-Path ([IO.Path]::GetTempPath()) ('using-ai-install-test-' + [guid]::NewGuid().ToString('N'))
$savedCodexHome = $env:CODEX_HOME
$fixtureState = @{ revision = 'a' * 40; networkFailure = $false; incomplete = $false; requests = 0; passed = 0 }
$passed = 0

function codex { }
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
    & ([scriptblock]::Create((Get-Content -LiteralPath $installer -Raw))) -UserDirectory $testUser | Out-Null
    foreach ($file in @('SKILL.md', 'references/develop.md', 'LICENSE')) {
        Assert ((Get-FileHash -LiteralPath (Join-Path $target $file)).Hash -eq (Get-FileHash -LiteralPath (Join-Path $package $file)).Hash) "Installed bytes: $file"
    }
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser 'AGENTS.md'))) 'No project config written'
    $passed++

    $requestsBefore = $fixtureState.requests
    & $installer -UserDirectory $testUser | Out-Null
    Assert ($fixtureState.requests -eq $requestsBefore) 'Repeated install avoids network'
    $passed++
    & $installer -Update -UserDirectory $testUser | Out-Null
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser '.agents/using-ai-backups'))) 'Same commit avoids replacement'
    $passed++

    $fixtureState.revision = 'b' * 40
    & $installer -Update -UserDirectory $testUser | Out-Null
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $testUser '.agents/using-ai-backups'))
    Assert ($backups.Count -eq 1) 'Update retains one backup outside skills'
    Assert ((Get-Content -LiteralPath (Join-Path $target '.using-ai-install.json') -Raw | ConvertFrom-Json).commit -eq $fixtureState.revision) 'Updated commit'
    $passed++

    $fixtureState.networkFailure = $true
    Expect-Failure { & $installer -Update -UserDirectory $testUser } 'GitHub download failed'
    $fixtureState.networkFailure = $false
    Assert (Test-Path -LiteralPath (Join-Path $target 'SKILL.md')) 'Download failure preserves install'
    $fixtureState.incomplete = $true
    Expect-Failure { & $installer -Update -UserDirectory $testUser } 'Incomplete package'
    $fixtureState.incomplete = $false

    Add-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'Custom content'
    Expect-Failure { & $installer -Update -UserDirectory $testUser } 'Local changes detected'
    Expect-Failure { & $installer -Uninstall -UserDirectory $testUser } 'Local changes detected'
    Copy-Item -LiteralPath (Join-Path $package 'SKILL.md') -Destination (Join-Path $target 'SKILL.md')
    Set-Content -LiteralPath (Join-Path $target 'personal.txt') -Value 'Keep'
    Expect-Failure { & $installer -Update -UserDirectory $testUser } 'Local additions detected'
    Remove-Item -LiteralPath (Join-Path $target 'personal.txt')

    & $installer -Uninstall -UserDirectory $testUser | Out-Null
    Assert (!(Test-Path -LiteralPath $target)) 'Uninstall moves Skill outside discovery'
    $passed++
    Expect-Failure { & $installer -Update -UserDirectory $testUser } 'No managed installation'
    New-Item -ItemType Directory -Path $target | Out-Null
    Set-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'Unknown origin'
    Expect-Failure { & $installer -UserDirectory $testUser } 'Unknown existing Skill'
    Assert ((Get-Content -LiteralPath (Join-Path $target 'SKILL.md') -Raw).Trim() -eq 'Unknown origin') 'Unknown Skill preserved'

    $otherUser = Join-Path $sandbox 'other-user'
    New-Item -ItemType Directory -Path (Join-Path $otherUser '.codex/skills/develop') -Force | Out-Null
    Expect-Failure { & $installer -UserDirectory $otherUser } 'Another user-level develop Skill'
    Assert (@(Get-ChildItem -LiteralPath (Join-Path $testUser '.agents') -Filter 'using-ai-stage-*').Count -eq 0) 'Staging cleaned'
    Assert (!(Test-Path -LiteralPath (Join-Path $testUser '.agents/using-ai-develop.lock'))) 'Lock released'
    Write-Output "PASS: $($passed + $fixtureState.passed) isolated installer checks; network mocked, real user configuration untouched."
}
finally {
    $env:CODEX_HOME = $savedCodexHome
    if ((Test-Path -LiteralPath $sandbox) -and $sandbox.StartsWith([IO.Path]::GetTempPath())) {
        Remove-Item -LiteralPath $sandbox -Recurse -Force
    }
}
