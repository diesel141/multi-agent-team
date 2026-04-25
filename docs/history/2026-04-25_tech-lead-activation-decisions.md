---
date: 2026-04-25
type: decision / team-composition
title: Tech Lead 起用に関する確定事項
status: 決定済（Notion 掲示板の最初の開始指令で実行に移す）
tags: [team, tech-lead, persona, activation, governance]
---

# Tech Lead 起用に関する確定事項

## 1. 背景

PR #1 (`docs: Tech Lead ペルソナ起案 (早瀬蒼)`) の §11 にて、Tech Lead 起用の前に
ユーザーへ確認すべき項目を 4 つ列挙していた。本ファイルはそれら 4 項目への回答と
確定事項を記録する。

## 2. 決定事項

### 2.1 ペルソナ承認 (§11.1)

- **早瀬 蒼 / Sou Hayase** を Tech Lead として起用することを **承認**
- ペルソナ詳細: `docs/personas/tech_lead.md`
- 経歴・スキルセット・スタイルへの修正要望なし

### 2.2 権限境界 (§11.2)

`docs/personas/tech_lead.md` §5「責任範囲（Scope of Authority）」の表に **異論なし**。
要約:

| 領域 | 決定権 |
|------|--------|
| 技術スタック選定（言語・FW・DB・クラウド） | Tech Lead |
| アーキテクチャ設計（API・データモデル・コンポーネント分割） | Tech Lead |
| サブリポジトリ作成判断と境界 | Tech Lead（PM 承認） |
| コードレビュー基準・PR テンプレ・自動化 | Tech Lead |
| 個別エージェントへの技術タスク委譲 | Tech Lead |
| プロダクト要件・スコープ・優先順位・期日・予算 | PM |

### 2.3 起用タイミング (§11.3)

**A. 即時常駐** を採用。

- タスクなしの状態でも Tech Lead を起動し、プロジェクト全体の技術監督として張り付き
- 初期常駐期間中に「標準スタック策定」「次メンバー提案」「PR テンプレ整備」等の
  土台作りを並行で進める

### 2.4 次にアサインする職種 (§11.4)

**Tech Lead に任せる**。

- Tech Lead が次メンバーを ADR 形式で起案（候補職種・選定理由・初期タスク案）
- PM 神崎が承認 → 起動指令という流れ
- PM/ユーザーから職種を指名することはしない（Tech Lead の判断を尊重）

## 3. 直近のアクション

1. **Notion 掲示板の構築**: スキーマは `docs/notion-board-schema.md`、
   API キー類のテンプレは `.env.example` に定義済み
2. **PM 神崎の最初の開始指令** `docs/notion-messages/2026-04-25_001_tech-lead-onboarding.md`
   を Tech Lead に向けて発行（標準スタック ADR + 次メンバー提案 ADR の起案を依頼）
3. Tech Lead 起動 → 開始指令受領 → ADR 起票 → PM 承認 → 次メンバー起用へ

## 4. なぜこれを残すか

- 「即時常駐」「次メンバーを Tech Lead に委譲」は **チーム拡張の判断権限を Tech Lead に
  移譲する重要な決定**。後日「なぜ PM がメンバー指名しなかったのか」を辿れるようにする
- pptx レポート時に「Tech Lead 起用の判断プロセス」を再構成できる単位で残す

## 5. 関連ドキュメント

- `docs/personas/tech_lead.md` — Tech Lead ペルソナ本体
- `docs/persona.md` — PM ペルソナ
- `docs/notion-board-schema.md` — 掲示板スキーマ
- `docs/notion-messages/2026-04-25_001_tech-lead-onboarding.md` — 最初の開始指令
