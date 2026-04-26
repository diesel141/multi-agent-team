# 開始指令テンプレート（formal）

> Notion Messages DB に投稿する formal 開始指令の必須項目テンプレート。
> 種別=開始指令、ステータス=未着手、優先度=P0/P1/P2、受領者=対象ロール。

## タイトル
[TASK-NNNN] {{簡潔なタスク名}}

## プロパティ
- タスクID: TASK-NNNN
- 種別: 開始指令
- 発信者: PM
- 受領者: {{Tech Lead / Designer / BE / FE / SRE / ...}}
- 優先度: {{P0 / P1 / P2}}
- ステータス: 未着手
- 期日: {{YYYY-MM-DD}}

## 本文構造

```markdown
## 背景
{{なぜこのタスクが必要か。トリガとなったユーザー指示・問題報告・依存タスクの URL}}

## 成果物定義
{{何を生成するか。ファイル・コミット・PR・Notion 投稿など具体的に}}

## 期日
{{YYYY-MM-DD HH:MM JST}}

## 受入基準
1. {{Specific / Measurable / 数値で書ける項目}}
2. ...
N. 完了報告必須項目: 成果物リンク・受入基準照合・残課題・学び・採用案理由

## 依存関係
- 前提タスク: {{TASK-NNNN or なし}}
- 必要権限: {{ファイル書き込み・MCP・外部 API 等}}
- 必要情報: {{PM 事前調査結果・参照 URL 等}}

## 起動方式
{{外部プロセス `claude --dangerously-skip-permissions ...` / harness Agent ツール / 既存セッション}}

## 着手返答
受領後 30 分以内に informal「着手返答」を Notion 投稿。
```

## SMART チェック（PM 投稿前に自己点検）
- [ ] **Specific**: 何を作るかが明確
- [ ] **Measurable**: 受入基準が数値・PASS/FAIL で判定可能
- [ ] **Achievable**: 受領者のスキル・利用可能時間で達成可能
- [ ] **Relevant**: 上位目標とのつながりが明示
- [ ] **Time-bound**: 期日が具体的
