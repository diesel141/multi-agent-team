@echo off
chcp 65001 >nul 2>&1
title Multi-Agent Team Installer

echo.
echo   +============================================================+
echo   ^|  Multi-Agent Team - WSL2 Installer                         ^|
echo   ^|  ユーザー(you) → PM(pm) → Developer(dev) × 3                ^|
echo   +============================================================+
echo.

REM ===== Step 1: Check/Install WSL2 =====
echo   [1/3] WSL2 確認中...

wsl.exe --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo   WSL2 が見つかりません。自動インストール中...
    echo.
    net session >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo   +============================================================+
        echo   ^|  [WARN] 管理者権限が必要です                               ^|
        echo   +============================================================+
        echo.
        echo   install.bat を右クリック → 「管理者として実行」してください。
        echo.
        pause
        exit /b 1
    )
    echo   Installing WSL2...
    powershell -Command "wsl --install --no-launch"
    echo.
    echo   +============================================================+
    echo   ^|  [!] 再起動が必要です                                      ^|
    echo   +============================================================+
    echo.
    echo   再起動後、もう一度 install.bat を実行してください。
    echo.
    pause
    exit /b 0
)
echo   WSL2 OK
echo.

REM ===== Step 2: Verify dependencies in WSL2 =====
echo   [2/3] WSL2 内の依存パッケージ確認中...
wsl.exe -e bash -c "command -v tmux && command -v inotifywait && command -v flock && command -v python3" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   依存パッケージインストール中（tmux, inotify-tools, util-linux, python3）...
    wsl.exe -e bash -c "sudo apt-get update && sudo apt-get install -y tmux inotify-tools util-linux python3 python3-venv"
)
echo   依存パッケージ OK
echo.

REM ===== Step 3: Hint next steps =====
echo   [3/3] セットアップ完了
echo.
echo   +============================================================+
echo   ^|  次の手順（WSL2 内で実行）:                                ^|
echo   ^|                                                            ^|
echo   ^|    cd /mnt/c/_vps/git/multi-agent-team                     ^|
echo   ^|    claude --dangerously-skip-permissions  (初回認証のみ)  ^|
echo   ^|    ./scripts/start.sh                                      ^|
echo   +============================================================+
echo.
pause
