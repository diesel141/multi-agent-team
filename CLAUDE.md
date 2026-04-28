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

### 1.3 業務通信は Notion 掲示板（ハイブリッド型 / formal + informal）

掲示板は 2 層構造で運用する。**formal（必須項目あり）** と **informal（自由投稿可）** の両方を許容するが、別チャネル（Slack 等）の提案・新設は禁止する。

#### formal — トレーサビリティと歴史化の核（必須項目維持）

| 種別 | 必須項目 |
|------|---------|
| 開始指令 | タスクID / 受領者 / 背景 / 成果物定義 / 期日 / 受入基準 / 依存関係 |
| 問題報告 | タスクID / 事実 / 影響範囲 / 想定原因 / 必要な支援 / 期日影響 |
| 完了報告 | タスクID / 成果物リンク / 受入基準の照合結果 / 残課題 / 学び |

#### informal — 軽量に流せる業務会話（自由文体可）

| 種別 | 用途 | 推奨 SLA / 投稿粒度 |
|------|------|---------------------|
| 着手返答 | 開始指令を受領した直後の「了解、着手します」 | 受領から 30 分以内 |
| 進捗共有 | 中間状態の更新 | 「判断・状態遷移の単位」で投稿（ログ単位の 30% 完了等は禁止） |
| 質疑応答 | 仕様の不確実性を解消する一問一答 | 業務継続に支障が出るレベルなら問題報告へ昇格 |
| 議論 | 複数選択肢の比較・トレードオフ言語化 | 後で ADR / 歴史化メモへ昇格する候補 |

#### 共通ルール

- すべての投稿で **「種別」プロパティは必須**（formal 3 種 + informal 4 種から 1 つ選択）
- formal の必須項目は不変。`docs/notion-board-schema.md` §2 のテンプレートに従う
- informal は文体・長さ自由。ただし掲示板以外の IM チャネル（Slack 等）の提案・新設は禁止
- 詳細は `docs/adr/0005-communication-protocol-revision.md` / `docs/notion-board-schema.md` を参照

#### 通知レイヤの運用方針（ADR-0008）

- **自動 wake-up 通知レイヤは持たない**（ADR-0003 §2.1 を ADR-0008 §2.1 で Superseded / mat-board-watcher リポは 2026-04-29 に GitHub 削除 / phase2 復活時は別リポを起票し ADR-0003 / ADR-0008 / 歴史化メモを一次ソースとする）
- **新着メッセージ検知**: 各ロールはセッション開始時に **Notion mcp で能動 fetch**（受領者プロパティで自分宛のメッセージを抽出）
- **他エージェントの召喚**: ユーザー（上様）が `/<role>` slash command または Task ツールで起動 / 必要に応じて外部プロセス `claude --dangerously-skip-permissions ...` を BG 起動
- **phase2 復活条件**: ADR-0008 §3 却下 A 再考閾値（6 ロール以上 + 同時稼働 4 + 1 日 10 メッセージ超）が恒常化した時点で ADR-0009 を起案して再導入

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

### 5.1 ブランチ戦略 — trunk-based + integration

| ブランチ | 役割 | 直接 push | 直接 PR |
|---------|------|----------|---------|
| `main` | リリース済み・本番安定版（タグを切る基点） | 禁止 | 禁止（development からのみ） |
| `development` | 統合ブランチ。常時 deployable を維持 | 禁止 | feature/fix/docs/chore からの PR を受ける |
| `feature/<topic>` | 機能追加 | 自由（自分のブランチ） | → `development` |
| `fix/<topic>` | バグ修正 | 同上 | → `development` |
| `docs/<topic>` | ドキュメント変更 | 同上 | → `development` |
| `chore/<topic>` | リポ運用・設定変更 | 同上 | → `development` |

### 5.2 フロー

```
feature/* ─┐
fix/*     ─┤
docs/*    ─┼─PR─▶ development ─PR(リリース時)─▶ main ─tag─▶ release
chore/*   ─┘
```

- 日々の開発は **`development` への PR**。Base ブランチを間違えない
- リリースは development → main の PR を別途起こし、マージ時にタグを切る
- `main` は常にデプロイ可能。`development` も常時 deployable を維持する
  （壊れた状態で滞留させない）

### 5.3 PR ルール

- ブランチ命名: `<種別>/<短いトピック>`（小文字・ケバブケース。例: `feature/notion-board-init`）
- コミット粒度: 論理的に最小・PR で意図が伝わる単位
- コミットメッセージ: 日本語、何を / なぜ を簡潔に
- レビュー: 1 名以上の承認後マージ（チーム規模に応じて運用）
- マージ方式: squash を基本。コミット履歴を develop で再現する必要がない限り
- 同期: long-lived branch は定期的に `development` を rebase / merge して取り込む

### 5.4 例外

- 本リポジトリ初期化時のキックオフコミットのみ `main` 直 commit を許容（既に完了）
- 緊急 hotfix は `fix/hotfix-*` を main から切り、main と development 双方へマージ

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

- 別 IM チャネル（Slack 等）の提案・新設
- worktree 隔離の選択
- send-keys による業務通信
- 掲示板に「種別」プロパティを設定せず投稿する（formal/informal いずれの種別も明示する）
- 進捗共有を「30% 完了」のようなログ単位で乱発する（判断・状態遷移の単位で投稿）
- Definition of Done なき着手
- 並列 P0 タスクの発行
- 推測でファイルを作る（重要事項は必ずユーザー確認）

## 10. 不明点があったら

ユーザーの判断が要るときは黙って進めず、簡潔に質問する。
本ファイルや `docs/` の規約と矛盾する依頼を受けた場合は、矛盾点を指摘してから判断を仰ぐ。
