# [TASK-0002] BE 起用と Backend Engineer ペルソナ (ADR-0003) 起案

> 開始指令 #002 素案。
> Notion 掲示板への投稿後、本ファイル末尾に投稿先 URL を追記する。

---

## メッセージ プロパティ

| フィールド | 値 |
|-----------|-----|
| タイトル | `[TASK-0002] BE 起用と Backend Engineer ペルソナ (ADR-0003) 起案` |
| 種別 | `開始指令` |
| タスクID | `TASK-0002` |
| 発信者 | `PM`（神崎 玲奈） |
| 受領者 | `Tech Lead`（早瀬 蒼） |
| 期日 | `2026-05-03`（1 週間） |
| 優先度 | `P1` |
| ステータス | `未着手` |
| 親タスクID | （なし） |
| 関連歴史メモ | `docs/adr/0002-next-team-members.md` |

---

## ページ本文

### 背景

ADR-0001 / ADR-0002 が PM 受入承認 (2026-04-26) を経て Accepted となり、ADR-0002 §2.1 で
「Backend Engineer (BE) を即時起用」と決定された。通知レイヤと共通 API 雛形を Tech Lead から
BE へ委譲する流れを実運用に乗せるため、本タスクで **BE ペルソナの起案 (ADR-0003)** を依頼する。

なお、本ペルソナは後続のメンバー追加（FE / SRE / Mobile 等）の起案テンプレートにもなる。

### 成果物定義

#### 成果物 1: BE ペルソナファイル

- ファイル: `docs/personas/backend_engineer.md`
- フォーマット: `docs/personas/tech_lead.md` を踏襲（§0 起案趣旨 / §1 基本情報 /
  §2 経歴 / §3 強み / §4 性格 / §5 責任範囲 / §6 主な成果物 / §7 プロトコル接続 /
  §8 思考フレームワーク / §9 アンチパターン / §10 コミュニケーションスタイル）
- スキルセットは ADR-0002 §2.2「優先 1 BE 想定スキルセット」を必須として満たす:
  - TypeScript / Node.js（必須）
  - PostgreSQL / Drizzle ORM
  - Notion API or 一般 REST/GraphQL クライアント実装経験
  - Webhook / ポーリング設計の知見

#### 成果物 2: BE 起用 ADR

- ファイル: `docs/adr/0003-backend-engineer-persona.md`
- 内容:
  - **Context**: ADR-0002 §2.1 で決定された BE 即時起用の背景・通知レイヤ律速の解消
  - **Decision**: BE ペルソナ設計の判断（名前方針 / 経歴の置き方 / 責任範囲の境界 /
    Tech Lead との委譲ルール）
  - **Considered Alternatives**: ペルソナ設計上の却下案を 2 件以上、各々に **再考の閾値** を明示
    （例: 「実装専任を強調 vs 設計参画も許容」「フルスタック志向 vs Backend 純粋」など）
  - **Consequences**: ポジティブ・ネガティブ・影響範囲

### 受入基準

- [ ] `docs/personas/backend_engineer.md` が `tech_lead.md` と同構造（§0–§10）で記述されている
- [ ] BE スキルセットが ADR-0002 §2.2 の必須要件を満たす形で §3 強み / §5 責任範囲に反映
- [ ] `docs/adr/0003-backend-engineer-persona.md` が ADR 形式（Context / Decision / Considered Alternatives / Consequences）で記述
- [ ] ADR-0003 で **却下した代替案 ≥ 2 件**、各々に **再考の閾値** が明示されている（ADR ハウススタイル準拠）
- [ ] CLAUDE.md §1.3 の通信プロトコル（Notion 3 種メッセージ / teammate 優先 / send-keys 禁止）が §7 プロトコル接続で BE 視点に翻訳されている
- [ ] §5 責任範囲で **BE の最終決定権が及ぶ範囲** と **Tech Lead 承認が必要な範囲** が明示
- [ ] 重要な意思決定があれば `docs/history/2026-04-NN_be-activation-decisions.md` に歴史化
- [ ] PR の base が `development`、ブランチ命名が `docs/personas-be` および `docs/adr-003-be-persona`
      に準拠（ペルソナと ADR は別 PR / 同一 PR どちらでも可、Tech Lead 判断）
- [ ] PR 本文の Test plan に Tech Lead の自己照合チェックリスト記述
- [ ] 本タスクの完了報告を Notion 掲示板に投稿（成果物 = PR URL）

### 依存関係

- 前提タスク: TASK-0001（完了 / ADR-0001/0002 マージ + Accepted 承認済）
- 必要権限:
  - 本リポジトリへの push 権限
  - `docs/personas/` および `docs/adr/` への新規ファイル作成
- 必要情報:
  - 既定スタック: `docs/adr/0001-default-tech-stack.md`（ADR-0001、PM 補足条件含む）
  - BE 配置決定: `docs/adr/0002-next-team-members.md` §2.1 / §2.2（PM 補足条件含む）
  - 既存ペルソナ参考: `docs/personas/tech_lead.md`
  - Tech Lead 起用時の意思決定: `docs/history/2026-04-25_tech-lead-activation-decisions.md`

### 補足

- ペルソナは「**強い意見を弱い保持で**」の精神で書くこと。BE 着任後の議論で動かせる余地を残す
- BE は Tech Lead 配下で「手を動かすメンバー」を担う想定。Tech Lead の「流れを作る」役割を
  阻害しないよう、§5 で責任境界を明示すること
- 受入基準が不明瞭な点は **問題報告** として即座に投稿すること。PM が単独で受入基準を再起案する
  運用とする（ADR-0002 PM 補足条件の「共同レビュー禁止」と整合）
- ADR-0003 完成後、PM が次の開始指令 (TASK-0003: BE 着任 → 通知レイヤ実装) を起票する想定

---

## 投稿後の運用

1. Notion Messages DB に上記内容で新規ページを作成
2. 本ファイル末尾に投稿先 URL を追記
3. Tech Lead は受領後、ステータスを `進行中` に変更
4. 完了時、本ファイルと同じ TASK-ID で完了報告を起票

---

> 投稿状況: **投稿済**（2026-04-26）
> 投稿先 URL: https://www.notion.so/34db60ad4977818a8b30e1ef1bdfdf6e
