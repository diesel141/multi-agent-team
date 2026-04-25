---
date: 2026-04-25
type: investigation / design-constraint
title: psmux × Claude Code × Windows の運用検討
status: 結論済（ガードレール整備が前提条件）
tags: [psmux, claude-code, windows, communication-protocol, kickoff]
---

# psmux × Claude Code × Windows の運用検討

## 1. 背景

本プロジェクトの必須要件:
- マルチエージェントは **psmux** 上で動作させる（https://github.com/psmux/psmux/）
- エージェント間通信は **Notion 掲示板**「開始指令 / 問題報告 / 完了報告」の 3 種類のみ
- 稼働ホストは **ローカル Windows 機**

立ち上げ前に、上記スタックが整合的に成立するかを検証した。

## 2. 調査結果

### 2.1 psmux の Windows 対応：ネイティブ対応（WSL 不要）

- Rust 製の Windows ネイティブ実装。Windows ConPTY を直接利用
- WSL / Cygwin / MSYS2 すべて不要
- tmux コマンド言語互換、`.tmux.conf` を読む
- インストール手段: `winget install psmux` ほか scoop / cargo / choco / 直接ダウンロード

### 2.2 Claude Code との統合：ファーストクラス

psmux が以下を自動でセットする:

| 設定 | 値 | 役割 |
|------|----|----|
| env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | エージェントチーム機能の有効化（必須） |
| env `PSMUX_CLAUDE_TEAMMATE_MODE` | `tmux` | teammate モードの有効化 |
| `claude` 起動時引数 | `--teammate-mode tmux` | 自動注入 |
| ペイン分割 | Claude が teammate 作成 → `tmux split-window` を psmux 経由で実行 | 自動 |
| 子エージェント起動 | `cd <workdir> && claude.exe --agent-id <id> --agent-name <name>` を `send-keys` | 自動 |

### 2.3 ローカル環境の前提条件チェック（2026-04-25 時点）

| 項目 | 状態 |
|------|------|
| PowerShell | 7.5.5（要件 ≥ 7 を満たす） |
| winget | あり |
| Claude Code | あり（`C:\Users\141di\.local\bin\claude.exe`） |
| psmux | ✅ **3.3.3** インストール済（パッケージID: `marlocarlo.psmux`、2026-04-25） |
| `.psmux.conf` | 配置済（prefix は標準の `C-b`、横分割 `\|`／縦分割 `-` 補助バインドあり） |
| 動作確認 | ✅ ペイン分割テスト成功（`Ctrl+B → %`、`Ctrl+B → "`） |

### 2.4 操作上の留意点（実環境で得た知見）

- **prefix 単独では画面に変化が出ない**のが仕様。`Ctrl+B` を押して指を離してから
  次のキー（`%` 等）を押す。これを知らないと「prefix が効かない」と誤認しやすい。
- **PSReadLine との見分け方**: 緑のステータスバーが見えていれば psmux 内部で
  prefix として効く。見えていなければ通常 PowerShell プロンプトで PSReadLine の
  `BackwardChar`（カーソル左移動）に取られる。
- **`source-file` は追加適用**。前のセッションで設定した値を上書きするには
  明示的に `unbind-key` / `set` で戻すか `psmux kill-server` する必要あり。
- **PATH 反映タイミング**: winget インストール直後の現セッションには PATH が
  反映されない。新規 PowerShell ウィンドウで実行するか、`$env:Path` を手動更新する。
- **セッションは常駐**: ターミナルを閉じても psmux サーバはバックグラウンドで生きる。
  `psmux ls` で残骸を定期確認、不要なら `kill-session` / `kill-server`。

## 3. プロジェクト要件との衝突点

psmux + Claude Code のデフォルト挙動には、本プロジェクトのプロトコルと矛盾する点が 3 つある。**ガードレールなしでの採用は不可**。

### 衝突 A: worktree 隔離が優先される

- Opus 等の上位モデルは標準で `isolation: "worktree"` を選び、**psmux ペインではなく不可視のインプロセス subagent** を生成しがち
- これを強制的にペイン化する env var は **存在しない**
- Windows では worktree-tmux 統合がコード上ハードコードで無効化されている → worktree を選ばれた瞬間にチーム可視性とプロトコル遵守の双方が崩壊する
- **対策**: `CLAUDE.md` で「teammate（ペイン分割）を優先する。worktree を選ばない」を明示。各ペルソナにも組み込む

### 衝突 B: デフォルト通信は `tmux send-keys`

- psmux + Claude Code のデフォルト動作は、親エージェントが子ペインに対して `send-keys` で直接指示を流す
- 本プロジェクトの必須要件は **Notion 掲示板 3 種メッセージのみ** → デフォルト挙動は **プロトコル違反**
- **対策**:
  - `CLAUDE.md` および全ペルソナに「ペイン間の直接通信禁止、Notion 掲示板を必ず経由」を明記
  - 起動時の psmux ペイン分割は許容するが、その後の業務通信は Notion API 経由に限定
  - 違反検出（Notion 掲示板に紐づかないペイン間通信ログがある等）の運用監査を将来検討

### 衝突 C: `-p`（pipe mode）はチーム機能を無効化

- `claude -p` ではチームペインが生成されない（インタラクティブモード必須）
- 本プロジェクトのバッチ処理ニーズが将来出た場合は別アーキテクチャが必要

## 4. 既知のリスク

- **Issue #42848**: Unix スタイルパスが PowerShell に渡る既知バグの報告あり。実環境で踏むかは導入後検証
- pipe mode 不可 → 将来的なバッチ自動化の制約として留意

## 5. 結論

- 環境的なブロッカーはない（ネイティブ対応・PowerShell 要件クリア）
- ただし **デフォルト挙動 ≠ 本プロジェクトのプロトコル** であるため、以下の **ガードレール整備が採用の前提条件**:
  1. `CLAUDE.md` で「teammate 優先 / worktree 不選択」を強制
  2. 全ペルソナに「ペイン間直接通信禁止 / Notion 掲示板必須」を埋め込む
  3. インストール後に Issue #42848 の再現確認

## 6. 次のアクション

- [x] `winget install psmux` 実行（2026-04-25 完了、v3.3.3）
- [x] 動作確認・prefix キー操作の理解（2026-04-25）
- [x] `docs/setup-psmux.md` 作成（2026-04-25）
- [ ] `docs/communication-protocol.md` — Notion 必須・send-keys 禁止・teammate 優先
- [ ] `CLAUDE.md` 初稿 — 上記の運用規約をセッション横断で強制
- [ ] 初期コミット & PR 起動

## 7. 参考資料

- [psmux/psmux (README)](https://github.com/psmux/psmux)
- [psmux/docs/claude-code.md](https://github.com/psmux/psmux/blob/master/docs/claude-code.md)
- [anthropics/claude-code Issue #34150 — tmux agent teams on Windows via psmux](https://github.com/anthropics/claude-code/issues/34150)
- [anthropics/claude-code Issue #42848 — Unix-style path on Windows PowerShell](https://github.com/anthropics/claude-code/issues/42848)
