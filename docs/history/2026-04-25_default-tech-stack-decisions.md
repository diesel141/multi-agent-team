---
date: 2026-04-25
type: decision / tech-stack
title: 既定の技術スタック策定（ADR-0001 起案）
status: 提案（PM 承認待ち）
tags: [tech-stack, architecture, adr, boring-technology]
---

# 既定の技術スタック策定（ADR-0001 起案）

## 1. 背景

TASK-0001（PM 神崎発、Tech Lead 早瀬受領）の成果物 1 として、本プロジェクトの
**既定スタック**を ADR-0001 (`docs/adr/0001-default-tech-stack.md`) で起案した。
本歴史メモはその意思決定の **要点と前提**を pptx レポート用に圧縮して残すもの。

ADR 本体に詳細な比較表があるため、本ファイルは「未来の自分が読んで判断軸を再現できる」
粒度に絞る。

## 2. 採用の幹（Trunk decisions）

| 軸 | 採用 | 一行根拠 |
|----|------|---------|
| 共通言語 | TypeScript | FE/BE 横断で 1 言語、エージェント間レビューが速い |
| Web | Next.js 15 + Vercel | フルスタック・運用負荷ゼロ |
| API | Hono / Next.js Route Handlers | エッジ/Node 両対応の薄い層 |
| Mobile | Swift/Kotlin（既定）/ React Native（例外） | ネイティブ機能追従とチーム言語数のバランス |
| DB | PostgreSQL on Supabase or Neon | SQL 標準・SaaS 運用 |
| ORM | Drizzle | 型安全 + 生 SQL に近い |
| 認証 | Clerk / Supabase Auth | 自前実装回避 |
| Lint | Biome | ESLint+Prettier の単一バイナリ代替 |
| 監視 | Sentry + Axiom + Vercel Analytics | SaaS で軽量 |
| 研修資料 | Marp + python-pptx（`#000080`） | git diff 可能 + ブランド規約準拠 |
| サブリポ初期化 | テンプレートリポ + チェックリスト | 雛形リポ複数の陳腐化を回避 |
| サブリポ命名 | `mat-<purpose>` | チーム所属を一目で識別 |

## 3. 重要な却下と「再考の閾値」

却下案には **再考の閾値** を明示しておく。これにより未来の Tech Lead が「いつ再検討
すべきか」をルール化できる（pptx の判断アーカイブとして価値が高い）。

| 却下案 | 却下理由（要約） | 再考の閾値 |
|--------|-----------------|------------|
| Bun を Node.js 優先 | SaaS 互換性の検証蓄積が薄い / Boring 原則 | 主要 SaaS が Bun を一級サポートと公式表明 |
| Go を Backend 既定 | 2 言語化のレビュー観点分散 | Backend 単体で P95 < 50ms / RPS > 10k 常態化 |
| Flutter | Dart 学習コスト・ネイティブ機能追従の遅さ | RN で性能の壁にぶつかった場合のみ |
| Firebase/Firestore | SQL 不在・ロックイン | リアルタイム同期が中核機能のタスク常態化 |
| AWS フルスタック既定 | 初期段階の権限/IaC コストが過剰 | 月額 SaaS 費 > $500 もしくは VPC 必須要件 |
| Cloudflare Workers 既定 | Edge 制約の罠が多くデバッグが難しい | Edge 性能要件のあるタスク単位で個別採用 |
| 初期マイクロサービス | Conway's Law / 規模に対し過剰 | 単一リポビルド 10 分超 or デプロイサイクル分離 |
| GraphQL 既定 | スキーマ運用コスト / N+1 / キャッシュ | 外部公開 API でフィールド選択要件が明確化 |
| ESLint+Prettier | 設定分散・起動遅 | Biome 未対応の厳格ルールが必要な部分のみ併用 |

## 4. 設計原則の埋め込み

ADR-0001 は Tech Lead ペルソナ（`docs/personas/tech_lead.md` §4）の以下を実装層へ落とした:

- **Boring Technology** — Bun/Flutter/Workers を「再考の閾値」付きで却下
- **車輪の再発明は最低限** — Vercel/Supabase/Clerk/Sentry を SaaS で買う
- **読みやすさは性能** — TS で言語統一しレビュー速度を最大化
- **Working Backwards from API** — Hono/Next Route Handlers の薄い層で型を共有

「**強い意見を弱い保持で**」の方針も反映し、ADR §5 で「議論で動かしたい論点 4 件」を
明示している。

## 5. リスクと緩和策（要点）

| リスク | 緩和策 |
|-------|--------|
| SaaS 単一障害点（Notion / Vercel / Supabase） | 連鎖障害時の運用手順を別 ADR で起案予定 |
| スケール時のコスト増 | 月 $500/月 を超えたら IaC + 自前移行検討（AWS 却下案の閾値と一致） |
| Boring 採用の機会損失 | 各却下案に再考の閾値を明示済 |
| 4 言語の運用負荷集中 | 言語別チェックリストをテンプレートに同梱、Tech Lead で維持可能な粒度に絞る |

## 6. なぜこれを残すか（歴史化の理由）

1. **Tech Lead 起用後の最初の判断**として、本プロジェクトの技術アイデンティティを
   形作る決定。pptx レポートの「Phase 1: 土台」章の中核資料となる
2. **却下案と再考閾値の組** が後続 Tech Lead の意思決定をスケールさせる。
   「なぜ採らなかったか」を言語化しておくことで、毎回ゼロから議論しなくて済む
3. **PM とのスコープ境界の明示**として、§5 の「議論で動かしたい論点」が
   Tech Lead/PM の責任分担（`docs/personas/tech_lead.md` §5）の運用例になる

## 7. 関連ドキュメント

- `docs/adr/0001-default-tech-stack.md` — ADR 本体（本歴史メモの一次資料）
- `docs/personas/tech_lead.md` — 設計原則の出典
- `docs/history/2026-04-25_tech-lead-activation-decisions.md` — 起用判断の前提
- `docs/history/2026-04-25_notion-mcp-adoption.md` — SaaS 単一障害点の先行議論
- `docs/notion-messages/2026-04-25_001_tech-lead-onboarding.md` — TASK-0001 開始指令
