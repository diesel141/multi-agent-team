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
tmux select-layout -t team:0 tiled

# pane index → role の直接マッピング
# psmux は @user-option / show-option 未対応のため、添字で固定
role_for() {
  case "$1" in
    0) echo "pm" ;;
    1) echo "dev1" ;;
    2) echo "dev2" ;;
    3) echo "dev3" ;;
  esac
}

instr_for() {
  case "$1" in
    pm) echo "instructions/pm.md" ;;
    dev*) echo "instructions/dev.md" ;;
  esac
}

# 各ペインで claude を起動
for i in 0 1 2 3; do
  tmux send-keys -t team:0.$i "cd $REPO_ROOT && claude --dangerously-skip-permissions" Enter
done

# 各ペインで claude プロンプト '❯' が出るまで待機（fixed sleep ではなくポーリング）
for i in 0 1 2 3; do
  role=$(role_for $i)
  echo "[init] pane $i ($role): claude 起動待機..."
  ready=0
  for attempt in $(seq 1 30); do
    if tmux capture-pane -t team:0.$i -p | grep -q "❯"; then
      ready=1
      break
    fi
    sleep 2
  done
  if [ "$ready" -ne 1 ]; then
    echo "[warn] pane $i ($role): 60 秒以内に claude プロンプトが確認できませんでした。手動で確認してください。"
  fi
done

# 各ペインに init プロンプトを送信
# 長文 + Enter を 1 回の send-keys で送ると Enter が消化されないことがあるため分離
for i in 0 1 2 3; do
  role=$(role_for $i)
  instr=$(instr_for "$role")
  tmux send-keys -t team:0.$i "あなたは Multi-Agent Team の '${role}' です。${instr} を Read してから指示待ちしてください。"
  sleep 1
  tmux send-keys -t team:0.$i Enter
done

echo "[ok] team セッション起動完了 (pm + dev1 + dev2 + dev3)"
echo "アタッチ: tmux attach-session -t team"
echo "終了: tmux kill-session -t team"

tmux attach-session -t team
