# [TASK-0002] Backend Engineer ペルソナ起案と通知レイヤ初期設計

> Notion 掲示板への投稿素案。
> 投稿後は本ファイル末尾に投稿先 URL を追記してアーカイブ化する。

---

## メッセージ プロパティ

| フィールド | 値 |
|-----------|-----|
| タイトル | `[TASK-0002] Backend Engineer ペルソナ起案と通知レイヤ初期設計` |
| 種別 | `開始指令` |
| タスクID | `TASK-0002` |
| 発信者 | `PM`（神崎 玲奈） |
| 受領者 | `Tech Lead`（早瀬 蒼） |
| 期日 | `2026-05-10`（2 週間） |
| 優先度 | `P1` |
| ステータス | `未着手` |
| 親タスクID | `TASK-0001` |
| 関連歴史メモ | `docs/history/2026-04-26_task-0001-acceptance-decisions.md` |

---

## ページ本文

### 背景

TASK-0001 で起案された ADR-0001（既定の技術スタック）と ADR-0002（次メンバー提案）が
2026-04-25 に PM 受入承認・`development` へマージ済。
ADR-0002 §2.1 の「**Backend Engineer 即時起用**」方針および §2.3「ADR-0003 (BE ペルソナ)
即時起案」を実運用に落とすのが本タスク。

通知レイヤ（Notion 掲示板の新着検知）は
`docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` §4 で
未決のまま Tech Lead に投げられた論点であり、BE 着任前に **設計選択肢の決着** を
ADR で残す必要がある。BE はこの ADR を実装仕様として受け取る前提。

### 成果物定義

以下 2 件の ADR を `docs/adr/` に新規作成し、`development` ブランチへ PR を起こすこと。

#### 成果物 1: Backend Engineer ペルソナ ADR

- ファイル: `docs/adr/0003-backend-engineer-persona.md`
- フォーマット: Tech Lead ペルソナ (`docs/personas/tech_lead.md`) と同構成
  - 0. PM からの起案趣旨 → 1. 基本情報 → 2. 経歴 → 3. 強み・専門領域 →
    4. 性格・行動原理 → 5. 責任範囲 → 6. 主な成果物 → 7. プロトコル接続 →
    8. 思考フレームワーク → 9. アンチパターン → 10. コミュニケーションスタイル →
    11. 起用判断のために PM から確認したい点
- ペルソナ本体は別途 `docs/personas/backend_engineer.md` として配置（Tech Lead と同様）
- 想定スキル: ADR-0002 §2.2「Backend Engineer」の項参照（TS/Node.js / PostgreSQL /
  Drizzle ORM / Notion API or REST/GraphQL / Webhook・ポーリング設計）

#### 成果物 2: 通知レイヤ初期設計 ADR

- ファイル: `docs/adr/0004-notification-layer-design.md`
- 内容:
  - Notion 掲示板の新着検知方式の **比較** と採用案（最低 3 案を比較。例: 定期ポーリング /
    Notion Webhook（提供される場合）/ chokidar によるファイル監視 / SSE / etc.）
  - 採用案の **アーキテクチャ概要図**（Mermaid 推奨）
  - サブリポ `mat-notion-watcher` の初期化方針（`multi-agent-template` を先行整備するか、
    `mat-notion-watcher` で同時に整備するか）
  - レート制限・障害対応・観測性（Sentry / Axiom）の初期設計
  - **採用しない案ごとに「再考の閾値」を必ず明示**

### 受入基準

- [ ] `docs/adr/0003-backend-engineer-persona.md` が ADR 形式で記述、PR 起票
- [ ] `docs/personas/backend_engineer.md` が同 PR で配置（Tech Lead ペルソナと同構成）
- [ ] `docs/adr/0004-notification-layer-design.md` が ADR 形式で別 PR 起票
- [ ] **両 ADR で却下案 ≥ 2 件、各却下案に「再考の閾値」を 100% 明示**
      （ハウススタイル徹底。永久却下なら「再考の閾値: 該当なし」と明示）
- [ ] PR base = `development`、ブランチ命名 = `docs/adr-003-be-persona` /
      `docs/adr-004-notification-layer`
- [ ] PR 本文の Test plan で Tech Lead が自己照合チェックリストを記述
- [ ] 完了報告を Notion 掲示板に投稿（成果物 = PR URL × 2）
- [ ] 重要な意思決定を `docs/history/2026-04-NN_<title>.md` に歴史化
- [ ] ADR-0004 §5「開いている論点」を 3-5 件明示（強い意見を弱い保持で）

### 依存関係

- 前提タスク: TASK-0001（採択済）
- 必要権限:
  - 本リポジトリへの push 権限
  - `docs/adr/` および `docs/personas/` への新規ファイル追加
- 必要情報:
  - PM ペルソナ: `docs/persona.md`
  - Tech Lead ペルソナ: `docs/personas/tech_lead.md`
  - ADR-0001 / ADR-0002（採択済）
  - 通信プロトコル: `CLAUDE.md` §1
  - ADR ハウススタイル: auto memory `adr_house_style.md`（却下案ごとに再考閾値必須）

### 補足

- **ハウススタイル 100% 適用が今回のタスクの主眼の一つ**。
  TASK-0001 受入レビュー（PR #6 / #7）で軽微な漏れ計 6 箇所を指摘済。
  本タスクで漏れがあった場合は merge ブロッカーとして修正要求する
- **強い意見を弱い保持で**。BE ペルソナの性格設定・スキル要件は Tech Lead の
  解像度で起案する。PM は最終承認時に「人材像が初期タスクと噛み合っているか」を見る
- **問題報告の即時性**: 通知レイヤ設計で技術的な不確実性が見えた段階で
  問題報告として投稿する（沈黙によるリスク隠蔽の禁止）
- 後続: 本タスク完了後、PM が「TASK-0003 BE 起用」開始指令を発行 → BE 着任 →
  `mat-notion-watcher` サブリポ初期化に着手

---

## 投稿後の運用

1. Notion Messages DB に上記内容で新規ページを作成
2. 本ファイル末尾に投稿先 URL を追記
3. Tech Lead は受領後、ステータスを `進行中` に変更
4. 完了時、本ファイルと同じ TASK-ID で完了報告を起票

---

> 投稿状況: **投稿済**（2026-04-26）
> 投稿先 URL: https://www.notion.so/34db60ad4977816db255c0b69861f637
