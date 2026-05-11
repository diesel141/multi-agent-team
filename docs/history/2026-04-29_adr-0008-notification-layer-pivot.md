---
date: 2026-04-29
type: history / pivot-decision
title: ADR-0008 通知レイヤピボット（ADR-0003 部分 Superseded）
status: 採択時点の経緯記録
tags: [adr-0008, notification-layer, pivot, lessons-learned, 参照実装-comparison, mat-board-watcher]
---

# ADR-0008 通知レイヤピボット — 連鎖罠と 参照実装再確認の経緯

## 1. ADR-0003 採用後の 4 段階連鎖罠

### TASK-0016: Vercel Hobby cron 1 日 1 回制限見落とし

- ADR-0003 §2.1 で「Vercel Cron 1 min」採用
- 実装直前に Vercel Hobby plan の cron 制限が「1 日 1 回」と判明（Pricing/Limits ページの別記載）
- PM/Tech Lead 双方が ADR 採用時に Pricing ページを独立検証していなかった
- 規律化済: `memory/feedback_pm_saas_limit_verification.md`

### TASK-0017: GitHub Actions cron 外部化

- C 案改として「`*/5 * * * *` で GitHub Actions schedule + curl POST」採用
- handler 層 / 状態保持 / safety net は流用、トリガーだけ差し替えで 100/-24 行に収束
- スコープ内完了 / end-to-end 未達（後続 TASK-0018 と TASK-0019 への依存）

### TASK-0018: Vercel build / routing 修正（3 段階）

- 第 1 段: `apps/api/package.json` に `mkdir -p public` を追加（Turbo の 0 tasks 警告対策）→ Production deploy で同症状が再発
- 第 2 段: `apps/api/public/index.html` を repo に commit → deploy success
- 第 3 段: Hono 公式の `apps/api/api/[[...route]].ts` パターンが Next.js 前提と判明 → `apps/api/api/index.ts + vercel.json rewrites` に切替
- routing は解消したが、ランタイムで 500 FUNCTION_INVOCATION_FAILED が新規発覚

### TASK-0019: FUNCTION_INVOCATION_FAILED 修正

- BE 久遠周が PM 提示の 4 仮説（pnpm workspace bundle / `@upstash/redis` bundling / runtime 表記 / env vars）から仮説 3 を検証
- `export const config = { runtime: 'nodejs' }` → トップレベル `export const runtime = 'nodejs'` に置換した PR #11 で preview deploy → **依然 500**
- 仮説 3 単独原因ではないと BE 判定 → vercel logs 取得を試みるも Vercel CLI 認証未設定でブロック
- ユーザーへ vercel login 要請（A 案）→ ユーザー回答前に PM が ADR-0008 起案方針を提示
- 結果: TASK-0019 却下クローズ / PR #11 close

## 2. 参照実装比較分析（再参照のタイミング）

### 当時（2026-04-25）の参照範囲

`docs/history/2026-04-25_multi-agent-architecture-reference.md` で 参照実装の **通信レイヤ思想**（YAML + flock + inotifywait + tmux 通知のみ）を整理。
結論: 「思想を援用 / 直接フォークしない」。

### ADR-0003 起案時の見落とし

参照実装の **実装層**（クラウド deploy 不使用 / Notion mcp は能動 fetch のみ）を ADR-0003 起案（2026-04-27）時に再参照していなかった。

### 2026-04-28〜29 の再参照で判明した事実

ユーザー指摘で 参照実装リポ（更新: 2026-04-28）を再調査:

| 観点 | 参照実装 | 本 PJ ADR-0003 |
|------|--------|----------------|
| Notion 連携 | `claude mcp add notion` のみ（能動 fetch） | mcp + Vercel Cron polling + Cloudflare Tunnel + ローカル Notifier |
| 自動 wake-up 通知 | **無し**（エージェントは起動時に能動 fetch） | あり（tmux send-keys 経由） |
| クラウド deploy | 無し（Tailscale でリモート可） | mat-board-watcher → Vercel |
| Windows サポート | WSL2 + Ubuntu | psmux + Windows ネイティブ |
| ペルソナ階層 | 参照実装 / karo / ashigaru / gunshi（4 階層） | PM / Tech Lead / Designer / BE（フラット 4 ロール + 権限境界） |

つまり、参照実装は **「Notion 新着の自動 wake-up 通知レイヤ」自体を持っていない**。Claude Code 多エージェント運用は能動 fetch + ユーザー起動で成立している。

### 本 PJ への含意

ADR-0003 で立てた「自動 wake-up 通知レイヤ」要件 **そのものが、運用上は不要** だった可能性が高い。実際、本セッション（2026-04-28〜29）で PM がすべての業務を能動 fetch + ツール召喚で完遂し、mat-board-watcher が止まっていても支障が出ていない事実がこれを裏付ける。

## 3. ADR-0008 採択経緯

ユーザーへ 3 案提示:

- **案 A**: 現アーキ継続（vercel logs → BE 再起動 → 500 解消）
- **案 B**: 部分撤退（mat-board-watcher 凍結 + 能動 fetch 運用化 / ADR-0003 §2.1 / §5 / §5.5 を Superseded）
- **案 C**: 参照実装フル準拠（WSL2 + tmux + inotifywait）

ユーザー判断: **案 B（部分撤退）**。

PM 着手（2026-04-29 セッション 3）:

1. TASK-0019 「却下」遷移 + PM クロージング formal 投稿
2. PR #11 close（撤退方向確定の即時シグナル）
3. ADR-0008 起案（本 ADR）+ ADR-0003 ヘッダ Superseded + CLAUDE.md §1.3 更新 を 1 PR（PR #24）
4. mat-board-watcher 凍結 PR（PR #12 / schedule 削除 + README 凍結告知）/ ただし下記 8 で D2 採択により close 連動消滅
5. ユーザー作業 ステップ 1 完了: Cloudflare Tunnel `notifier.141plot.org` プロセス停止（cloudflared.exe Ctrl+C）
6. PM gh CLI 代行: GitHub Actions secrets `CRON_SECRET` / `PRODUCTION_POLL_URL` 削除
7. ユーザー作業 ステップ 2 完了: Vercel project `mat-board-watcher` 削除（env vars 5 件連動消滅）
8. **ユーザー判断 D2 採択**: 「使わないものは全部削除」方針で mat-board-watcher リポ自体を GitHub 削除 → ADR-0008 §2.1 / §4.2 / §4.3 / §5 を D2 反映に修正（追加コミット）→ PR #12 close → `gh repo delete diesel141/mat-board-watcher` で完全削除
9. ユーザー作業 ステップ 3 完了: Cloudflare Tunnel resource + DNS record `notifier.141plot.org` を Cloudflare Dashboard で削除

これにより、ADR-0003 phase1 通知レイヤの全外部リソース（GitHub リポ / Vercel project / Vercel env vars / GitHub Actions secrets / Cloudflare Tunnel resource / DNS record）は **完全に削除済み**。残るのは本リポの ADR / 歴史化メモ / 個人ローカル clone のみ。

## 4. 失われたもの・残るもの

### 失われたもの

- mat-board-watcher の phase1 実装稼働（dispatcher / notion-client / state / cron-poll handler / Vercel deploy / GitHub Actions cron）
- BE 久遠周の TASK-0019 着工分（PR #11 / runtime 表記修正コミット）
- Cloudflare Tunnel `notifier.141plot.org` プロセス + Tunnel resource + DNS CNAME（全削除済）
- **mat-board-watcher リポ自体**（D2 採択により GitHub から完全削除 / 2026-04-29）
- **個人ローカル clone `/c/_vps/git/mat-board-watcher/`**（L1 採択により削除済 / 2026-04-29）
- Vercel project `mat-board-watcher` + env vars 5 件（削除済）
- GitHub Actions secrets 2 件（削除済）

### 残るもの

- ADR-0003 §3 却下案 A〜F + 再考閾値（phase2 復活時の判断材料）
- ADR-0003 §5.4 認証経路（Notion mcp Internal Integration / OAuth 並存）
- ペルソナ群（PM / Tech Lead / Designer / BE）と権限境界（ADR-0006 §5.2）
- ハイブリッド通信プロトコル（ADR-0005 / formal 3 + informal 4）
- ADR ハウススタイル（採用 + 却下 + 再考閾値）
- 歴史化アーカイブ（TASK-0016〜0019 の踏破経験 / 本メモ）
- 既存 feedback memory 群（PM proactive review / SaaS limit verification 等）

## 5. 学び（feedback memory 昇格候補）

### 学び 1: ADR 起案時の関連歴史化メモ全件再読

ADR-0003 起案時に 参照実装 参照メモ（2026-04-25）を再読していれば、「参照実装は通知レイヤ無しで運用」という重要事実が見えていた可能性が高い。

**規律化候補**:

- ADR 起案時、`docs/adr/<number>-*.md` の関連 ADR と `docs/history/*.md` の関連歴史化メモを全件再読することを `memory/feedback_pm_proactive_review.md` 工程 A に追加
- または PM 自己点検チェックリスト `docs/templates/checklists/pm-self-review.md` 工程 A に「ADR 起案時の関連歴史化メモ全件再読」項目追加

### 学び 2: 採用スタックの実機踏破経験を ADR 採択前に独立検証

ADR-0003 採用時に「Vercel + Hono + pnpm workspace + Vercel Functions runtime」の組み合わせを誰も事前踏破していないことを PoC で検証していなかった。

**規律化候補**:

- 採用スタックに「組み合わせとしては 5 件以上の本番実績がある」「公式 docs に Next.js 等の特定 framework 前提が含まれていないか」「無料枠制限を Pricing/Limits ページで独立検証」の 3 点を ADR 採択前に PM/Tech Lead 双方が独立確認する規律
- `memory/feedback_pm_saas_limit_verification.md` を拡張 → `memory/feedback_pm_stack_adoption_verification.md` に格上げ候補

### 学び 3: 過剰設計の判定タイミング

「クラウド deploy で自動 wake-up を作る」要件自体が過剰設計だった可能性を、ADR-0003 採択後 4 タスク踏んでから判定した。早期判定の規律が必要。

**規律化候補**:

- 「実装に 3 段階以上の手戻りが連続したら、要件そのものの過剰設計疑念を ADR 起案者（or PM）が独立検証」を `memory/feedback_pm_proactive_review.md` に追加
- 工程 B（受入レビュー）で「累計手戻り段階数」を計測し、3 段階超で「要件再評価セッション」を起動する閾値ライン

### 学び 4: 連鎖罠ゾーンの早期撤退判断

TASK-0016 で 1 段目を踏んだ時点で「Vercel + Hono + pnpm workspace 組み合わせはニッチ罠ゾーン」と判定する余地はあった。撤退を決断するまでに踏んだ罠は 4 段階。

**規律化候補**:

- 「同一スコープで 2 段階以上の罠を踏んだら、撤退コスト vs 継続コストを ADR で文書化して PM 決裁」を恒久規律化
- 撤退 ADR のテンプレート（本 ADR-0008 形式）を `docs/templates/adr/` に格納

## 6. 次の起動条件（phase2 通知レイヤ復活）

ADR-0008 §3 却下 A 再考閾値 + §5 開いている論点 (2) 数値:

- チーム規模が **6 ロール以上**
- 同時稼働 **4 ロール以上**
- 1 日 **10 メッセージ超**

これらが恒常化した時点で ADR-0009（仮）を起案し、ADR-0008 を Superseded する形で通知レイヤを再導入。

phase2 採用スタック候補:

- 参照実装スタイル WSL2（却下 B 再考閾値が並行成立した場合）
- Cloudflare Workers + Notion Webhooks（却下 C 再考閾値が並行成立した場合）
- その他

## 7. 参考資料

- ADR-0003 / ADR-0008 / ADR-0006 §5.2 / ADR-0007 §2.6
- 参照実装リポ: <https://github.com/yohey-w/参照実装リポ>
- 本 PJ history: `docs/history/2026-04-25_multi-agent-architecture-reference.md` / `2026-04-25_psmux-windows-investigation.md`
- TASK-0016〜0019 Notion ページ群（タスクID 横断検索 / TASK-0017 0018 PM 受入レビュー / TASK-0019 PM クロージング却下）
