# 通信プロトコル

## YAML キュー方式

| ファイル | 用途 |
|---|---|
| `queue/you_to_pm.yaml` | ユーザー → PM 指示 |
| `queue/inbox/<agent>.yaml` | エージェント別メールボックス |
| `queue/reports/<agent>.yaml` | dev → PM 完了報告 |

## 通知・受信

- **通知**: `tmux send-keys -t team:0.<N> "inbox" Enter`（psmux の tmux 互換コマンド）
- **受信**: polling（pm が手動 or 数秒間隔で inbox チェック）

## inbox 確認規律

- タスク振出し後は **同セッション内でも** `queue/inbox/pm.yaml` + `queue/reports/dev*.yaml` を即再確認すること
- 「振った→待機」は NG

## 将来拡張

PowerShell `FileSystemWatcher` で push 型通知に拡張予定
