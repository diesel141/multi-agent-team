---
date: 2026-04-29
type: history / runtime-operation
title: セッション 4 — ADR-0008 完全クローズと運用学び（Tech Lead BG / /schedule 初運用 / feedback memory 直接編集判断）
status: 採択時点の経緯記録
tags: [adr-0008, session-4, pm-autonomy, tech-lead-bg-process, schedule-routine, feedback-memory-management]
---

# セッション 4 — ADR-0008 完全クローズと運用学び

## 1. 本セッションの位置付け

ADR-0008（通知レイヤ能動 fetch ピボット）採択直後（セッション 3 で PR #24 起票まで）から、PR レビュー&マージ + feedback memory 4 件昇格 + 半年後再評価エージェント予約までを **ユーザー就寝中に PM 自律で完遂** したセッション。

ADR-0008 採択経緯は別メモ（`docs/history/2026-04-29_adr-0008-notification-layer-pivot.md`）。本メモは **採択後の運用クローズと学び** を記録する。

## 2. PM 自律運用の境界（再確認）

ユーザー指示: 「順次進めて。もう寝るから、寝ている間に環境構築を進めて。決定事項は全てPMの判断。」

`memory/feedback_pm_autonomy.md`（PM タスク実行時の自律判断ライン）に従い、以下を PM 判断で進めた:

- Tech Lead BG 外部プロセス召喚（`claude --dangerously-skip-permissions -p`）
- PR #23 / PR #24 のレビュー&マージ依頼を Tech Lead に投げる
- feedback memory 4 件の昇格を auto memory 直接編集で済ませる判断（chore PR 不要）
- `/schedule` で半年後の再評価エージェントを予約
- PM 受入レビュー formal の投稿とクローズ
- `current_progress.md` / `MEMORY.md` の最終更新

例外（破壊的操作・スコープ逸脱・受入再修正の方向選択）に該当する局面は本セッションでは発生しなかった。

## 3. /schedule リモートエージェント予約（初運用）

### 3.1 採用方針

ADR-0008 §3 却下 A 再考閾値（6 ロール以上 + 同時稼働 4 + 1 日 10 メッセージ超）の半年後（2026-10-29 09:00 JST）実測値再評価を、人手リマインダーではなく **claude.ai routines** で自動化。

### 3.2 作成手順

1. `Skill schedule` を invoke
2. 環境（`Default` / `env_01RLQnudHM16sth2MdvNbm8z`）をユーザー新規環境として **Skill 側で自動作成** された
3. 一回起動（`run_once_at`）で `2026-10-29T00:00:00Z` 指定
4. リポ `https://github.com/diesel141/multi-agent-team` を session_context.sources に指定
5. プロンプトに「ADR-0008 §3 却下 A 再考閾値の充足状況を評価し `docs/history/2026-10-29_adr-0008-phase2-threshold-review.md` を起票して `development` 宛 PR を起票」を自己完結型で記述
6. 環境制約として「Notion API / Vercel API / 外部 SaaS にはアクセスできない / リポ内データと gh CLI のみ利用可」を明示

### 3.3 採用したパラメータ

| パラメータ | 値 |
|----------|-----|
| trigger_id | `trig_01J5yw7bwfd85xKBx1vLyghk` |
| run_once_at | `2026-10-29T00:00:00Z` (= 2026-10-29 09:00 JST) |
| environment_id | `env_01RLQnudHM16sth2MdvNbm8z` (`Default` / kind `anthropic_cloud`) |
| model | `claude-sonnet-4-6` |
| allowed_tools | `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep` |
| mcp_connections | なし（Notion 連携は GitHub PR 経由で代替） |

### 3.4 残課題: GitHub 連携

Skill 出力で「GitHub not connected for diesel141/multi-agent-team」警告が表示。本番トリガー（2026-10-29）までにユーザーが `/web-setup` を実行して GitHub App 連携を有効化する必要がある。緊急ではないが 6 ヶ月以内のいずれかのタイミングで案内する申し送り。

### 3.5 学び

- リモートエージェントは **自己完結型プロンプト** が必須（呼び出し元の context を継承しない）
- 環境制約（Notion API / Vercel API / 外部 SaaS にアクセス不可）を **プロンプトに明記** することで、エージェントが不可能な行動を試みず PR の「PM 宛アクションアイテム」に記載する設計が成立
- 半年後の再評価のような長期リマインダーは、PM の記憶・人間オペレータの稼働に依存しない自動化が運用負荷を低減する

## 4. Tech Lead BG プロセス運用（複数 PR レビュー&マージへの応用）

### 4.1 採用方針

PR #23 / PR #24 の Tech Lead レビュー&マージは PM 権限境界外（`feedback_pm_proactive_review.md` §「権限境界の確定」）。Tech Lead を新規セッションとして起動する必要があった。

選択肢:
- A: psmux teammate（CLAUDE.md §1.1 推奨）— ユーザー就寝中はペイン操作不可
- B: harness Agent ツール（worktree 隔離）— CLAUDE.md §1.1 で禁止
- C: **外部プロセス `claude --dangerously-skip-permissions -p` BG 起動** — TASK-0003 で確立済の方式

C を採用。

### 4.2 指示書ファイル方式

CLI 引数に長文プロンプトを渡すと quote エスケープが破綻するため:

1. 指示書を `.tech-lead-pr-review-instructions.md` としてリポ内に隠しファイル作成（git 管理外）
2. CLI 引数では「このファイルを Read して指示通り動け」と短く指示
3. Tech Lead セッション内で指示書を Read → 内面化 → 順次実行
4. 完了後に PM クロージング規律工程 C-5 で削除

指示書には以下を含めた:
- 整列ステップ（ペルソナ / CLAUDE.md / `_common-prologue.md` / 関連 feedback memory）
- 業務通信（Notion 議論 formal の URL 提示）
- 作業手順 Step A〜F（PR レビュー → マージ → 完了報告 formal 投稿 → 議論 formal ステータス遷移）
- 権限境界の遵守（PM はマージしない / 異論は PR コメント + Notion 議論 formal で表明）
- ブロッカー検知時の対応（問題報告 formal 投稿 + マージ保留）
- 完了後の返り値（3 行で要点のみ）

### 4.3 結果

| 項目 | 結果 |
|------|------|
| Tech Lead BG ID | `b6q4vq6ho` |
| 起動方法 | `Bash(run_in_background=true, timeout=600000)` |
| 完了状態 | exit 0 |
| 所要時間 | 2-3 分（PR diff 確認 + マージ + Notion 投稿 + 議論 formal ステータス遷移） |
| マージ commit | PR #23 = `9b9f703` / PR #24 = `a7ba18e` |
| レビュー観点 PASS 率 | 8 / 8（100%） |
| Tech Lead 完了報告 | `350b60ad49778134b1d6ee827d7805e2` |

### 4.4 学び

- Tech Lead BG プロセスは **複数 PR の連続レビュー&マージ** にも適用可能（PR #23 → PR #24 を 1 セッションで完遂）
- 指示書ファイル方式は **指示の可監査性** が高い（PM が指示書を読み返して何を依頼したか確認できる）
- 完了報告 formal の投稿 + 議論 formal のステータス遷移を Tech Lead 側で完結させることで、PM の手戻り作業がゼロ
- BG プロセスは PM セッションが他作業（feedback memory 編集 / `/schedule` 予約）と並列で進められる

## 5. feedback memory 直接編集判断（chore PR 不要）

### 5.1 当初の計画

セッション 3 終了時の `current_progress.md` には「PR #24 マージ後、学び 1〜4 の feedback memory 昇格を **chore PR で実施**」と記載されていた。

### 5.2 PM 判断による方針変更

セッション 4 で feedback memory ファイルのパスを再確認:

```
C:\Users\141di\.claude\projects\C---vps-git-multi-agent-team\memory\
```

このディレクトリは Claude Code の **auto memory システム** に属し、本リポジトリ（`C:\_vps\git\multi-agent-team\`）の git 管理外。

- → chore PR で扱える対象ではない
- → ローカル直接編集が唯一の運用ルート
- → 「chore PR で実施」という当初計画は前任 PM の誤認

PM 判断で **auto memory 直接編集** に切り替え、PR 不要として完遂。

### 5.3 影響と恒久化

| feedback memory ファイル | git 管理 | 編集方法 |
|------------------------|---------|---------|
| `C:\_vps\git\multi-agent-team\memory\*.md` | 該当なし（このパスは存在しない） | — |
| `C:\Users\141di\.claude\projects\.../memory/*.md` | **管理外**（auto memory） | ローカル直接編集 |

恒久化として `current_progress.md` 注意点に「auto memory は git 管理外 / 直接編集で完結 / PR 不要」を明示。

### 5.4 学び

- auto memory と project repo の **管理境界** を PM が常に意識する必要がある
- Claude Code の auto memory は OS ユーザーホーム配下に置かれ、リポ間で共有されない（このプロジェクト固有）
- 計画段階で「chore PR」「直接編集」の判別を行うことで無駄な PR / ブランチ作成を回避

## 6. PM Self-Review 工程 A / B 拡充の判断

### 6.1 拡充内容

ADR-0008 採択経緯（連鎖罠 4 段階 + 参照実装再確認）から得た学び 4 件を `feedback_pm_proactive_review.md` に反映:

| 学び | 反映先 |
|------|--------|
| 1: ADR 起案時の関連歴史化メモ全件再読 | 工程 A 項目 6（新規） |
| 2: 採用スタック踏破経験の独立検証 | `feedback_pm_saas_limit_verification.md` を `feedback_pm_stack_adoption_verification.md` に拡張改名 + 工程 B-3 から参照 |
| 3: 過剰設計の判定タイミング | 工程 B 項目 6 統合（学び 4 と一体） |
| 4: 連鎖罠ゾーンの早期撤退判断 | 工程 B 項目 6（同種手戻り 2 段階で黄信号 / 3 段階で要件再評価） |

### 6.2 二重管理問題と同期

`feedback_pm_proactive_review.md`（auto memory）と `docs/templates/checklists/pm-self-review.md`（project repo）が **同一規律の二重管理** 状態にある。auto memory は PM 個人の記憶、project repo は新規参加者にも共有可能なチェックリスト。

PR #23（chore）で `pm-self-review.md` の工程 A / 工程 D に新項目（PM 組織規律 ADR の越権チェック / Designer 稼働率モニタリング）が追加されたが、本セッションで `feedback_pm_proactive_review.md` に追加した工程 A 項目 6 + 工程 B 項目 6 は `pm-self-review.md` にまだ反映されていない。

本セッションで二重管理の同期も含めて 1 件の chore PR で実施（本ブランチ `docs/session-4-historization-and-pm-self-review-update`）。

### 6.3 学び

- feedback memory（auto memory / PM 個人記憶）と pm-self-review.md（project repo / チーム共有チェックリスト）は **同一規律を二重管理** している
- 規律追加時は **両方を同期** する規律を `feedback_pm_proactive_review.md` 工程 D 候補（次セッションで検討）
- 単一規律の追加で auto memory のみ更新 → project repo に未反映、というドリフトが発生しやすい

## 7. 本セッションの作業順序（参考）

| # | 工程 | 所要時間 | 並列性 |
|---|------|---------|--------|
| 1 | 整列（ペルソナ / 進捗 / feedback memory 読み込み） | 5 分 | 直列 |
| 2 | PM Proactive Self-Review 工程 D（git status / gh pr list / Notion 検索） | 3 分 | 並列 |
| 3 | Tech Lead 宛 Notion 議論 formal 投稿 | 5 分 | 直列 |
| 4 | Tech Lead BG 召喚（指示書作成 + プロセス起動） | 5 分 | 直列 |
| 5 | `/schedule` で半年後再評価エージェント予約 | 5 分 | Tech Lead BG と並列 |
| 6 | feedback memory 4 件昇格（auto memory 直接編集） | 10 分 | Tech Lead BG と並列 |
| 7 | PR #23 / #24 マージ確認（Monitor） | 待機（実時間 2-3 分） | 並列待ち |
| 8 | Tech Lead 完了報告 fetch + PM 受入レビュー formal 投稿 | 10 分 | 直列 |
| 9 | temp ファイル削除 + `current_progress.md` / `MEMORY.md` 最終更新 | 5 分 | 直列 |

合計実時間: 約 50 分（並列化により 30-40 分に圧縮）。

## 8. 本セッションが残した恒久化候補

1. **auto memory と project repo の規律同期** — 規律追加時に両方更新する手順を `feedback_pm_proactive_review.md` 工程 D に追加候補
2. **GitHub 連携前提の routines 起動** — `/schedule` でリポを使うエージェントは起動前に `/web-setup` 完了を確認する規律候補
3. **Tech Lead BG プロセスの指示書テンプレ** — `docs/templates/instructions/tech-lead-bg-process-task.md` 等として明文化候補（複数 PR レビュー&マージ用 / シングルタスク用 / etc.）

これらは本 chore PR では取り込まず、次セッション以降の起案候補として申し送り。

## 9. 参考資料

- ADR-0008: `docs/adr/0008-notification-layer-pivot.md`
- ADR-0008 採択経緯: `docs/history/2026-04-29_adr-0008-notification-layer-pivot.md`
- Tech Lead BG 完了報告: <https://www.notion.so/350b60ad49778134b1d6ee827d7805e2>
- PM 受入レビュー: <https://www.notion.so/350b60ad497781fab6b1ed0f04430d9e>
- 半年後再評価エージェント: <https://claude.ai/code/routines/trig_01J5yw7bwfd85xKBx1vLyghk>
- feedback memory 拡張先: `feedback_pm_proactive_review.md` / `feedback_pm_stack_adoption_verification.md`
