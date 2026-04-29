# CLAUDE.md

このリポジトリは [yohey-w/multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun) を採用した Multi-Agent ADD（Agent-Driven Development）チーム環境です。

## 階層

上様（You）→ 将軍（Shogun）→ 家老（Karo）→ 足軽（Ashigaru）× 7 + 軍師（Gunshi）× 1

## 起動手順（WSL2 必須）

1. `install.bat` を **管理者権限** で実行（初回のみ / WSL2 自動セットアップ）
2. WSL2 内で:
   ```bash
   cd /mnt/c/_vps/git/multi-agent-team/shogun
   ./first_setup.sh                       # 初回のみ
   source ~/.bashrc
   claude --dangerously-skip-permissions  # 初回認証のみ
   ./shutsujin_departure.sh               # 毎日の起動
   ```
3. tmux: `shogun` セッション 1 ペイン + `multiagent` セッション 9 ペイン

## 通信プロトコル

shogun の YAML キュー方式:

- `shogun/queue/<from>_to_<to>.yaml` — 指示
- `shogun/queue/inbox/<agent>.yaml` — メールボックス
- `shogun/queue/reports/<agent>.yaml` — 完了報告
- 通知: `tmux send-keys "inbox3" Enter`（短い合図のみ。本文は YAML）
- 受信: `inotifywait` でファイルイベント検知

詳細は `shogun/CLAUDE.md` および `shogun/instructions/`（shogun.md / karo.md / ashigaru.md / gunshi.md）を参照。

## 言語

- ユーザー対話・YAML メッセージ・コミットメッセージ: 日本語
- 技術用語（API 名・コマンド・識別子）: 英字のまま
- コードコメント: 必要なら日本語、不要なら書かない

## 個別タスクのコード

新規プロジェクトはサブリポを切る。既存プロジェクト（`ai_training_for_rjc`, `mat-board-watcher` 等）はそのまま利用。本リポにアプリコードは置かない（運用ハブ）。

## 既存資産（旧運用）

`archive/pre-shogun-reset` ブランチに旧運用の全資産（旧 CLAUDE.md / docs/personas / docs/adr 9 本 / docs/templates / Notion 通信プロトコル等）を退避済み。歴史化メモは `docs/history/` にそのまま保持。

## Git 運用

- `main`: リリース済み・本番安定版
- `development`: 統合ブランチ（PR base）
- `feature/*` / `fix/*` / `chore/*` / `docs/*`: development へ PR

## 不明点

ユーザー判断が要るときは黙って進めず簡潔に質問。
