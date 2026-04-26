# Tech Lead タスク指示書テンプレート

> 使い方: 本ファイルをコピーして `.tech-lead-task-NNNN-instructions.md` を作り、`{{}}` プレースホルダを埋める。完了後にコピー元（隠しファイル）は削除する。

## 0. 整列

`docs/templates/instructions/_common-prologue.md` を Read して整列せよ。あなたのペルソナは `docs/personas/tech_lead.md`（早瀬蒼）。

権限境界の確認: あなたは **PR レビューとマージ** の責務を持つ（PM はマージしない）。本タスクで PR を起こした場合、レビューしてマージするのもあなたの仕事。

## 1. タスク

- **タスクID**: TASK-{{NNNN}}
- **タイトル**: {{title}}
- **Notion 開始指令**: {{notion_url}}
- **背景・経緯**: {{context}}

## 2. 成果物

- **対象ファイル**: {{target_files}}
- **新規作成ファイル**: {{new_files}}
- **既存修正ファイル**: {{modified_files}}

## 3. ADR ハウススタイル（ADR 起案タスクの場合）

`memory/adr_house_style.md` を参照。採用案・却下案ごとの「再考閾値」を 100% 明示（漏れは merge ブロッカー）。§5 で議論論点を列挙。

## 4. 受入基準

- {{acceptance_criteria_list}}
- 完了報告に成果物リンク・受入基準照合結果・残課題・学び・採用案理由を明記

## 5. PR 起票

- ブランチ命名: `<種別>/<短いトピック>` 形式（feature/fix/docs/chore）
- base: `development`
- マージ方式: squash（あなたが自身で実行）

## 6. 期日

{{deadline}}

## 7. 完了報告（テンプレ）

`docs/templates/notion/completion-report.md` のフォーマットに従う。
