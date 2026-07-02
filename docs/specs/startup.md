# 起動ガイド

## 必要環境

| ツール | 詳細 |
|---|---|
| **psmux** | 3.3.3+（Windows ネイティブ Rust 実装）`winget install psmux` |
| **シェル** | bash（Git for Windows / MSYS2 等） |
| **Claude Code** | Windows ネイティブ |
| WSL2 | **不要** |

## 起動手順

bash プロンプトで実行:

```bash
cd /c/_vps/git/multi-agent-team
./scripts/start.sh
```

## 起動後の状態

- psmux セッション `team` が 4 ペイン（pm + dev1 + dev2 + dev3）で起動
- 各ペインで `claude --dangerously-skip-permissions` が自動起動
- 各ペインが `instructions/<role>.md` を Read してから指示待ち状態に入る

## 参考資料

起動環境の一次ソース: `docs/history/2026-04-25_psmux-windows-investigation.md`
