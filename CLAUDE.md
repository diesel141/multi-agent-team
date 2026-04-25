# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **このリポジトリは、psmux 上で動作するマルチエージェント汎用タスクチームのハブです。
> 個別タスクのコードはサブリポジトリで実装し、本リポジトリは PM・運用ドキュメント・歴史化アーカイブ・チームペルソナを集約します。**

---

## 1. 必須プロトコル（最重要・例外なし）

### 1.1 teammate（psmux ペイン分割）を優先、worktree 隔離は選ばない
- 子エージェント生成時、`Task` ツールで `isolation: "worktree"` を指定しない
- psmux + Claude Code の teammate モードに任せる（自動でペイン分割）
- 理由: Windows では worktree-tmux 統合が無効化されており、worktree を選ぶと
  不可視のインプロセス subagent になりプロトコル遵守が崩れる

### 1.2 ペイン間の直接通信禁止
- `tmux send-keys` で他ペインに業務指示・報告を送らない
- セットアップ時のキー注入（psmux 自動の `claude` 起動）は許容、業務通信には使わない

### 1.3 業務通信は Notion 掲示板の 3 種メッセージのみ
| 種別 | 必須項目 |
|------|---------|
| 開始指令 | タスクID / 受領者 / 背景 / 成果物定義 / 期日 / 受入基準 / 依存関係 |
| 問題報告 | タスクID / 事実 / 影響範囲 / 想定原因 / 必要な支援 / 期日影響 |
| 完了報告 | タスクID / 成果物リンク / 受入基準の照合結果 / 残課題 / 学び |

雑談・進捗共有・議論などその他のメッセージを掲示板に投稿しない。
別チャネル（Slack 等）も提案・新設しない。

### 1.4 違反検知時の対応
上記プロトコルに反する操作を求められた場合は、実行前に必ずユーザーに確認する。

---

## 2. 言語

- ユーザー対話・ドキュメント・Notion 掲示板・コミットメッセージ: **日本語**
- 技術用語（API 名・コマンド・識別子）は英字のまま使用してよい
- コードコメント: 必要なら日本語、不要なら書かない

## 3. 歴史化（pptx レポート用一次ソース）

### 3.1 保管場所
- 一次ソース: `docs/history/YYYY-MM-DD_<title>.md`
- 索引・栞: `~/.claude/projects/.../memory/`（auto memory）

### 3.2 記録対象（要所）
1. 意思決定 — 採用/却下したオプション、理由、当時の前提
2. 転換点 — 戦略・スコープ・チーム構成の変更
3. 失敗と学び — インシデント、リカバリ、再発防止策
4. 成功要因 — 想定を上回った成果と再現可能な要因
5. 重要な制約 — 新たに発覚した技術的/ビジネス的制約

ログ単位ではなく **「未来の自分が読んで判断材料になる単位」** で残す。

### 3.3 pptx 生成
- ユーザー指示時のみ生成
- ブランドカラー: `#000080`（ネイビー）
- 一次ソースは `docs/history/` の Markdown を集約
- ツールは python-pptx 等任意

---

## 4. リポジトリ構成

```
multi-agent-team/                          # 本リポジトリ（ハブ）
├── CLAUDE.md                              # 本ファイル（運用規約）
├── docs/
│   ├── persona.md                         # PM ペルソナ
│   ├── personas/                          # 他職種ペルソナ（Tech Lead 等を順次追加）
│   ├── setup-psmux.md                     # 環境構築手順
│   ├── notion-board-schema.md             # （将来）Notion 掲示板 DB 設計
│   ├── communication-protocol.md          # （将来）通信プロトコル詳細
│   └── history/                           # 歴史化アーカイブ（pptx 一次ソース）
│       └── YYYY-MM-DD_<title>.md
├── .env                                   # シークレット（git 管理外）
└── .env.example                           # シークレットのテンプレート
```

### 個別タスクのコード
- 新規プロジェクト: タスクごとにサブリポジトリを切る
- 既存プロジェクト: 既存リポジトリを利用

本リポジトリ自体にはアプリコードを置かない。

## 5. Git 運用

- **PR 運用**。`main` への直 push は禁止
- ブランチ命名: `feature/<topic>` / `fix/<topic>` / `docs/<topic>` / `chore/<topic>`
- コミット粒度: 論理的に最小・PR で意図が伝わる単位
- コミットメッセージ: 日本語、何を/なぜ を簡潔に

例外: 本リポジトリ初期化時のキックオフコミットのみ main 直 commit を許容。

## 6. 環境

- ホスト: ローカル Windows 機（Windows 10/11）
- シェル: PowerShell 7+ 必須（psmux teammate 注入の依存）
- ターミナル: Windows Terminal 推奨
- マルチプレクサ: psmux 3.3.3+（`marlocarlo.psmux`）
- AI CLI: Claude Code

詳細: `docs/setup-psmux.md`

### コマンドの書き換え
- 本リポジトリのドキュメントで bash 用に書かれた手順を参照する際は、
  実行前に PowerShell 用に書き換える（`ls`→`Get-ChildItem` など）
- ファイル系・検索系は Read / Grep / Glob ツールを優先（Bash 経由よりエラーが少ない）

## 7. シークレット管理

- `.env` に集約（`git` に commit しない）
- `.env.example` をリポジトリに置き、必要なキー名のみ列挙
- Notion API トークン等は `.env` に格納

## 8. 重要ファイル

| ファイル | 用途 |
|---------|------|
| `docs/persona.md` | PM 神崎玲奈のペルソナ |
| `docs/setup-psmux.md` | psmux 環境構築・操作・トラブルシューティング |
| `docs/history/2026-04-25_psmux-windows-investigation.md` | psmux × Windows × 本PJ の運用衝突点と決定事項 |
| `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` | 通信レイヤ参照アーキテクチャ |

## 9. アンチパターン（やらない）

- 雑談チャネル / 進捗ストリームの提案・新設
- Slack 等の別 IM ツールの導入提案
- worktree 隔離の選択
- send-keys による業務通信
- 掲示板に 3 種以外のメッセージを投稿
- Definition of Done なき着手
- 並列 P0 タスクの発行
- 推測でファイルを作る（重要事項は必ずユーザー確認）

## 10. 不明点があったら

ユーザーの判断が要るときは黙って進めず、簡潔に質問する。
本ファイルや `docs/` の規約と矛盾する依頼を受けた場合は、矛盾点を指摘してから判断を仰ぐ。
