# psmux セットアップ手順 (Windows)

> 本プロジェクトのマルチエージェント実行基盤である **psmux** のローカル Windows 環境への
> セットアップと、Claude Code チーム運用に必要な前提条件をまとめた運用ドキュメント。

## 1. 前提条件

| 項目 | 要件 | 確認コマンド |
|------|------|-------------|
| OS | Windows 10 / 11 | — |
| PowerShell | 7.0 以降（必須） | `$PSVersionTable.PSVersion` |
| パッケージマネージャ | winget（推奨）／ scoop ／ cargo ／ choco | `winget --version` |
| Claude Code CLI | インストール済み・PATH 通っている | `Get-Command claude` |

PowerShell 7+ は psmux の env shim と teammate モード注入に必須。Windows 標準の
PowerShell 5.1 では動作しません。未導入なら:

```powershell
winget install --id Microsoft.PowerShell --source winget
```

## 2. インストール

```powershell
winget install psmux --accept-source-agreements --accept-package-agreements
```

- パッケージ ID: `marlocarlo.psmux`
- 動作確認バージョン: **3.3.3**（2026-04-25 検証）
- インストール先: `%LOCALAPPDATA%\Microsoft\WinGet\Packages\marlocarlo.psmux_*\`
- PATH に上記パスが追加され、`psmux` / `pmux` / `tmux` の 3 エイリアスが利用可能になる

### インストール直後の落とし穴

winget が PATH を更新しても、**現在開いているシェルには反映されない**。新しい
PowerShell ウィンドウを開くか、現セッションで以下を実行する:

```powershell
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
```

### 動作確認

```powershell
psmux --version           # → psmux 3.3.3
psmux list-keys | Select-Object -First 5
psmux show-options -g prefix    # → prefix C-b
```

## 3. 設定ファイル `.psmux.conf`

`%USERPROFILE%\.psmux.conf` に配置。本プロジェクトでは以下の最小構成を採用:

```conf
# Convenience pane-split aliases
bind-key | split-window -h
bind-key - split-window -v

# Tolerance for slow keystrokes
set -g escape-time 500

# Claude Code teammate mode integration
set -g claude-code-fix-tty on
```

設定変更を稼働中サーバへ反映:

```powershell
psmux source-file "$env:USERPROFILE\.psmux.conf"
```

> 注意: `source-file` は **追加適用**。以前のセッションで設定した値を上書きしたい場合は
> 明示的に `unbind-key` / `set` で戻すか、`psmux kill-server` で全セッションを破棄する。

## 4. 基本操作

### prefix キー

- 本プロジェクトでは tmux 標準の **`Ctrl+B`** を使用
- prefix 単独では画面に変化が出ない（仕様）。`Ctrl+B` を押して指を離してから次のキー

### セッション管理

| 操作 | コマンド |
|------|---------|
| 新規セッション作成（attach あり） | `psmux new-session -s <name>` |
| 新規セッション作成（detach 状態） | `psmux new-session -d -s <name>` |
| セッション一覧 | `psmux ls` |
| セッションへ attach | `psmux attach -t <name>` |
| 既存セッションへ detach | `Ctrl+B` → `d` |
| セッションを kill | `psmux kill-session -t <name>` |
| 全セッション kill | `psmux kill-server` |

### ペイン操作（attach 中）

| 操作 | キー |
|------|-----|
| 横分割 | `Ctrl+B` → `%`（または `\|`） |
| 縦分割 | `Ctrl+B` → `"`（または `-`） |
| ペイン移動 | `Ctrl+B` → 矢印キー |
| ペイン番号表示 | `Ctrl+B` → `q` |
| ペイン kill | `Ctrl+B` → `x` |
| ズーム切替 | `Ctrl+B` → `z` |

### CLI からのペイン操作（attach 不要）

別 PowerShell ウィンドウから既存セッションを操作:

```powershell
psmux split-window -h -t <session>     # 横分割
psmux split-window -v -t <session>     # 縦分割
psmux list-panes -t <session>
psmux send-keys -t <session>:0.1 'echo hello' Enter
```

multi-agent 運用では結局 CLI 主導になるので、prefix キー操作は補助的位置付け。

## 5. Claude Code チーム連携

psmux は Claude Code agent teams をファーストクラスでサポート。インタラクティブな
`claude` 実行時に teammate を要求すると、自動でペイン分割しサブエージェントを起動する。

### psmux が自動で行うこと

- 環境変数 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` を全ペインに設定
- 環境変数 `PSMUX_CLAUDE_TEAMMATE_MODE=tmux` を設定
- `claude` 起動時に `--teammate-mode tmux` を自動注入

### 推奨ワークフロー

```powershell
# 1. ハブセッションを開く
psmux new-session -s mat-hub

# 2. ペイン内で claude を起動
claude
```

teammate を要求すると、追加ペインが自動生成され子エージェントが立ち上がる。

## 6. 本プロジェクト固有の運用ルール（重要）

psmux + Claude Code のデフォルト挙動には、本プロジェクトの通信プロトコルと衝突する
点がある。詳細は `docs/history/2026-04-25_psmux-windows-investigation.md` を参照。

要点:

1. **teammate（ペイン分割）を優先、worktree 隔離は選ばない**
   - Opus 等は標準で worktree を選びがちで、ペイン化されない
   - `CLAUDE.md` および各ペルソナで明示的に teammate 優先を指定する
2. **ペイン間の直接通信禁止、Notion 掲示板必須**
   - psmux のデフォルトは親→子への `tmux send-keys` 直接指示
   - 業務指示・報告は **Notion 掲示板の 3 種メッセージのみ**（開始指令／問題報告／完了報告）
3. **`-p`（pipe mode）はチーム機能無効化**
   - インタラクティブモード必須

## 7. トラブルシューティング

### Q. `psmux` コマンドが見つからない
- インストール直後のシェルでは PATH 未反映。**新規 PowerShell** を開くか §2 のコマンドで反映。

### Q. `Ctrl+B` が効かない（緑バーは出ている）
- prefix 単体では何も起きないのが仕様。**指を離してから次のキー**。
- それでもダメな場合、ターミナル側（Windows Terminal / VS Code 統合ターミナル等）が
  `Ctrl+B` をインターセプトしている可能性。設定で `ctrl+b` 検索 → 競合解除。
- 暫定回避: `.psmux.conf` で prefix を `Ctrl+A` に変更。

### Q. `Ctrl+B` が効かない（緑バーが見えない）
- psmux セッションに attach していない。`psmux ls` で確認 → `psmux attach -t <name>`。

### Q. 設定変更が反映されない
- 稼働中サーバへは `psmux source-file <path>` で反映。
- `set -g` で同じオプションを上書きしないと前の値が残る。完全リセットは `psmux kill-server`。

### Q. セッションがいつの間にか残っている
- ターミナルウィンドウを閉じても **psmux サーバはバックグラウンド常駐**。
- `psmux ls` で一覧、不要なら `psmux kill-session -t <name>` または `psmux kill-server`。

### 既知の問題

- **Issue #42848**: Unix スタイルパスが PowerShell に渡る不具合の報告あり。
  Claude Code agent team 起動時に踏む可能性あり。再現したら別途記録。
  https://github.com/anthropics/claude-code/issues/42848

## 8. 参考資料

- [psmux/psmux (README)](https://github.com/psmux/psmux)
- [psmux + Claude Code 公式ガイド](https://github.com/psmux/psmux/blob/master/docs/claude-code.md)
- 本プロジェクト調査メモ: `docs/history/2026-04-25_psmux-windows-investigation.md`
- 通信アーキテクチャ参照: `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md`
