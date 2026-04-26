# Designer タスク指示書テンプレート

> 使い方: 本ファイルをコピーして `.designer-task-NNNN-instructions.md` を作り、`{{}}` プレースホルダを埋める。完了後にコピー元（隠しファイル）は削除する。

## 0. 整列

`docs/templates/instructions/_common-prologue.md` を Read して整列せよ。あなたのペルソナは `docs/personas/ui_ux_designer.md`（白井美雪）。

特に **PM の越権を発見したら指摘する** 権限を持つ（Designer ペルソナ §8 / §11）。PM が UX 仕様（pt 値・anchor・grid）を裁量で確定していたら「Designer 領域です」と差し戻すこと。

## 1. タスク

- **タスクID**: TASK-{{NNNN}}
- **タイトル**: {{title}}
- **Notion 開始指令**: {{notion_url}}
- **背景・経緯**: {{context}}

## 2. 修正対象

- **ファイル**: {{target_files}}
- **対象スライド/画面**: {{target_slides_or_screens}}
- **対象要素**: {{target_elements}}
- **現状**: {{current_state_with_numbers}}

## 3. 制約・継承（破壊禁止の既存規律）

- TASK-0007 で確立した規律を維持: 内部 padding 対称（diff < 0.10 inch）/ 8pt baseline grid / vertical anchor=MIDDLE で実テキスト中央寄せ
- 影響を与えてはいけない既存スライド: {{out_of_scope_slides}}
- {{additional_constraints}}

## 4. 受入基準（pptx 系の既定 12 項目 + タスク固有）

`docs/templates/checklists/pptx-acceptance.md` を参照して 12 項目を満たすこと。タスク固有の追加項目:
- {{extra_acceptance_criteria}}

## 5. 検証スクリプト

`scripts/verify/pptx_internal_padding.py` を実行し、対象 container がすべて PASS することを確認。実描画 PDF を `build/` に生成（PowerPoint COM or LibreOffice CLI）し目視確認。

## 6. 期日

{{deadline}}

## 7. 完了報告（テンプレ）

`docs/templates/notion/completion-report.md` のフォーマットに従い、内部 padding ダンプ表 + Squint test 結果 + 採用案/却下案/再考閾値を必ず含める。
