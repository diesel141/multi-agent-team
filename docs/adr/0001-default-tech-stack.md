# ADR-0001: 既定の技術スタック

- 状態: **Proposed**（PM 承認待ち）
- 起案日: 2026-04-25
- 起案者: Tech Lead 早瀬 蒼
- 関連: `docs/personas/tech_lead.md` / `CLAUDE.md` §4-§5 / `docs/history/2026-04-25_tech-lead-activation-decisions.md`

---

## 1. Context（文脈）

「Multi-Agent Team」は psmux 上で複数 Claude Code エージェントが Notion 掲示板の
3 種メッセージのみで通信する制約下、**マルチプラットフォーム展開（iOS / Android / Web / Backend）
+ 開発者向け研修資料生成**を担う汎用タスクチームである。

タスクごとにサブリポジトリを切る運用のため、各サブリポが個別に技術スタックを選ぶと
チーム全体のレビュー観点・CI 設計・ナレッジ共有が分散する。本 ADR は **「迷ったら
これを採る」既定スタック**を定義し、サブリポ初期化のテンプレと CI レビュー観点の
基準点を作ることを目的とする。

### 1.1 制約・前提

| 種別 | 内容 |
|------|------|
| ホスト | ローカル Windows 機（PowerShell 7+） |
| エージェント | Claude Code CLI（複数ペイン同時稼働） |
| 通信 | Notion 掲示板（公式 Remote MCP）3 種メッセージのみ |
| 業務範囲 | iOS / Android / Web / Backend / 研修資料 |
| チーム規模 | 少数精鋭（PM 1 + Tech Lead 1 + 必要に応じて実装エージェント数名） |
| 言語 | UI / ドキュメントは日本語 |
| デプロイ先 | 未確定（タスクごとに最適化）。ローカル開発が出発点 |

### 1.2 設計原則（再掲）

`docs/personas/tech_lead.md` §4 より:

- **Boring Technology** を選ぶ勇気 — 派手より retention
- **車輪の再発明は最低限** — OSS / SaaS で解ける問題は買う
- **読みやすさは性能** — チーム生産性が最大の non-functional requirement
- **Working Backwards from API** — 利用者の手元のコードから設計を始める

これらを実装層に落としたものが本 ADR である。

---

## 2. Decision（決定）

### 2.1 既定スタック早見表

| レイヤ | 既定の選択 | 主な理由（後段で詳述） |
|--------|-----------|----------------------|
| 言語: Web/Backend | **TypeScript（Node.js 22 LTS）** | チーム横断で 1 言語、エージェント間レビューが速い |
| 言語: iOS | **Swift 6 + SwiftUI** | Apple 純正・長期保守性 |
| 言語: Android | **Kotlin + Jetpack Compose** | Google 純正・長期保守性 |
| 言語: スクリプト/教材 | **Python 3.12** | python-pptx / 既存ツール資産との親和性 |
| Web フロント | **Next.js 15（App Router）** | フルスタック構築、SSR/RSC、Vercel と直結 |
| 状態管理（Web） | **TanStack Query（サーバ状態）+ Zustand（UI 状態）** | Redux 不要、学習コストが低い |
| Backend フレームワーク | **Hono**（軽量 API）/ Next.js Route Handlers（フルスタック内） | エッジ/Node 両対応、API 中心の薄い層 |
| データベース | **PostgreSQL 16**（Supabase or Neon） | 標準 SQL、SaaS で運用負荷ゼロ |
| ORM / クエリ | **Drizzle ORM** | 型安全 + 生 SQL に近い、移行コストが低い |
| 認証 | **Clerk**（外部 IdP 連携多用時）/ **Supabase Auth**（DB と同居時） | OAuth 自前実装回避 |
| ホスティング: Web | **Vercel**（Hobby / Pro） | Next.js と直結、ゼロコンフィグ |
| ホスティング: API | **Vercel Functions** または **Fly.io**（長時間 worker） | 段階的にスケール、ベンダロックは限定的 |
| オブジェクトストレージ | **Cloudflare R2**（S3 互換、エグレス無料） | コスト面の安心感 |
| Monorepo | **pnpm workspaces + Turborepo** | サブリポ内マルチパッケージ時の標準 |
| パッケージマネージャ | **pnpm**（Node）/ **uv**（Python） | 高速・disk 効率 |
| CI/CD | **GitHub Actions** | repo と同居、無料枠で十分 |
| テスト | **Vitest**（unit）/ **Playwright**（E2E）/ **Pytest**（Python） | 既定の主流、エージェントの素養と一致 |
| Lint/Format | **Biome** | ESLint+Prettier の代替、設定 1 ファイルで完結 |
| 型チェック | **TypeScript strict** + **tsc --noEmit** in CI | 言うまでもなく |
| ロギング | **Pino**（Node）/ **structlog**（Python） | 構造化ログ既定 |
| エラー監視 | **Sentry** | 多言語対応、無料枠で初期は十分 |
| メトリクス/分析 | **Vercel Analytics**（Web）/ **Axiom**（ログ集約） | SaaS で軽量 |
| シークレット管理 | **`.env`（git 管理外）+ Vercel/CI の Secrets** | クラウドの KMS は導入後で良い |
| IaC | **当面なし**（SaaS Web UI で管理） | Terraform は規模が見えてから |
| ドキュメント形式 | **Markdown**（Notion・GitHub 双方で読める） | 統一の最強選択 |
| 研修資料: スライド | **Marp**（Markdown→PDF/PPTX） | コードレビュー可能なスライド |
| 研修資料: pptx 出力 | **python-pptx**（ブランドカラー `#000080`） | プロジェクト規約準拠 |
| 研修資料: 図解 | **Mermaid**（diagrams as code） | git diff 可能 |

### 2.2 Mobile スタックの方針

- **既定はネイティブ**（iOS=Swift/SwiftUI、Android=Kotlin/Compose）
- **例外的にクロスプラットフォーム**: 「Web/Mobile で 80% 以上のロジックを共有したい」
  「単純な業務アプリ」「期日が極端に厳しい」のいずれかを満たす場合のみ
  **React Native (Expo SDK)** を許容
- **Flutter は当面採用しない**（理由は §3.2）
- 採用判断は ADR で個別に残す（本 ADR からの逸脱を見える化）

### 2.3 サブリポジトリ初期化方針

「**雛形リポは作らない、初期化チェックリスト + 単一テンプレートリポ**」を採用。

- **理由**: 雛形リポ（複数）は陳腐化が早い。1 ファイルのチェックリストの方が
  保守コストが低い
- **実装**:
  - `docs/subrepo-init-checklist.md`（別 ADR で起案）に「最小ファイル一覧と
    `gh repo create --template` の手順」を 1 ページにまとめる
  - 単一テンプレートリポ `multi-agent-template`（GitHub の Template repository）を
    別途用意。`create from template` でクローン → サブリポ名にリネーム
  - テンプレートは「TypeScript モノレポ + GitHub Actions + Biome + Vitest」の最小構成
- **テンプレートが合わないタスク**（iOS 単体・Python 教材等）は手動で初期化し、
  チェックリストで漏れを防ぐ

### 2.4 サブリポ命名規約

- 形式: `mat-<purpose>` （`mat` = Multi-Agent Team の略）
- 例: `mat-notion-watcher`（通知レイヤ）/ `mat-training-2026q2`（研修資料）
- 本ハブリポ `multi-agent-team` は例外（既存名を維持）

---

## 3. Considered Alternatives（却下した代替案）

### 3.1 言語・ランタイム

#### 却下 A: Bun を Node.js より優先採用

- **却下理由 1**: 2026-04 時点で Bun は急速に成熟しているが、企業ユースの SaaS や
  ライブラリ（Sentry / Vercel SDK 等）の挙動検証が Node.js ほど蓄積されていない
- **却下理由 2**: Boring Technology 原則。Node 22 LTS で十分速く、エージェントの
  ナレッジ密度が高い
- **再考の閾値**: Bun の Node 互換性が「主要 SaaS が Bun を一級サポート」と公式
  表明し始めたら ADR を更新する

#### 却下 B: Go を Backend 既定に採用

- **却下理由 1**: TS/Node に揃えることで FE/BE のレビュー観点が統一できる
  （ペルソナ §4「読みやすさは性能」）。Go 採用は 2 言語化の管理コストを生む
- **却下理由 2**: 高並列・低レイテンシが要件にある特定タスクで Go を選ぶ余地は残す
  が、既定にはしない
- **再考の閾値**: Backend 単体の P95 < 50ms / RPS > 10k クラスの非機能要件が
  常態化したら採用検討

### 3.2 Mobile

#### 却下 C: Flutter

- **却下理由 1**: Dart という追加言語の学習・レビューコスト。本チームは既に
  Swift/Kotlin/TypeScript の 3 言語を扱う前提で、4 言語目は害が利を上回る
- **却下理由 2**: ネイティブ機能（Apple Pay / Health / WidgetKit / Live Activities）
  の追従が React Native + Expo の方が早い場面が多い
- **再考の閾値**: クロスプラットフォーム要件かつ Web シェアが薄いタスクで
  React Native では性能面の壁にぶつかった場合のみ

#### 却下 D: クロスプラットフォーム（RN/Flutter）を既定にする

- **却下理由 1**: ネイティブ機能の品質要求が読めない初期段階で、共通コード資産が
  ない状態でクロスプラットフォームを既定にすると「両プラットフォームで微妙に動かない」
  問題に時間を取られる
- **却下理由 2**: チームに iOS/Android のネイティブ知見を必ず持たせるためにも
  最初の 1 本はネイティブが適切

### 3.3 データベース

#### 却下 E: Firebase / Firestore を既定 DB に採用

- **却下理由 1**: SQL がない・複雑な集計に弱い・ベンダロックが強い
- **却下理由 2**: 研修・Backend など SQL ベースの要件が多く、PostgreSQL の方が
  汎用
- **再考の閾値**: リアルタイム同期が中核機能のタスクが常態化した場合に部分採用

#### 却下 F: 自前 PostgreSQL を VPS で運用

- **却下理由 1**: バックアップ・パッチ・モニタリングの運用負荷を SaaS（Supabase/Neon）
  が肩代わりしてくれる
- **却下理由 2**: 少数精鋭のチームで運用コストを払う段階ではない

### 3.4 ホスティング

#### 却下 G: AWS フルスタック（ECS/EKS + RDS + CloudFront）を既定

- **却下理由 1**: 初期段階で AWS の権限・ネットワーク設計に時間を取られる
  ROI が悪い。SaaS（Vercel / Supabase / Cloudflare）で同等以上の速度
- **却下理由 2**: IaC（Terraform/CDK）の導入コストも初期段階では過剰
- **再考の閾値**: コンプライアンス要件（VPC 必須・専用線・SOC2 等）または
  月額インフラ費が SaaS で合計 $500/月 を超えたタイミング

#### 却下 H: Cloudflare Workers をデフォルト Backend ランタイムに採用

- **却下理由 1**: Edge 制約（Node API の互換性 / 一部ライブラリ非対応）の罠が
  多く、デバッグが Vercel Functions / Node ランタイムより難しい
- **却下理由 2**: 「迷ったらこれ」の既定としては学習曲線が立つ
- **使う場面**: 静的アセット配信は Cloudflare、API/関数は Vercel から始め、
  Edge 性能要件があるタスク単位で Workers を採用する

### 3.5 アーキテクチャ

#### 却下 I: 初期からマイクロサービス分割

- **却下理由 1**: Conway's Law。エージェント数（≤5 名）に対してサービス分割が
  過剰。デプロイ単位の管理コストが利益を上回る
- **却下理由 2**: モジュラーモノリス → サービス境界が見えてから分割、の方が手戻り
  少ない（Stripe/Shopify 系の経験則）
- **再考の閾値**: 単一リポのビルド時間が 10 分超 / 異なるデプロイサイクルの
  サービスが明確化した場合

#### 却下 J: GraphQL を API 既定に採用

- **却下理由 1**: スキーマ管理・N+1・キャッシュ設計のオーバーヘッドが、本チームの
  少数精鋭規模では割に合わない
- **却下理由 2**: TS の型を共有する **tRPC** または **REST + Zod** で十分なケースが
  ほとんど
- **再考の閾値**: 外部公開 API で「クライアント側がフィールドを選びたい」要件が
  明確になったら検討

### 3.6 リント / フォーマッタ

#### 却下 K: ESLint + Prettier の組合せ

- **却下理由 1**: 設定ファイルが分散し、サブリポ初期化のテンプレが膨らむ
- **却下理由 2**: Biome は単一バイナリ・1 設定ファイルで同等の機能を提供し、
  起動が桁違いに速い（ローカル & CI 双方で効く）
- **使う場面**: Biome がカバーしないルール（特定 React フックの厳格チェック等）が
  必要になったら部分的に併用

---

## 4. Consequences（帰結）

### 4.1 ポジティブ

1. **レビュー観点の統一**: TS が共通言語になることで、エージェント間の PR レビュー
   速度が上がる
2. **サブリポ初期化が高速**: テンプレートリポ + チェックリストで「最初の 1 コミット
   までの時間」を分単位に短縮できる
3. **運用負荷ゼロ**: SaaS 中心で、PM/Tech Lead がインフラ運用に時間を割かなくて済む
4. **歴史化の連続性**: ドキュメントが Markdown 一本で揃うため pptx 集約（`#000080`
   ブランドカラー、CLAUDE.md §3.3）の自動化が容易

### 4.2 ネガティブ・リスク

1. **SaaS 単一障害点**: Vercel / Supabase / Notion がいずれも障害発生時に業務停止
   （Notion MCP 障害は `docs/history/2026-04-25_notion-mcp-adoption.md` §7 で既出）
   - **緩和策**: SaaS 横断の障害が連鎖した場合の手順を別 ADR で起案予定
2. **コスト増加**: スケール時に Vercel/Supabase 上位プランへの移行が必要になり、
   AWS セルフホストより割高になり得る
   - **緩和策**: コストが月 $500/月 を超えたら IaC + 自前移行を検討（§3.4 G の
     再考閾値と一致）
3. **Boring 採用の機会損失**: Bun / Edge Workers / GraphQL 等の新技術キャッチアップが
   遅れるリスク
   - **緩和策**: 各却下案に「再考の閾値」を明示済み。閾値到達時は ADR を更新する
4. **言語混在の運用**: TS / Swift / Kotlin / Python の 4 言語を扱う前提のため、
   各言語の Lint/CI/テスト基盤を維持する責任が Tech Lead に集中する
   - **緩和策**: 言語ごとのチェックリストをテンプレートに同梱、Tech Lead 単独で
     維持できる粒度に絞る

### 4.3 影響範囲

- **既存リポ**: 本ハブ `multi-agent-team` は既に Markdown のみ。影響なし
- **新規サブリポ**: 本 ADR 承認後、初回サブリポ作成時にテンプレートリポを起こし、
  以降のサブリポはテンプレ + チェックリストから派生
- **CI**: GitHub Actions の最小ワークフロー（lint / type-check / test）を
  テンプレートに同梱

---

## 5. 開いている論点（PM 承認・議論で動かしたい点）

> 「**強い意見を弱い保持で**」の精神。以下は議論で動く可能性のある点を明示する。

1. **Vercel 中心のホスティング** — 国内案件で Vercel/Cloudflare がコンプライアンス的に
   選べないシナリオが PM の手元にあれば、Render/Fly.io 中心へスライド検討
2. **Clerk の採用** — 個人情報の海外保管に懸念があるケースがあれば Supabase Auth に
   寄せる
3. **Marp + python-pptx の研修資料スタック** — PM 神崎が想定する研修案件で別ツール
   指定があれば差し替え可能
4. **テンプレートリポ運用 vs ADR 単独** — テンプレリポを別途立てる工数が許容できない
   場合、初期はチェックリストのみで運用する案も残す

---

## 6. References（関連資料）

- `docs/personas/tech_lead.md` — Tech Lead ペルソナ（決定原則の出典）
- `docs/persona.md` — PM ペルソナ
- `CLAUDE.md` §4 リポジトリ構成 / §5 Git 運用
- `docs/history/2026-04-25_tech-lead-activation-decisions.md` — 起用方針
- `docs/history/2026-04-25_notion-mcp-adoption.md` — SaaS 単一障害点リスクの先行議論
- `docs/history/2026-04-25_branching-strategy.md` — ブランチ運用との整合
- `docs/history/2026-04-25_default-tech-stack-decisions.md`（本 ADR とともに起案）
