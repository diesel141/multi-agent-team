# ADR-0008: 通知レイヤを能動 fetch 方式へピボット（ADR-0003 部分 Superseded）

- 状態: **Proposed**（PM 起案 / Tech Lead レビュー & マージ前提・ADR-0006 §5.2 / ADR-0007 §2.6）
- 起案日: 2026-04-29
- 起案者: PM 神崎 玲奈
- 関連: `docs/adr/0003-notification-layer-design.md` / `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` / `docs/history/2026-04-29_adr-0008-notification-layer-pivot.md`（本 ADR と同時起票）/ `CLAUDE.md` §1.3 / `memory/feedback_pm_saas_limit_verification.md` / `memory/feedback_pm_proactive_review.md` / `memory/adr_house_style.md`

---

## 1. Context（文脈）

### 1.1 ADR-0003 採用後の連鎖罠

ADR-0003（Vercel Cron + Notion Search API ポーリング + ローカル Notifier + tmux send-keys wake-up）採用後、TASK-0016〜0019 で 4 段階の罠を踏んだ:

| # | タスク | 罠 | 解消結果 |
|---|--------|----|---------|
| TASK-0016 | Vercel Cron 1 min 採用 | Vercel Hobby plan は **1 日 1 回制限**（Pricing/Limits ページに別記載 / 採用時独立検証漏れ） | 却下 → GitHub Actions cron 外部化に切替 |
| TASK-0017 | GitHub Actions cron で外部化 | 単独では成功 / end-to-end 未達 | スコープ内完了 |
| TASK-0018 | Vercel build / routing 修正（3 段階） | "No Output Directory" / Hono `[[...route]].ts` Next.js 前提 / catch-all → index.ts + rewrites に統一 | build / routing 解消 / Function 500 検出 |
| TASK-0019 | FUNCTION_INVOCATION_FAILED 修正 | runtime 表記修正で preview 500 不変 → vercel logs 取得に Vercel CLI 認証ブロッカー | 却下（本 ADR 採択により撤退） |

各踏み方は単独では ADR ハウススタイル（採用 + 却下 + 再考閾値）を守って前進していたが、**「採用したスタックの実機動作経験が誰にも無い」** という構造的欠陥が事前検知されないまま 200+ 行のコードを投じた状態に至った。

### 1.2 shogun 比較分析（再参照のタイミング）

`docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` の「思想を援用 / 直接フォークしない」結論は当時正しかったが、ADR-0003 起案時に shogun の **実装層**（クラウド deploy 不使用 / Notion mcp は能動 fetch のみ / 通知レイヤは tmux + inotifywait）を再参照していなかった。

shogun は本 PJ と同種の「Claude Code 多エージェント運用」を成立させながら **「Notion 新着の自動 wake-up 通知」自体を持っていない**。`claude mcp add notion` だけで mcp サーバーをぶら下げ、エージェントは起動時に能動 fetch する設計。

| 観点 | shogun | 本 PJ ADR-0003 |
|------|--------|----------------|
| Notion 連携 | `claude mcp add notion` のみ（能動 fetch） | mcp + Vercel Cron polling + Cloudflare Tunnel + ローカル Notifier |
| 自動 wake-up 通知 | **無し**（エージェントは起動時に能動 fetch） | あり（tmux send-keys 経由） |
| クラウド deploy | 無し（Tailscale でリモート可） | mat-board-watcher → Vercel |
| Windows サポート | WSL2 + Ubuntu | psmux + Windows ネイティブ |

つまり、ADR-0003 で立てた「Notion 掲示板 → 自動 wake-up 通知レイヤ」要件 **そのものが、運用上は不要** だった可能性が高い。

### 1.3 現セッションの能動 fetch 検証

本セッション（2026-04-28〜29）で PM が以下をすべて **「Notion mcp で能動 fetch + Task / Bash ツールで召喚」** で完遂している:

- TASK-0019 起票 / BE 召喚 / TASK-0017 / 0018 PM 受入レビュー / chore PR #23 起票

mat-board-watcher が止まっていても運用に支障が出ていない事実が、§1.2 の評価を実証している。

---

## 2. Decision（決定）

### 2.1 通知レイヤの撤去

ADR-0003 §2.1 採用案（Vercel Cron + Cloudflare Tunnel + ローカル Notifier (HTTPS POST → tmux send-keys)）の通知パスを **撤去**。

| 撤去対象 | 措置 |
|---------|------|
| Vercel project `mat-board-watcher` | **削除済**（2026-04-29 ユーザー Web UI 操作 / env vars 5 件も連動消滅） |
| GitHub Actions secrets（`CRON_SECRET` / `PRODUCTION_POLL_URL`） | **削除済**（2026-04-29 PM gh CLI 代行） |
| GitHub Actions `Cron Poll` workflow | schedule トリガー削除（PR #12 / リポ削除に伴い消滅） |
| Cloudflare Tunnel `notifier.141plot.org` + DNS record | **削除済**（2026-04-29 / プロセス Ctrl+C → Tunnel resource → DNS CNAME を順次ユーザー Web UI で削除完了） |
| mat-board-watcher リポ | **GitHub から完全削除**（2026-04-29 / ユーザー D2 判断 / ローカル clone は任意保存 / phase2 復活時は別リポ起票） |
| ローカル Notifier (`tools/local-notifier`) / `dispatcher` 層 / `tmux send-keys` wake-up | リポ削除に伴い GitHub からは消滅（ローカル clone のみ任意保存） |

### 2.2 wake-up 機能の代替（採用案: ユーザー起動 + 能動 fetch）

| シーン | 旧（ADR-0003 想定） | 新（ADR-0008 採用） |
|--------|--------------------|---------------------|
| 新着メッセージ検知 | Vercel Cron が 1 min ポーリング | **PM / 各ロールがセッション開始時に Notion mcp で能動 fetch** |
| 他エージェントの召喚 | tmux send-keys wake-up | **ユーザー（上様）が `/<role>` slash command で次エージェントを起動 / または Task ツール / 外部プロセス起動** |
| メッセージ取りこぼし防止 | KV cursor で last-seen 管理 | **能動 fetch 時に投稿日時 desc で取得、Notion 上に「ステータス＝未着手」が残る限り消えない（Notion 自体が persistence）** |

### 2.3 ADR-0003 の Superseded 範囲（粒度明示）

**Superseded by ADR-0008**:
- §2.1 採用案（Vercel Cron + ポーリング + Notifier + send-keys wake-up）
- §5 サブリポ初期化方針（mat-board-watcher の Vercel deploy 構成）
- §5.5 受入基準 7 項目（`/api/cron/poll` 200 等の end-to-end 動作確認）

**継続有効**:
- §3 却下案 A〜F + 各再考閾値（将来再起動時の判断材料）
- §5.4 認証経路（Notion mcp Internal Integration / OAuth 並存）
- §6 開いている論点（phase2 候補として保留）

ADR-0003 自体は archive せず、ヘッダに「**Superseded by ADR-0008（粒度: §2.1 / §5 / §5.5）**」を追記して履歴を残す。

---

## 3. Considered Alternatives（却下した代替案）

### 却下 A: 現アーキ継続（vercel logs → BE 再起動 → 500 解消）

- **却下理由 1**: TASK-0016〜0019 で 4 段階の罠を踏んでおり、Function 500 を解消しても次のニッチ罠（ADR-0003 §6 開いている論点 1, 2, 3, 5 残）を踏むリスクが高い
- **却下理由 2**: shogun 比較で「自動 wake-up 通知レイヤ自体が運用上不要」と判明した以上、根本対応にトークンとサイクルを投じる費用対効果が極めて低い
- **再考の閾値**: チーム規模が **6 ロール以上** + **同時稼働 4 ロール以上** + **1 日 10 メッセージ超** のいずれかが恒常化した時点で自動 wake-up 通知レイヤを再採用検討（その場合は本 ADR を Superseded する **将来の別 ADR**（ADR-0009 は通信プロトコル再改訂で消費済 / 起案時の最新番号を採番）を起案）

### 却下 B: shogun フル準拠（WSL2 + Ubuntu + tmux + inotifywait + flock + ローカル YAML inbox）

- **却下理由 1**: Windows + psmux + PowerShell + Notion 構成への投資（CLAUDE.md / docs/setup-psmux.md / 既存 ADR 群）が無駄になる
- **却下理由 2**: WSL2 移行コスト + Notion を YAML inbox に置き換える作業 + ペルソナ階層（shogun / karo / ashigaru）への再構築が、現状の PM / Tech Lead / Designer / BE 構成の利点（明示的責務分担 / ADR-0006 §5.2 権限境界）を捨てる
- **再考の閾値**: 「ローカル PC 24/7 稼働を業務前提化できる事業フェーズ」+「同時稼働ロール 4 以上 + リモートメンバー含む」の両方が成立した時点

### 却下 C: Notion 公式 Webhook + ngrok / Cloudflare Tunnel リレー

- **却下理由 1**: ADR-0003 §3 却下 B と同条件（Notion 公式 Webhook が phase2 候補 / 自前リレー不要が未到達）
- **却下理由 2**: Webhook を採用してもローカル PC 受信側で Tunnel 必須 → 現 ADR-0003 の Cloudflare Tunnel + ローカル Notifier と同じハマりどころに戻る
- **再考の閾値**: Notion 公式 Webhook の GA + 自前リレー不要化が確認された時点

### 却下 D: PowerShell `FileSystemWatcher` / Node `chokidar` でのローカル代替

- **却下理由 1**: 監視対象は SaaS（Notion）上にあり、ローカル FS 監視と同期層が別途必要 → 結局 Notion API ポーリング + 同期コードが必要で複雑度減らず
- **再考の閾値**: ローカル FS をプロジェクト一次ソースに変更する事業判断（shogun フル準拠 = 却下 B）と一体で検討

### 却下 E: ADR-0003 §6 開いている論点 (1)(2)(3)(5) を全て決議してから phase2 に進む

- **却下理由 1**: 開いている論点 1（ポーリング間隔）・2（Webhook 移行条件）・3（phase3 移行）の決議に追加で複数セッションかかる。その間 mat-board-watcher の 500 を解消する作業が継続。費用対効果が低い
- **却下理由 2**: 決議しても §1.2 shogun 比較で示した「通知レイヤそのものが過剰設計」の構造的疑念は解消されない
- **再考の閾値**: 該当なし（永久保留は採用しない / phase2 復活時には ADR-0009 で改めて再起案）

---

## 4. Consequences（帰結）

### 4.1 ポジティブ

1. **連鎖罠ゾーンから脱出** — Vercel Functions runtime / pnpm workspace bundle / Cloudflare Tunnel / Vercel Hobby cron 制限の複合罠を一括離脱
2. **既存資産の保全** — 本リポ（multi-agent-team）の核（ペルソナ / Notion mcp / ハイブリッド通信プロトコル / ADR ハウススタイル / chore PR #23 ADR-0007 派生整理）は無傷
3. **shogun 比較で運用コア確認済** — Notion mcp + 能動 fetch + ユーザー起動の最小構成で PM 業務が回ることを本セッション中に実証
4. **歴史化アーカイブの濃度向上** — TASK-0016〜0019 の踏破経験が `docs/history/` + ADR 群に保存され、再起動時の判断材料になる

### 4.2 ネガティブ・リスク

1. **mat-board-watcher の実装投資が完全消失（D2 + L1 採択 / 2026-04-29）** — phase1 で書いた 200+ 行（dispatcher / notion-client / state / cron-poll handler / vercel.json / GitHub Actions workflow）は GitHub + 個人ローカル clone とも削除
   - **緩和策**: phase2 復活時は新規リポを起票し、ADR-0003 / ADR-0008 / 本歴史化メモ §1〜§5 を一次ソースとして起案。コード本体は失われたが、設計判断・採用案・却下案・再考閾値は ADR / 歴史化メモに完全保存
2. **自動 wake-up 不在による「次セッション着手の遅延」** — ユーザーが Notion 新着に気付かないとセッション再開が遅れる
   - **緩和策**: ユーザーが手動で Notion を覗く運用 / 重要な進捗は PM が能動的にユーザーに報告（既に動いている運用）
3. **shogun 比較分析の遅延が引き起こした手戻り** — ADR 起案時に関連歴史化メモを再読する規律が無かったことの代償
   - **緩和策**: 本 ADR 採択時に新規 feedback memory「ADR 起案時は関連歴史化メモを全件再読 / 採用スタックの実機踏破経験を独立検証」を恒久化（同時起票の歴史化メモ §5 学び）
4. **PR #23 (ADR-0007 派生整理) のマージ前後の整合性** — chore PR #23 マージ前の development を base に本 PR を起票するが、ADR-0007 §2.1 / §2.6 / pm-self-review.md への参照は脚注追加のみのため衝突なし
   - **緩和策**: Tech Lead レビュー時に PR #23 を先にマージしてから本 PR をリベース、または本 PR から先にマージしてから PR #23 をリベース、どちらでも mergeable

### 4.3 影響範囲

| ファイル / リポ | 変更内容 |
|----------------|---------|
| `docs/adr/0008-notification-layer-pivot.md` | 新規（本 ADR） |
| `docs/adr/0003-notification-layer-design.md` | ヘッダに Superseded 注記 + 粒度明示 |
| `CLAUDE.md` §1.3 | 通知レイヤ運用方針の節を追加（能動 fetch の明文化） |
| `docs/history/2026-04-29_adr-0008-notification-layer-pivot.md` | 新規（連鎖罠経緯 + shogun 比較 + 学び） |
| mat-board-watcher リポ | **GitHub 削除済**（2026-04-29 / ユーザー D2 判断）/ 凍結 PR #12 は close 連動消滅 |
| Vercel project / GitHub Actions secrets | **削除済**（2026-04-29 / Vercel = ユーザー UI / secrets = PM gh CLI 代行） |
| Cloudflare Tunnel `notifier.141plot.org` + DNS record | **削除済**（2026-04-29 / プロセス停止 → Tunnel resource 削除 → DNS CNAME 削除を順次完了） |

---

## 5. 開いている論点（PM 議論で動かしたい点）

1. **能動 fetch の運用粒度標準化** — PM / Tech Lead / Designer / BE が各セッション開始時に Notion mcp で fetch する頻度・対象範囲を共通プロローグ `docs/templates/instructions/_common-prologue.md` に追記すべきか。**測定方針**: 1 ヶ月運用後に「メッセージ取りこぼし件数 / 重複応答件数」を点検
2. **チーム規模拡大時の自動 wake-up 復活閾値** — §3 却下 A 再考閾値「6 ロール以上 + 同時稼働 4 + 1 日 10 メッセージ超」の妥当性は半年後（2026-10-29 頃）に実測値で再評価
3. **mat-board-watcher リポの最終処置** — **決議済（2026-04-29 ユーザー D2 判断）**: GitHub 上から完全削除。phase2 復活時は新規リポを起票し ADR-0003 / ADR-0008 / 歴史化メモを一次ソースとする
4. **shogun 流 WSL2 ピボットの検討タイミング** — §3 却下 B 再考閾値「ローカル PC 24/7 稼働を業務前提化できる事業フェーズ」が成立した時に検討
5. **PR #23 (ADR-0007 派生整理) と本 ADR の merge 順序** — §4.3 整合性リスクの実運用判断（Tech Lead 領域）

---

## 6. References（関連資料）

- `docs/adr/0003-notification-layer-design.md` — Superseded（粒度: §2.1 / §5 / §5.5）
- `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` — shogun 通信レイヤ参照 + 本 ADR §1.2 で再評価
- `docs/history/2026-04-29_adr-0008-notification-layer-pivot.md` — 本 ADR と同時起票（連鎖罠 / shogun 比較 / 学び）
- `CLAUDE.md` §1.3 — 通信プロトコル（本 ADR で能動 fetch 運用を明示）
- `memory/feedback_pm_saas_limit_verification.md` — TASK-0016 由来規律（本 ADR の学び 1 で拡張候補）
- `memory/adr_house_style.md` — ADR ハウススタイル（採用 + 却下 + 再考閾値）
- shogun 参照リポ: <https://github.com/yohey-w/multi-agent-shogun>（更新 2026-04-28）
