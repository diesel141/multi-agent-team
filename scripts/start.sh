#!/usr/bin/env bash
# Multi-Agent Team 起動スクリプト
# tmux セッション 'team' を 4 ペイン (pm / dev1 / dev2 / dev3) で起動
#
# 使用方法:
#   ./scripts/start.sh           # 全エージェント起動
#   ./scripts/start.sh -c        # キューをクリアして起動

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# キュークリア（オプション）
if [ "$1" = "-c" ]; then
  echo "[init] キューをクリア"
  rm -rf queue/
fi

# キューディレクトリ初期化
mkdir -p queue/inbox queue/reports
for agent in pm dev1 dev2 dev3; do
  touch "queue/inbox/${agent}.yaml"
done
touch queue/reports/dev1.yaml queue/reports/dev2.yaml queue/reports/dev3.yaml
touch queue/you_to_pm.yaml

# tmux セッション既存確認
if tmux has-session -t team 2>/dev/null; then
  echo "[info] team セッションが既に存在します。アタッチします。"
  tmux attach-session -t team
  exit 0
fi

# 4 ペイン構成: pm / dev1 / dev2 / dev3
tmux new-session -d -s team -n agents
tmux split-window -h -t team:0
tmux split-window -v -t team:0.1
tmux split-window -v -t team:0.0

# ペイン 0 = pm / 1 = dev1 / 2 = dev2 / 3 = dev3 ※レイアウト依存
# 配置を確実にするため改めて指定
tmux select-layout -t team:0 tiled

# エージェント識別子を tmux user option に設定（ペイン順序非依存）
tmux set-option -t team:0.0 -p @agent_id pm
tmux set-option -t team:0.1 -p @agent_id dev1
tmux set-option -t team:0.2 -p @agent_id dev2
tmux set-option -t team:0.3 -p @agent_id dev3

# 各ペインで claude を自動起動
for i in 0 1 2 3; do
  agent_id=$(tmux show-option -t team:0.$i -pv @agent_id)
  case "$agent_id" in
    pm)   instr="instructions/pm.md" ;;
    dev*) instr="instructions/dev.md" ;;
  esac
  tmux send-keys -t team:0.$i "cd $REPO_ROOT && claude --dangerously-skip-permissions" Enter
  sleep 1
  tmux send-keys -t team:0.$i "あなたは Multi-Agent Team の '${agent_id}' です。${instr} を Read してから指示待ちしてください。" Enter
done

echo "[ok] team セッション起動完了 (pm + dev1 + dev2 + dev3)"
echo "アタッチ: tmux attach-session -t team"
echo "終了: tmux kill-session -t team"

tmux attach-session -t team
