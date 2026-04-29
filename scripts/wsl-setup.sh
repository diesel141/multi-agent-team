#!/usr/bin/env bash
# WSL2 Ubuntu 環境への Multi-Agent Team セットアップスクリプト
# 使用方法: bash scripts/wsl-setup.sh
#
# 実行内容:
#   1. apt update + 必要パッケージ (tmux / inotify-tools / util-linux / python3 / curl)
#   2. Node.js LTS (NodeSource) + claude CLI (npm)
#   3. 完了後の次の手順を表示

set -e

GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

log_info()    { echo -e "${YELLOW}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error()   { echo -e "${RED}[ERR]${NC} $1"; }

if [ -z "$BASH_VERSION" ]; then
  log_error "bash で実行してください: bash scripts/wsl-setup.sh"
  exit 1
fi

if ! grep -qi "ubuntu" /etc/os-release 2>/dev/null; then
  log_error "Ubuntu 以外のディストロでは未検証です（Docker Desktop の WSL2 等は不可）"
  cat /etc/os-release 2>/dev/null | head -3
  exit 1
fi

log_info "[1/3] apt 更新 + 必要パッケージ導入..."
sudo apt-get update -qq
sudo apt-get install -y -qq tmux inotify-tools util-linux python3 python3-venv curl ca-certificates
log_success "依存パッケージ OK"

log_info "[2/3] Node.js LTS + claude CLI 導入..."
if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - >/dev/null 2>&1
  sudo apt-get install -y -qq nodejs
fi
log_success "Node.js: $(node --version)"

if ! command -v claude >/dev/null 2>&1; then
  sudo npm install -g @anthropic-ai/claude-code 2>&1 | tail -3
fi
log_success "claude CLI: $(claude --version 2>/dev/null || echo 'インストール直後')"

log_info "[3/3] scripts/start.sh 実行権限付与..."
chmod +x "$(dirname "$0")/start.sh" 2>/dev/null || true
log_success "セットアップ完了"

cat <<EOF

${GREEN}=====================================================${NC}
  セットアップ完了。次のコマンドを実行してください:

  ${YELLOW}claude --dangerously-skip-permissions${NC}    # 初回認証 (ブラウザ開く)
                                              # → "say hi" 等で動作確認 → /quit
  ${YELLOW}./scripts/start.sh${NC}                       # tmux 4 ペイン起動

${GREEN}=====================================================${NC}
EOF
