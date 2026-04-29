# CLAUDE.md

[yohey-w/multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun) の YAML キュー + マルチペイン + ファイル監視思想を踏襲した、本プロダクト独自の **Multi-Agent ADD（Agent-Driven Development）チーム**環境です。Windows ネイティブで psmux を使い、WSL2 不要。

## 階層

ユーザー（you）→ PM 兼 Designer（pm）→ Developer 兼 Tester（dev）× 3

- **pm**: タスク分解 / UX 仕様判断 / dev への分配 / 受入レビュー
- **dev1 / dev2 / dev3**: 実装 + 自己テスト / pm へ完了報告

## 起動環境

- **マルチプレクサ**: psmux 3.3.3+（Windows ネイティブ Rust 実装 / `winget install psmux`）
- **シェル**: bash（Git for Windows / MSYS2 等）
- **Claude Code**: Windows ネイティブ
- **WSL2 不要**

## 起動手順

bash プロンプトで:

```bash
cd /c/_vps/git/multi-agent-team
./scripts/start.sh
```

psmux セッション `team` が 4 ペイン（pm + dev1 + dev2 + dev3）で起動。各ペインで `claude --dangerously-skip-permissions` が自動起動し、`instructions/<role>.md` を Read してから指示待ち状態に入ります。

## 通信プロトコル

YAML キュー方式:

| ファイル | 用途 |
|---|---|
| `queue/you_to_pm.yaml` | ユーザー → PM 指示 |
| `queue/inbox/<agent>.yaml` | エージェント別メールボックス |
| `queue/reports/<agent>.yaml` | dev → PM 完了報告 |

- **通知**: `tmux send-keys -t team:0.<N> "inbox" Enter`（psmux の tmux 互換コマンド）
- **受信**: 当面は polling（pm が手動 or 数秒間隔で inbox チェック）
- **将来**: PowerShell `FileSystemWatcher` で push 型に拡張可能

## 個別タスクのコード

新規プロジェクトはサブリポを切る。既存（`ai_training_for_rjc` / `mat-board-watcher`）はそのまま利用。本リポにアプリコードは置かない（運用ハブ）。

## 言語

- ユーザー対話・YAML メッセージ・コミットメッセージ: 日本語
- 技術用語（API 名・コマンド・識別子）: 英字のまま
- コードコメント: 必要なら日本語、不要なら書かない

## 既存資産

- `archive/pre-shogun-reset` ブランチに旧運用資産（旧 CLAUDE.md / docs/personas / docs/adr 9 本 / docs/templates / Notion 通信）を退避済み
- `docs/history/` は資産として保持（特に `2026-04-25_psmux-windows-investigation.md` が起動環境の一次ソース）

## Git 運用

- `main`: リリース済み
- `development`: 統合（PR base）
- `feature/*` / `fix/*` / `chore/*` / `docs/*`: development へ PR
