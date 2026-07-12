# CLAUDE.md

YAML キュー + マルチペイン + ファイル監視思想を踏襲した **Multi-Agent ADD（Agent-Driven Development）チーム**環境。Windows ネイティブで psmux を使用。

## 基本ルール

- 本リポにアプリコードは置かない（運用ハブ）
- 新規プロジェクトはサブリポを切る。既存（`ai_training_for_rjc` / `mat-board-watcher`）はそのまま利用
- ユーザー対話・YAML メッセージ・コミットメッセージ: 日本語
- 技術用語（API 名・コマンド・識別子）: 英字のまま

## ディレクトリ構造

```
multi-agent-team/
├── docs/
│   ├── specs/          # 仕様書（チーム構成・起動・通信プロトコル）
│   ├── history/        # 過去の調査・ADR 記録
│   └── images/         # レポート用画像（png は docs 直下に置かない）
├── instructions/       # 各ロールの指示ファイル
├── queue/              # YAML キュー（エージェント間通信）
└── scripts/            # 起動スクリプト等
```

## 参照先

| 内容 | ファイル |
|---|---|
| チーム構成・ロール定義 | [`docs/specs/team-structure.md`](docs/specs/team-structure.md) |
| 起動環境・起動手順 | [`docs/specs/startup.md`](docs/specs/startup.md) |
| 通信プロトコル（YAML キュー） | [`docs/specs/communication-protocol.md`](docs/specs/communication-protocol.md) |
| 起動環境の一次ソース | [`docs/history/2026-04-25_psmux-windows-investigation.md`](docs/history/2026-04-25_psmux-windows-investigation.md) |

## 既存資産

`archive/legacy` ブランチに旧運用資産（旧 CLAUDE.md / docs/personas / docs/adr 9 本 / docs/templates / Notion 通信）を退避済み
