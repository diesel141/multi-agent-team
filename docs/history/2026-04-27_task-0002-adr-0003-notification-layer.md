---
date: 2026-04-27
type: decision / architecture
title: TASK-0002 ADR-0003 通知レイヤ実装方式の決定
status: ADR 起案完了 / PM 受入待ち
tags: [adr, notification, vercel-cron, notion, mat-board-watcher, history]
---

# TASK-0002 ADR-0003 通知レイヤ実装方式の決定

## 1. 背景・経緯

- TASK-0002 は元来「BE ペルソナ起案 + 通知レイヤ初期設計」のセット
- ADR-0006 §5.1 で「ペルソナ起案 = PM の正規ルート」と確定したため、BE ペルソナ部分は TASK-0011 に分離（PR #17 / commit `4beab20` でマージ済）
- 本タスクは残スコープ「ADR-0003 通知レイヤ実装方式の起案」のみを担当
- `docs/history/2026-04-25_multi-agent-architecture-reference.md` §4 で「Tech Lead アサイン後に委ねる」と保留されていた論点を、Tech Lead 早瀬が本 ADR で決着

## 2. 採用案サマリ

**Vercel Cron + Notion Search API による中央集約ポーリング（phase1）**

- Vercel Cron Functions が 1 分間隔で Notion Messages DB の `last_edited_time` 差分を取得
- cursor は Vercel KV に CAS 更新で永続化
- ローカル PC 側で動く Node CLI Notifier に署名付き HTTPS POST → `tmux send-keys` で各 psmux ペインに **短い wake-up シグナル** を投入（業務本文は流さない、参照実装思想を継承）

### 5 評価軸 P95 数値

- レイテンシ: P50 30 sec / P95 90 sec
- レート制限消費: 0.017 req/s（Notion 平均 3 req/s 制限の 0.6%）
- 障害モード耐性: cursor 永続化により Vercel 復旧後の取りこぼしゼロ
- 初期コスト: $0/month（Vercel Hobby + Vercel KV 無料枠）
- 近期拡張性: phase2 で Webhook 化に差し替え可能（dispatcher 層を共有）

## 3. 却下案と再考閾値（5 件）

| # | 案 | 主な却下理由 | 再考閾値（測定可能 trigger） |
|---|----|-----------|----------------------------|
| A | short-interval setInterval ローカル常駐ポーリング | ローカル PC 常時稼働非保証 / Vercel KV 案より状態同期難 | UPS/自動起床つき常時稼働ホスト + sub-minute SLA 必須化 |
| B | Notion 公式 Webhook + Vercel Functions 受け皿 | Webhook DB scope 未 GA / 中継 SaaS 必須 / phase1 SLA に過剰 | (a) 公式 Webhook GA + (b) 中継 SaaS 不要 + (c) P95 < 10 sec SLA |
| C | chokidar / FileSystemWatcher + docs/history 代理シグナル | 歴史化原則と逆向き / カバレッジ不完全 / PC 依存 | 歴史化と通知の event sourcing 統合再設計（別 ADR） |
| D | 参照実装直系 YAML inbox + Notion 二次降格 | ADR-0005 通信プロトコルを覆す / 単一 writer 維持に難 | Notion 連続障害 四半期 2 回以上 / air-gap 環境への移行 |
| E | GitHub Actions cron + ポーリング | cron 粒度 5-15 min で P95 10x 悪化 / ロギング分散 | Vercel Cron 有償化 / Actions cron 1 min 化公式化 |

## 4. mat-board-watcher サブリポ初期化方針

- 命名: `mat-<purpose>` 規約準拠（ADR-0001 §2.4）
- スタック: TS / pnpm + Turborepo / Hono on Vercel Functions / Vercel KV / Biome / Vitest
- ディレクトリ: `apps/api`（Vercel Functions）+ `packages/{notion-client, state, dispatcher}` + `tools/local-notifier`
- CI: GitHub Actions で lint / typecheck / test
- デプロイ: Vercel の Git 連携（development → preview / main → production）
- **`multi-agent-template` は未起票** — 暫定方針として「mat-board-watcher を事実上の最初のテンプレ実装」とし、後追いで `multi-agent-template` を抽出（§6 開いている論点 (4)）

## 5. 開いている論点（PM 承認で動かす可能性）

1. ポーリング間隔の確定（1 min vs 5 min vs 30 sec）
2. Webhook 移行条件の優先順位（GA / リレー不要 / SLA 強化）
3. ハイブリッド（Cron + ローカル Watcher）への phase3 移行タイミング
4. `multi-agent-template` の起票タイミング（先 or 後追い）
5. mat-board-watcher の運用責任者（BE / Tech Lead / SRE 未起用期）
6. send-keys 通知規律の CI 自動検証（payload 長制限など）

## 6. 学び・ハイライト

### 6.1 「通知レイヤ未決」が本当の律速だった

BE ペルソナ採択（TASK-0011）後に通知レイヤを着手するのが当然だが、本来この問題は ADR-0001 / ADR-0002 起案時にも顕在化できたはず。**「実装メンバーが決まる前に運用速度の律速ポイントを明示する」** という観点を ADR-0001 系列の起案フローに織り込む価値がある（次回 ADR 起案時の自己レビュー観点に追加候補）。

### 6.2 段階導入で再考閾値を 3 段に分けた

phase1（採用案）/ phase2（Webhook）/ phase3（ハイブリッド）の **段階移行条件を全て測定可能 trigger で書く** ことで、後続 Tech Lead が「いつ何を見直すか」を判定できる構造になった。これは ADR ハウススタイル `memory/adr_house_style.md` の運用例として再現価値がある。

### 6.3 send-keys 「通知のみ」規律をコード型レベルで縛る発想

CLAUDE.md §1.2 の「send-keys 業務通信禁止」を ADR §4.2 緩和策で **dispatcher 層の型ガード + payload 文字列正規表現制限** まで具体化した。規律をドキュメントだけでなくコードで縛る設計は、本 PJ の他の規律（worktree 禁止 / 種別必須 / etc.）にも応用しうる。

### 6.4 後続タスクへの引き継ぎ

- TASK-0012（想定）: BE 久遠周が `mat-board-watcher` サブリポを初期化、本 ADR §5 の受入基準を満たす実装
- ADR-0007（PM 起案検討中）: 本 ADR §6 開いている論点 (1)(2)(4) を統合する PM 主導 ADR の候補

## 7. 関連資料

- `docs/adr/0003-notification-layer-design.md` — 本決定の本体
- `docs/adr/0001-default-tech-stack.md` — 既定スタック
- `docs/adr/0005-communication-protocol-revision.md` — 通信プロトコル
- `docs/adr/0006-persona-creation-flow-and-role-recalibration.md` — 権限境界（PR レビュー＆マージ Tech Lead）
- `docs/history/2026-04-25_multi-agent-architecture-reference.md` §4 — 元の未決問題
- `memory/adr_house_style.md` — ADR ハウススタイル
