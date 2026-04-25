# [TASK-0001] Tech Lead 起用と初期スタック・チーム構成提案

> Notion 掲示板の最初のメッセージ素案。
> ユーザーは Notion 掲示板（Messages Database）構築後、本ファイルの内容を新規ページに転記して投稿する。
> 投稿後は本ファイルを「投稿済」マークと Notion ページ URL の追記でアーカイブ化する。

---

## メッセージ プロパティ

| フィールド | 値 |
|-----------|-----|
| タイトル | `[TASK-0001] Tech Lead 起用と初期スタック・チーム構成提案` |
| 種別 | `開始指令` |
| タスクID | `TASK-0001` |
| 発信者 | `PM`（神崎 玲奈） |
| 受領者 | `Tech Lead`（早瀬 蒼） |
| 期日 | `2026-05-09`（2 週間） |
| 優先度 | `P1` |
| ステータス | `未着手` |
| 親タスクID | （なし） |
| 関連歴史メモ | `docs/history/2026-04-25_tech-lead-activation-decisions.md` |

---

## ページ本文

### 背景

本プロジェクト「Multi-Agent Team」は psmux 上のペイン分割で複数の Claude Code エージェントを動かし、
Notion 掲示板の 3 種メッセージのみで通信する制約下で、マルチプラットフォームアプリ開発から
研修資料作成まで担う汎用タスクチームである。

PM が要件・期日を、Tech Lead が技術判断を担う体制を 2026-04-25 に確定。
Tech Lead 早瀬を即時常駐とし、最初の責務として **本プロジェクトの「土台」を作りきる** ことを依頼する。

### 成果物定義

以下 2 件の ADR を `docs/adr/` に新規作成し、`development` ブランチへ PR を起こすこと。

#### 成果物 1: 標準スタック ADR

- ファイル: `docs/adr/0001-default-tech-stack.md`
- 内容:
  - マルチプラットフォーム展開（iOS / Android / Web / Backend）における **既定の技術選択**
  - 言語・フレームワーク・状態管理・DB・ホスティング・CI/CD・モニタリング
  - 各選択について **採用理由** と **却下した代替案** を ADR 形式で記述
  - Boring Technology 優先の方針を反映
  - 本リポジトリでは実装を行わない（タスクごとサブリポジトリ）ため、
    サブリポ初期化スクリプト or 雛形リポの方針も提示
- 形式: ADR テンプレート（Context / Decision / Consequences）

#### 成果物 2: 次メンバー提案 ADR

- ファイル: `docs/adr/0002-next-team-members.md`
- 内容:
  - 直近の業務見立てから、次にアサインすべき職種の **優先順位付き提案**
  - 各候補職種について:
    - 想定する初期タスク
    - 起用タイミング（即時 or タスク到来時）
    - ペルソナ起案の優先度
  - 上限: 提案 3 職種まで（PM の意思決定負荷を軽減）

### 受入基準

- [ ] `docs/adr/0001-default-tech-stack.md` が ADR 形式で記述され、PR 起票されている
- [ ] `docs/adr/0002-next-team-members.md` が同様に PR 起票されている
- [ ] 両 ADR で「却下した代替案」が最低 2 件ずつ列挙されている
- [ ] PR の base が `development`、ブランチ命名が `docs/adr-001-tech-stack`
      および `docs/adr-002-next-members` に準拠
- [ ] PR 本文の Test plan で Tech Lead が自己照合チェックリストを記述
- [ ] 本タスクの完了報告を Notion 掲示板に投稿（成果物 = PR URL × 2）
- [ ] 重要な意思決定（採用 SaaS / クラウド等）を `docs/history/` に歴史化

### 依存関係

- 前提タスク: なし（本プロジェクトの最初のタスク）
- 必要権限:
  - 本リポジトリへの push 権限
  - `docs/adr/` ディレクトリの新規作成
- 必要情報:
  - PM ペルソナ: `docs/persona.md`
  - Tech Lead ペルソナ: `docs/personas/tech_lead.md`
  - 通信プロトコル: `CLAUDE.md` §1
  - Git 運用: `CLAUDE.md` §5
  - psmux 環境: `docs/setup-psmux.md`
  - 過去の意思決定: `docs/history/`

### 補足

- ADR は「**強い意見を弱い保持で**」の精神で書くこと。妥協せず提案し、議論で動かせる余地を残す
- 本タスクは Tech Lead 着任の象徴的な成果物となる。pptx レポート時に「Tech Lead が最初に
  何を判断したか」が読み取れる解像度で書くこと
- 不明点・要件の不確実性は **問題報告** として即座に投稿すること（沈黙によるリスク隠蔽の禁止）

---

## 投稿後の運用

1. Notion Messages DB に上記内容で新規ページを作成
2. 本ファイル末尾に投稿先 URL を追記（例: `> 投稿済: https://notion.so/...`）
3. Tech Lead は受領後、ステータスを `進行中` に変更
4. 完了時、本ファイルと同じ TASK-ID で完了報告を起票

---

> 投稿状況: **未投稿**（Notion 掲示板の構築待ち）
> 投稿先 URL:
