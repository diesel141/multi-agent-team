---
date: 2026-04-25
type: decision / integration
title: Notion 連携は公式 Remote MCP を採用
status: 決定済（.mcp.json コミット済 / OAuth セットアップは Notion 構築時に実施）
tags: [notion, mcp, integration, oauth, governance]
---

# Notion 連携は公式 Remote MCP を採用

## 1. 背景

PR #3 で Notion 掲示板スキーマと `.env.example`（`NOTION_TOKEN`）を整備した時点では、
連携手段を未確定としていた。直後にユーザーから「MCP を利用するか」の問いがあり、
3 案（Remote MCP / Local MCP / 自作 API クライアント）を比較検討した。

## 2. 検討した選択肢

| 選択肢 | 概要 | 評価 |
|-------|------|------|
| **A. Notion 公式 Remote MCP**（採用） | `https://mcp.notion.com/mcp` に HTTP 接続、OAuth 認証 | コード不要 / 公式メンテ / 全エージェントで一貫 |
| B. Notion 公式 Local MCP (`@notionhq/notion-mcp-server`) | npm/Docker でローカルに常駐、bearer token 認証 | Notion 社が sunset 方針を表明済み |
| C. 自作 Notion API クライアント | Python/TS で SDK を直叩き | 実装・保守コスト高、Claude Code 直接統合の利点を失う |

## 3. 決定

**A. Notion 公式 Remote MCP** を採用。

### 3.1 設定

リポジトリ直下 `.mcp.json` に以下を配置（コミット済み）:

```json
{
  "mcpServers": {
    "notion": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

これで本リポで起動した全 Claude Code（teammate を含む）が同じ MCP に自動接続する。

### 3.2 認証

各 Claude Code インスタンスで初回 `/mcp` 実行時に OAuth フローを完了する。
認証情報は Claude Code 側で保管されるため `.env` にトークンを置かない。
`NOTION_TOKEN` は不要となり、`.env.example` から削除した。

`NOTION_BOARD_DATABASE_ID` のみ `.env` に残す。

## 4. 採用理由

1. **公式が活発に投資** — Notion 社は Remote MCP に開発リソースを集中させており、
   Local MCP は将来 sunset 予定と公式表明
2. **追加コードゼロ** — エージェントは MCP ツール（`create_page` / `query_database`
   等）を自然言語で呼び出せ、独自実装が要らない
3. **マルチエージェント整合性** — psmux ペインで動く各 Claude Code が同じ MCP を
   参照するため、振る舞いが揃いやすい
4. **トークン漏洩リスクの低減** — bearer token を `.env` で管理する必要がなく、
   OAuth で per-instance 認可

## 5. 却下理由

### 5.1 Local MCP を採用しない理由
- 公式が将来 sunset 予定と明言。長期維持コストが見えない
- npm/Docker のセットアップが各マシンで必要（マルチエージェント運用で煩雑）

### 5.2 自作 API クライアントを採用しない理由
- 開発コストが MCP の利点を上回らない（CRUD は MCP で十分）
- Claude Code との直接統合がない（Claude が自然言語でツールを呼ぶ仕組みを失う）
- 独自実装は Notion API バージョンアップへの追従責任が発生

## 6. MCP がカバーしない領域（将来課題）

| 課題 | 暫定対応 / 将来対応 |
|------|-------------------|
| スキーマ検証（必須フィールド抜け） | Claude 側にチェックリストを仕込む。バリデーション CLI は将来検討 |
| 月次アーカイブ等の一括処理 | 将来 Python/TS スクリプトで補完 |
| 通知レイヤ（新着検知） | MCP 非対応。`docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` の 4 候補から Tech Lead が選定 |

これらは MCP 採用とは独立した課題であり、必要になったタイミングで個別 PR で対応する。

## 7. リスクと監視

- **公式 Remote MCP 障害時**: 業務通信が完全停止する単一障害点。代替プランは未策定。
  Tech Lead に「Notion MCP が落ちた場合の運用」を ADR で検討させる候補とする
- **MCP ツール仕様変更**: Notion 社の更新でツール名・引数が変わる可能性あり。
  `/mcp` で都度確認する習慣をルール化（`docs/notion-board-schema.md` §5.3）

## 8. 関連ドキュメント

- `.mcp.json` — 設定ファイル本体
- `.env.example` — 環境変数テンプレート（`NOTION_TOKEN` 削除済）
- `docs/notion-board-schema.md` §5（API 連携を Remote MCP 前提に書き換え）
- `docs/notion-board-schema.md` §6（構築チェックリストに OAuth 手順を追加）

## 9. 参考情報

- [Notion 公式: Connecting to Notion MCP](https://developers.notion.com/docs/get-started-with-mcp)
- [makenotion/notion-mcp-server (Local 版・将来 sunset)](https://github.com/makenotion/notion-mcp-server)
- 公式エンドポイント: `https://mcp.notion.com/mcp`
