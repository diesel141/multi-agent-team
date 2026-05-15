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
NO_ATTACH=0
for arg in "$@"; do
  [ "$arg" = "--no-attach" ] && NO_ATTACH=1
done

# キュークリア（オプション）
if [ "$1" = "-c" ]; then
  echo "[init] キューをクリア"
  rm -rf queue/
fi

# キュー・ログディレクトリ初期化
mkdir -p queue/inbox queue/reports logs
for agent in pm dev1 dev2 dev3; do
  touch "queue/inbox/${agent}.yaml"
done
touch queue/reports/dev1.yaml queue/reports/dev2.yaml queue/reports/dev3.yaml
touch queue/you_to_pm.yaml

# tmux セッション既存確認
if tmux has-session -t team 2>/dev/null; then
  if [ "$NO_ATTACH" = "1" ]; then
    echo "[info] team セッションが既に存在します。--no-attach のためスキップ。"
    exit 0
  fi
  echo "[info] team セッションが既に存在します。アタッチします。"
  if [ -n "$TMUX" ]; then
    tmux switch-client -t team
  else
    exec tmux attach-session -t team
  fi
  exit 0
fi

# 4 ペイン構成: pm / dev1 / dev2 / dev3
tmux new-session -d -s team -n agents
tmux split-window -h -t team:0
tmux split-window -v -t team:0.1
tmux split-window -v -t team:0.0
tmux select-layout -t team:0 tiled

# pane index → ペルソナ名と instructions ファイルのマッピング
persona_for() {
  case "$1" in
    0) echo "藤宮 詩織 (pm)" ;;
    1) echo "黒崎 颯真 (dev1)" ;;
    2) echo "緑川 啓介 (dev2)" ;;
    3) echo "茜野 真理 (dev3)" ;;
  esac
}

instr_for() {
  case "$1" in
    0) echo "instructions/pm.md" ;;
    *) echo "instructions/dev.md" ;;
  esac
}

# 各ペインで claude を起動
# ペイン 0 (pm): bash 経由で claude
# ペイン 1-3 (dev): glm-env.sh で環境変数を設定してから claude を起動
# （claude-glm は PS Function のため bash から呼べない → env vars を直接設定）
BASH_EXE="C:/Program Files/Git/bin/bash.exe"
GLM_ENV="$REPO_ROOT/scripts/glm-env.sh"
tmux send-keys -t team:0.0 "& '$BASH_EXE' --login -c 'cd $REPO_ROOT && claude --dangerously-skip-permissions'" Enter
for i in 1 2 3; do
  tmux send-keys -t team:0.$i "& '$BASH_EXE' --login -c 'cd $REPO_ROOT && source $GLM_ENV && claude --dangerously-skip-permissions'" Enter
done

# claude 起動待機（psmux は capture-pane で ❯ を検出できないため固定 sleep）
echo "[init] claude 起動待機 (5 秒)..."
sleep 5

# 各ペインに init プロンプトを送信
# 長文 + Enter を 1 回の send-keys で送ると Enter が消化されないことがあるため分離
for i in 0 1 2 3; do
  persona=$(persona_for $i)
  instr=$(instr_for $i)
  tmux send-keys -t team:0.$i "あなたは Multi-Agent Team の '${persona}' です。${instr} を Read してから指示待ちしてください。"
  sleep 1
  tmux send-keys -t team:0.$i Enter
done

echo "[ok] team セッション起動完了 (pm + dev1 + dev2 + dev3)"

# queue ウォッチャーをバックグラウンドで起動
# yaml 書き込みを検知して対象ペインに inbox を自動送信する
WIN_QUEUE_DIR=$(cygpath -w "$REPO_ROOT/queue" 2>/dev/null || echo "$REPO_ROOT\\queue")
pwsh -NoProfile -NonInteractive \
  -File "$REPO_ROOT/scripts/watch-queue.ps1" \
  -QueueDir "$WIN_QUEUE_DIR" \
  -Session team \
  > "$REPO_ROOT/logs/watch-queue.log" 2>&1 &
echo "[ok] queue ウォッチャー起動 (PID: $! / ログ: logs/watch-queue.log)"

echo "アタッチ: tmux attach-session -t team"
echo "終了: tmux kill-session -t team"

if [ "$NO_ATTACH" = "1" ]; then
  echo "[ok] --no-attach: 起動完了。'tmux a' で接続してください。"
  exit 0
fi
if [ -n "$TMUX" ]; then
  tmux switch-client -t team
else
  exec tmux attach-session -t team
fi
