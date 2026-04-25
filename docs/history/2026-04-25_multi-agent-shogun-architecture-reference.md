---
date: 2026-04-25
type: reference / architecture-study
title: multi-agent-shogun のペイン間通信アーキテクチャ
status: 参照済（採用判断は Tech Lead アサイン後）
tags: [architecture, ipc, tmux, notion, windows, design-reference]
---

# multi-agent-shogun のペイン間通信アーキテクチャ

## 1. 背景

本プロジェクトの必須要件は「Notion 掲示板の 3 種メッセージのみで通信」。
psmux + Claude Code のデフォルト挙動（親→子の `tmux send-keys` 直接指示）はこれと衝突する
（詳細は `2026-04-25_psmux-windows-investigation.md`）。

先行事例として `yohey-w/multi-agent-shogun` を調査し、本プロジェクトの通信レイヤ設計に
援用できる思想を整理する。

## 2. shogun のアーキテクチャ要点

「**メッセージ本体は別チャネル / tmux は通知のみ**」というハイブリッド設計。

| レイヤ | 仕組み | 目的 |
|--------|--------|------|
| メッセージ本体 | YAML ファイル + `flock` 排他ロック（例: `queue/inbox/ashigaru1.yaml`） | アトミック書き込み・耐障害性 |
| 通知 | `tmux send-keys` で短いウェイクアップ信号のみ | 「メールあり」のキックだけ。本文は流さない |
| 共有掲示板 | `dashboard.md`（書き込みは Karo 一名のみ） | 単一 writer で競合回避 |
| タスクキュー | `queue/shogun_to_karo.yaml` 等 | 役職間の指示キュー |
| エージェント識別 | tmux user option `@agent_id` | ペイン順序変動に強い安定 ID。`tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}'` |
| inbox 監視 | `inotifywait`（Linux FS イベント） | ポーリング 0 |
| CLI 抽象化 | `lib/cli_adapter.sh` | Claude Code / Codex / Copilot / Kimi Code を切替 |

公式ドキュメントからの引用:
> "Agents talk to each other by writing YAML files — like passing notes.
> No polling loops, no wasted API calls."
> "Message content is never sent through tmux — only a short 'you have mail' nudge.
> The agent reads its own file."

## 3. 本プロジェクトへの援用ポイント

shogun の **思想** は本プロジェクトと整合的。実装層を差し替えれば成立する。

| 役割 | shogun | 本プロジェクト（提案） |
|------|--------|----------------------|
| メッセージ実体 | ローカル YAML ファイル | **Notion 掲示板**（3 種メッセージ） |
| tmux の役割 | ウェイクアップ通知のみ | 同（業務通信には使わない） |
| 共有状態 | `dashboard.md`（単一 writer） | Notion ボード（PM が一次管理者） |
| 競合回避 | `flock` + 単一 writer | Notion API のトランザクション + 単一 writer 規律 |
| エージェント識別 | tmux `@agent_id` | 同方式を踏襲推奨（ペイン順序非依存） |
| 通知レイヤ | `inotifywait`（Linux のみ） | **未決**（§4 参照） |

### 採用候補の規律
- **tmux は通知レイヤ**に限定し、業務指示・報告は必ず Notion 経由
- **共有状態は単一 writer**（PM のみ Notion ボードに状態書き込み権限）
- **エージェント ID は tmux user option** で安定識別

## 4. 未解決の設計課題

### Windows での通知レイヤ
shogun の `inotifywait` は Linux 限定。Windows + psmux 環境での代替を選定する必要あり。

| 候補 | メリット | デメリット |
|------|----------|------------|
| Notion API ポーリング | 実装が単純。クロスプラットフォーム | API コスト・レイテンシ |
| Notion Webhooks | プッシュ型でレイテンシ最小 | 公開エンドポイント or リレーが必要。ローカル PC では工夫要 |
| PowerShell `FileSystemWatcher` + ローカルシャドー | Windows ネイティブ・低レイテンシ | Notion ↔ ローカルの同期層が別途必要 |
| Node.js `chokidar` | クロスプラットフォーム | 同上（同期層必要） |

3 種メッセージのみ・低頻度通信のため、**初期実装はシンプルなポーリング**から始め、
レイテンシが問題になったら Webhook 化、という段階導入が現実的。

最終的な選定は **Tech Lead / Architect** にアサイン後に委ねる。

## 5. 結論

- shogun の設計思想（メッセージ本体は別チャネル / tmux は通知のみ / 単一 writer）は
  本プロジェクトの通信レギュレーションを実装する上での **参照アーキテクチャ** として有用
- 実装層は Notion 掲示板に置き換え、Windows の通知手段は Tech Lead が選定
- shogun を直接フォークするのではなく、思想だけを援用する（本プロジェクトはあくまで Notion ベース）

## 6. 参考資料

- [yohey-w/multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun)
- 関連: `docs/history/2026-04-25_psmux-windows-investigation.md`（衝突点の前提）
