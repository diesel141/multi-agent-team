# ADR-0002: 次にアサインする職種の提案

- 状態: **Superseded by ADR-0006**（§5.3 ペルソナ起案フローは ADR-0006 §5 で更新。§2.1 BE/FE/SRE 採用順 / §3 却下案 A〜G の起用条件は継続有効）
- 起案日: 2026-04-25
- 起案者: Tech Lead 早瀬 蒼
- 関連: `docs/adr/0001-default-tech-stack.md` / `docs/adr/0006-persona-creation-flow-and-role-recalibration.md` / `docs/personas/tech_lead.md` /
  `docs/history/2026-04-25_tech-lead-activation-decisions.md` §2.4

---

## 1. Context（文脈）

PM 神崎から「次メンバーの選定は Tech Lead に委譲」(`docs/history/2026-04-25_tech-lead-activation-decisions.md` §2.4) の決定を受け、本 ADR で **直近の業務見立てに基づく次メンバー優先順位** を提案する。

### 1.1 制約

| 項目 | 内容 |
|------|------|
| 提案上限 | **3 職種まで**（PM の意思決定負荷軽減、TASK-0001 の受入条件） |
| 起用判断 | Tech Lead 起案 → PM 神崎承認 → 次の開始指令で起動 |
| 起用方式 | psmux ペイン分割 + Notion 掲示板 3 種メッセージ通信 |
| 既存メンバー | PM 神崎玲奈 / Tech Lead 早瀬蒼（2026-04-25 時点） |
| 既定スタック | ADR-0001 で定義（TS/Next.js/PostgreSQL/Vercel 中心） |

### 1.2 直近 4-8 週間で発生する見立て

ADR-0001 §3 / §4 と TASK-0001 完了後の自然な次タスクから、以下を想定する:

1. **通知レイヤの実装** — `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` §4 で
   未決のまま Tech Lead に投げられた、Notion 掲示板の新着検知
   （ポーリング / Webhook / chokidar 等から選定）。
   サブリポ `mat-board-watcher` を新設して実装する想定
2. **テンプレートリポ整備** — ADR-0001 §2.3 で決めたサブリポ初期化テンプレート
   `multi-agent-template` の新規作成（TS モノレポ + Biome + Vitest + GH Actions）
3. **最初の業務タスク（未到来）** — Web/Backend/Mobile/研修 のいずれか
4. **CI/CD 整備** — Notion API レート制限・Vercel デプロイ・型チェックの GH Actions ワークフロー
5. **歴史化 → pptx 自動生成** — `docs/history/*.md` を入力に python-pptx で出力する
   サブリポ（時期未定、優先度低）

### 1.3 設計原則の適用

- **Conway's Law**（`docs/personas/tech_lead.md` §8）: チーム構造とアーキテクチャは鏡。
  通信レイヤを実装するメンバーがいないとアーキテクチャが机上に留まる
- **少数精鋭**: 「1 タスクを 1 名で完走できる粒度」のメンバーを優先。並列 P0 を
  避ける（PM ペルソナ §5.6）
- **Boring 採用**: 最初に Mobile / QA / Researcher を入れない。需要が確定してから

---

## 2. Decision（決定）

### 2.1 提案する次メンバー（優先順、最大 3 職種）

| 優先 | 職種 | 起用タイミング | 初期想定タスク | ペルソナ起案優先度 |
|------|------|---------------|----------------|-------------------|
| **1** | **Backend Engineer (BE)** | **即時**（PM 承認直後） | 通知レイヤ実装 / `mat-board-watcher` サブリポ初期化 / Notion MCP の運用ラッパー / 共通 API 雛形 | **高**（即時、ADR-0001 と同じ品質基準で起案） |
| **2** | **Frontend Engineer (FE)** | **タスク到来時**（最初の Web タスク受領時） | Next.js 15 雛形のテンプレートリポ整備 / 認証導線（Clerk）/ 最初のページ実装 | 中（タスクが見えた時点で起案） |
| **3** | **SRE / DevOps Engineer** | **タスク到来時**（CI/CD またはインフラ案件発生時） | GitHub Actions ワークフロー整備 / Vercel/Supabase の権限設計 / シークレット運用 / 観測性整備（Sentry/Axiom） | 低（必要性が顕在化したら起案） |

### 2.2 起用方針の詳細

#### 優先 1: Backend Engineer（即時）

- **なぜ即時か**:
  - 通知レイヤは Notion 掲示板の運用速度を直接決める律速要因。Tech Lead が
    本来の「流れを作る」役割（`docs/personas/tech_lead.md` §9）に集中するため、
    BE が手を動かすメンバーとして最優先で必要
  - サブリポ初期化テンプレ（ADR-0001 §2.3）の最初の被試験者にもなる
- **想定スキルセット**:
  - TypeScript / Node.js（必須）/ PostgreSQL / Drizzle ORM
  - Notion API or 一般的な REST/GraphQL クライアント実装経験
  - Webhook / ポーリング設計の知見
- **PM への提案項目**: ペルソナ起案（名前・経歴・性格・コミュニケーションスタイル）を
  ADR-0003 として別途起こす

#### 優先 2: Frontend Engineer（タスク到来時）

- **なぜタスク到来時か**:
  - 現時点で Web UI が必要なタスクは未到来。先行起用すると「待機する FE」が発生し、
    並列 P0 を避ける PM 原則（§5.6）に反する
  - テンプレートリポ自体は BE がスキャフォルドできる粒度
- **トリガ条件**: 「Web UI を含むタスクの開始指令」が PM から発行されたタイミング
- **想定スキルセット**:
  - TypeScript / Next.js 15 App Router（必須）
  - TanStack Query / Zustand / Tailwind CSS
  - Playwright での E2E 経験

#### 優先 3: SRE / DevOps Engineer（タスク到来時）

- **なぜタスク到来時か**:
  - SaaS 中心スタック（ADR-0001）のため、初期段階では Vercel/Supabase の Web UI で
    十分。SRE の専任化は早すぎる
  - ただし「複数サブリポ × CI/CD 一貫性」「シークレット集中管理」「障害対応」が
    顕在化したら必須化
- **トリガ条件（いずれか）**:
  - サブリポ数が 3 以上になり CI ワークフローの重複が目立つ
  - 月額 SaaS 費が $200 を超える（ADR-0001 §3.4 G の閾値の 4 割）
  - 本番障害が 1 件発生する
- **想定スキルセット**:
  - GitHub Actions / Terraform or Pulumi（後者は ADR-0001 で「未導入」）
  - Sentry / Axiom / Datadog 等の観測性ツール
  - インシデント対応経験

### 2.3 ペルソナ起案の進め方

採用順に Tech Lead が起案、PM が承認 → Notion 掲示板 開始指令で起動:

1. ADR-0003: Backend Engineer ペルソナ（即時起案）
2. ADR-0004: Frontend Engineer ペルソナ（FE トリガ条件成立時）
3. ADR-0005: SRE / DevOps Engineer ペルソナ（SRE トリガ条件成立時）

各ペルソナは Tech Lead ペルソナ (`docs/personas/tech_lead.md`) のフォーマットを
踏襲する（基本情報 / 経歴 / 強み / 性格 / 責任範囲 / 成果物 / プロトコル接続 /
思考フレームワーク / アンチパターン / コミュニケーションスタイル）。

---

## 3. Considered Alternatives（却下した代替案）

### 却下 A: Mobile Engineer を上位 3 に含める

- **却下理由 1**: 直近 4-8 週間で Mobile タスクの開始指令が見えていない。
  起用後に待機させるとリソース無駄打ち
- **却下理由 2**: ADR-0001 §2.2 で「Mobile はネイティブ既定（Swift/Kotlin）」と
  決めたため、起用時は **iOS と Android で別人材** になる可能性が高く、
  上限 3 職種を圧迫する
- **再考の閾値**: Mobile タスクの開始指令が 1 件でも発行された時点で ADR-0006 として
  起案

### 却下 B: QA Engineer を上位 3 に含める

- **却下理由 1**: 開発初期は実装者が Vitest/Playwright を書く方がフィードバックループ
  が短い（Tech Lead ペルソナ §3 のレビュー観点でカバー）
- **却下理由 2**: チーム規模 ≤ 5 名で QA を専任化すると、レビュー以外の専門業務
  （テストプラン作成、バグトリアージ等）の量が QA を待機状態にする
- **再考の閾値**:
  - リグレッション率が 1 スプリント 2 件以上
  - 受入基準の照合（PM ペルソナ §5.4）で抜けが目立つようになった場合

### 却下 C: TechWriter を即時起用

- **却下理由 1**: 研修資料タスクの開始指令がまだ無い。発行されたタイミングで
  起案する方が、想定読者・レベル感に合った人材を選べる
- **却下理由 2**: ADR や歴史化メモは Tech Lead/PM が直接書く規約のため、内部
  ドキュメント用途に専任 TechWriter は不要
- **再考の閾値**: 「外部公開の研修資料」または「顧客向け技術ドキュメント」のタスクが
  発行された時点

### 却下 D: Researcher を即時起用

- **却下理由 1**: 現時点でリサーチ対象が定義されていない（先行事例調査は
  `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` で完了済み）
- **却下理由 2**: スポット的なリサーチタスクは Tech Lead が直接担当できる量
- **再考の閾値**: 「特定ドメイン（例: 医療・金融・法務）の調査が継続的に必要」と
  判明した時点

### 却下 E: SRE を即時起用（優先 1 への昇格）

- **却下理由 1**: 初期スタックは SaaS 中心で運用負荷が低い。SRE 専任化は
  Conway's Law から見て過剰（チーム構造に対しサービス分割が早すぎる）
- **却下理由 2**: BE が GitHub Actions の最小ワークフローを ADR-0001 のテンプレに
  同梱する想定で、初期 CI/CD は BE で吸収可能
- **採用に転じる条件**: §2.2 SRE のトリガ条件参照

### 却下 F: 専任 PM Assistant / Scrum Master

- **却下理由 1**: PM 神崎ペルソナ（§3, §10）が情報設計とデリバリー規律を自前で
  担保する想定。アシスタント職種は責任分散を生む
- **却下理由 2**: Notion 掲示板の 3 種メッセージ規約自体が儀式（スタンドアップ等）を
  最小化する設計。Scrum Master の介入余地が小さい

### 却下 G: 上限 3 を緩めて 4 職種以上を一括提案

- **却下理由 1**: TASK-0001 の受入条件（上限 3）に違反
- **却下理由 2**: PM が同時に意思決定する人材数を増やすと、各メンバーへの権限境界・
  期日設定の品質が落ちる（PM ペルソナ §4「明示性」）

---

## 4. Consequences（帰結）

### 4.1 ポジティブ

1. **流れを止めない**: BE 即時起用により、Tech Lead がアーキテクチャ判断と
   コードレビューに専念できる体制になる
2. **段階的拡張**: FE/SRE は需要トリガ式で起用するため、待機メンバーが発生しない
3. **判断の連続性**: Tech Lead 起案 → PM 承認のループが動き出すことで、
   Tech Lead 起用時に決めた「次メンバー委譲」(`docs/history/2026-04-25_tech-lead-activation-decisions.md` §2.4) が
   実運用に乗る
4. **ペルソナ起案の標準化**: ADR-0003 以降のペルソナ起案テンプレが固まり、
   後続メンバー追加時の手戻りが減る

### 4.2 ネガティブ・リスク

1. **BE 起用後の最初の 1 タスクで品質が決まる**: テンプレートリポ + 通知レイヤは
   後続全タスクの基盤になるため、BE 着任時の TASK-0002（仮）の受入基準を
   慎重に書く必要がある
   - **緩和策**: PM/Tech Lead が共同で BE 向け開始指令の受入基準をレビューする
2. **FE/SRE のトリガ条件が曖昧化するリスク**: 「タスク到来時」は便利だが
   先送りの口実にもなる
   - **緩和策**: §2.2 で各トリガ条件を測定可能な形で明示済（「Web UI を含む開始指令」「サブリポ 3 以上」「月額 $200 超」「本番障害 1 件」）
3. **3 職種上限の窮屈さ**: Mobile/QA/TechWriter/Researcher が必要になった時、
   既存 3 職種の優先順位入替が必要
   - **緩和策**: 各却下案に「再考の閾値」を明示済。閾値到達時は本 ADR を更新する

### 4.3 影響範囲

- **本リポジトリ**: ペルソナ追加に伴い `docs/personas/` に新ファイルが追加される
- **Notion 掲示板**: `発信者 / 受領者` の Select 値（既に `BE / FE / Mobile / QA /
  SRE / TechWriter / Researcher` を含む）はスキーマ修正不要
  （`docs/notion-board-schema.md` §1.3 で先行登録済）
- **psmux**: 起用ごとにペインが 1 つ増える運用。teammate モードで自動分割される

---

## 5. 開いている論点（PM 承認・議論で動かしたい点）

> 「**強い意見を弱い保持で**」。以下は議論で動く可能性のある点を明示する。

1. **BE 即時起用の是非** — 「通知レイヤは後回しでも運用回る」という判断があれば
   BE もトリガ式に降格可能。その場合、優先 1 を空席にし FE を繰り上げない
2. **FE と SRE の優先順入替** — 国内案件で「インフラの調達フェーズ」が先に来る
   想定があれば SRE を優先 2 に上げる
3. **ペルソナ起案の主体** — 本 ADR では Tech Lead 起案 + PM 承認としているが、
   PM がペルソナ自体は自分で起こしたい場合は分担を変更可能（その場合 Tech Lead は
   スキル要件・初期タスクの定義のみ提供）
   **※ 2026-04-27 ADR-0006 §5 で本論点は更新済。正規ルートは「PM 起案」、Tech Lead 起案は残置ルートに縮退（ADR-0006 §2.1 / §5.1 / §5.2 参照）。**
4. **Mobile 担当の事前確保** — 顧客側で Mobile タスクが内定している場合、
   §3 却下 A の判断を事前に動かす

---

## 6. References（関連資料）

- `docs/adr/0001-default-tech-stack.md` — 既定スタック（本 ADR の前提）
- `docs/personas/tech_lead.md` — Tech Lead ペルソナ（起案者の判断基準）
- `docs/persona.md` — PM ペルソナ
- `docs/history/2026-04-25_tech-lead-activation-decisions.md` — 次メンバー委譲の決定
- `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` §4 — 通知レイヤ未決事項
- `docs/notion-board-schema.md` §1.3 — 役職スキーマ（追加不要）
- `docs/history/2026-04-25_next-team-members-decisions.md` — 本 ADR の歴史化メモ
