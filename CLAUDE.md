# CLAUDE.md

このリポジトリは [yohey-w/multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun) の思想を採用した **Multi-Agent ADD（Agent-Driven Development）チーム**環境です。

## 階層

ユーザー（you）→ PM 兼 Designer（pm）→ Developer 兼 Tester（dev）× 3

- **pm**: タスク分解 / UX 仕様判断 / dev への分配 / 受入レビュー
- **dev1 / dev2 / dev3**: 実装 + 自己テスト / pm へ完了報告

## 起動手順（WSL2 必須）

1. `install.bat` を **管理者権限** で実行（初回のみ / WSL2 自動セットアップ）
   - Windows コマンドプロンプトから「管理者として実行」（bash からは起動不可）
2. WSL2 内で:
   ```bash
   cd /mnt/c/_vps/git/multi-agent-team
   ./scripts/start.sh
   ```
3. tmux セッション `team` が 4 ペイン（pm / dev1 / dev2 / dev3）で起動

## 通信プロトコル

YAML キュー方式（shogun 思想）:

| ファイル | 用途 |
|---|---|
| `queue/you_to_pm.yaml` | ユーザー → PM 指示 |
| `queue/pm_to_dev.yaml` | PM → dev 一括指示（複数 dev へ並列分配） |
| `queue/inbox/<agent>.yaml` | エージェント別メールボックス |
| `queue/reports/<agent>.yaml` | dev → PM 完了報告 |

- **通知**: `tmux send-keys "inbox" Enter`（短い合図のみ。本文は YAML）
- **受信**: `inotifywait` でファイル変更検知（ポーリング 0）
- **書き込み**: `flock` で排他ロック

実装スクリプトは `shogun/scripts/inbox_write.sh` / `shogun/scripts/inbox_watcher.sh` を参考（submodule で参照可能）。

## 個別タスクのコード

新規プロジェクトはサブリポを切る。既存（`ai_training_for_rjc` / `mat-board-watcher`）はそのまま利用。本リポにアプリコードは置かない（運用ハブ）。

## 言語

- ユーザー対話・YAML メッセージ・コミットメッセージ: 日本語
- 技術用語（API 名・コマンド・識別子）: 英字のまま
- コードコメント: 必要なら日本語、不要なら書かない

## 既存資産

- `archive/pre-shogun-reset` ブランチに旧運用資産（旧 CLAUDE.md / docs/personas / docs/adr 9 本 / docs/templates / Notion 通信）を退避済み
- `docs/history/` は資産として保持
- `shogun/`（submodule）は学習・参考リソースとして残置

## Git 運用

- `main`: リリース済み
- `development`: 統合（PR base）
- `feature/*` / `fix/*` / `chore/*` / `docs/*`: development へ PR
