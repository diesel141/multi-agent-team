# 共通プロローグ（全ロール共通の整列・規律参照）

> 本ファイルはすべてのロール召喚指示書で参照される共通整列ブロック。
> 個別タスク指示書は `{{include: docs/templates/instructions/_common-prologue.md}}` または冒頭でこのファイルを Read するよう指示し、本文ではタスク固有差分のみを記述する。

## 0. 整列（全ロール共通）

1. 自分のペルソナファイルを読み内面化する:
   - PM: `docs/persona.md`（神崎玲奈）
   - Tech Lead: `docs/personas/tech_lead.md`（早瀬蒼）
   - Designer: `docs/personas/ui_ux_designer.md`（白井美雪）
   - BE/FE/SRE 等: `docs/personas/<role>.md`（起案後）
2. `CLAUDE.md` の §1 必須プロトコル / §3 歴史化 / §5 Git 運用 / §9 アンチパターンを再確認
3. 自分のロールに関連する `memory/feedback_*.md` を読み、当該タスクのドメインに当てはまる規律を受入基準・実装方針に折り込む
   - pptx 系タスク: `memory/feedback_pptx_review_discipline.md`
   - 用語集系タスク: `memory/feedback_glossary_review_discipline.md`
   - クロージング: `memory/feedback_task_closing_discipline.md`
   - PM ロール特有: `memory/feedback_pm_proactive_review.md` / `memory/feedback_pm_autonomy.md`
4. Notion で自分のタスクの開始指令を取得しステータスを「進行中」に更新
5. 受領後 30 分以内に **着手返答（informal）** を Notion に投稿

## 1. 業務通信プロトコル（Notion 7 種メッセージ）

formal 3 種 + informal 4 種。掲示板以外の IM チャネル（Slack 等）の提案・新設は禁止（CLAUDE.md §1.3）。

| 種別 | 用途 |
|------|------|
| 開始指令 (formal) | タスク発出 / 必須項目: タスクID・受領者・背景・成果物定義・期日・受入基準・依存関係 |
| 完了報告 (formal) | タスク完遂 / 必須項目: 成果物リンク・受入基準照合結果・残課題・学び |
| 問題報告 (formal) | ブロッカー / 必須項目: タスクID・事実・影響範囲・想定原因・必要な支援・期日影響 |
| 着手返答 (informal) | 受領から 30 分以内 |
| 進捗共有 (informal) | 判断・状態遷移の単位（ログ単位禁止） |
| 質疑応答 (informal) | 仕様の不確実性を解消する一問一答 |
| 議論 (informal) | 複数選択肢の比較・トレードオフ言語化（ADR / 歴史化メモ昇格候補） |

## 2. 厳守事項（全ロール共通）

- worktree 隔離禁止（Windows 環境の制約 / CLAUDE.md §1.1）
- send-keys による業務指示禁止（CLAUDE.md §1.2）
- ADR ハウススタイル: 採用案・却下案・**再考閾値** を 100% 明示（`memory/adr_house_style.md`）
- 開始指令受領時にスコープ外の作業を勝手に拡張しない（必要なら問題報告 or 質疑応答）
- 完了報告には必ず「採用案 / 却下案 / 再考閾値」「学び」を含める

## 3. 権限境界（2026-04-27 確定）

- **PM**: スコープ / 期日 / 受入基準 / 最終受入判定 / **人材ペルソナ起案** / 歴史化メモ起票
- **Designer**: UX 仕様確定（padding / vertical anchor / typography / grid）/ 実描画検証
- **Tech Lead**: コード品質 / アーキテクチャ判断 / **PR レビューとマージ**
- **BE / FE / SRE 等**: ドメイン実装 / Tech Lead レビューを通す

PM は UX 仕様を裁量で確定しない。Tech Lead は PR マージ判断を担う（PM はマージしない）。

## 4. 完了時の返り値（呼び出し元への報告）

完了報告を Notion に投稿したら、呼び出し元セッションには **3 行で要点のみ** 返す:
1. 採用した主要仕様 / 数値根拠
2. 受入基準の PASS 確認
3. 残課題 / 申し送り
