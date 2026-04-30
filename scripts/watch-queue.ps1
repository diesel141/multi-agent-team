#!/usr/bin/env pwsh
# queue/ ディレクトリを FileSystemWatcher で監視し、
# yaml 書き込みを検知したら対象ペインに "inbox" を送信する
#
# 起動: pwsh -NoProfile -NonInteractive -File scripts/watch-queue.ps1
#        -QueueDir <Windowsパス> -Session team

param(
    [string]$QueueDir = "C:\_vps\git\multi-agent-team\queue",
    [string]$Session  = "team"
)

# pane マッピング
$paneMap = @{
    "reports"      = "$Session`:0.0"   # dev が report を書いた → PM へ
    "inbox/pm"     = "$Session`:0.0"   # PM inbox 更新 → PM へ
    "inbox/dev1"   = "$Session`:0.1"   # dev1 inbox 更新 → dev1 へ
    "inbox/dev2"   = "$Session`:0.2"   # dev2 inbox 更新 → dev2 へ
    "inbox/dev3"   = "$Session`:0.3"   # dev3 inbox 更新 → dev3 へ
}

# デバウンス: 同一ペインへの連続送信を 3 秒以内は無視
$lastSent = @{}

function Resolve-Pane([string]$fullPath) {
    $rel = $fullPath.Replace($QueueDir, "").TrimStart("\").Replace("\", "/")
    if ($rel -match "^reports/")            { return $paneMap["reports"] }
    if ($rel -match "^inbox/pm\.yaml$")     { return $paneMap["inbox/pm"] }
    if ($rel -match "^inbox/dev1\.yaml$")   { return $paneMap["inbox/dev1"] }
    if ($rel -match "^inbox/dev2\.yaml$")   { return $paneMap["inbox/dev2"] }
    if ($rel -match "^inbox/dev3\.yaml$")   { return $paneMap["inbox/dev3"] }
    return $null
}

$watcher = [System.IO.FileSystemWatcher]::new($QueueDir)
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter          = [System.IO.NotifyFilters]::LastWrite
$watcher.Filter                = "*.yaml"
$watcher.EnableRaisingEvents   = $true

$handler = {
    $path = $Event.SourceEventArgs.FullPath
    $data = $Event.MessageData

    $pane = Resolve-Pane $path
    if (-not $pane) { return }

    $now  = [DateTime]::UtcNow
    $last = $data.LastSent[$pane]
    if ($last -and ($now - $last).TotalSeconds -lt 3) { return }
    $data.LastSent[$pane] = $now

    $rel = $path.Replace($data.QueueDir, "").TrimStart("\")
    Write-Host "[watch-queue] $rel → $pane"
    & tmux send-keys -t $pane "inbox" Enter 2>$null
}

$state = [PSCustomObject]@{ QueueDir = $QueueDir; LastSent = $lastSent }
Register-ObjectEvent $watcher Changed -Action $handler -MessageData $state | Out-Null
Register-ObjectEvent $watcher Created -Action $handler -MessageData $state | Out-Null

Write-Host "[watch-queue] 監視開始: $QueueDir (session=$Session)"

while ($true) {
    & tmux has-session -t $Session 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[watch-queue] $Session セッション終了 → 監視停止"
        break
    }
    Start-Sleep -Seconds 5
}
