# scripts/verify/

PM 受入レビュー時 / Designer 自己照合時 / Tech Lead 検証時に使う共通検証スクリプト集。

ロール側のサブリポでスクリプトを毎回再発明せず、本リポに集約することで再利用性を高める。

## 一覧

### `pptx_internal_padding.py`

pptx 内部 padding 対称性 + inter-element gap 均等性 + 8pt baseline grid 整合を検証する。

- 起源: TASK-0007 で Designer 白井美雪が `W:\ai_training_for_rjc\scripts\verify_internal_padding.py` として起案
- 汎用化: TASK-0010 chore で本リポに集約し pptx パスを引数化、exit code で PASS/FAIL を返すよう改修

```bash
# pptx 全スライドを検証
python scripts/verify/pptx_internal_padding.py path/to/your.pptx

# 特定スライド範囲のみ
python scripts/verify/pptx_internal_padding.py path/to/your.pptx --slides 17-22

# 詳細 child ダンプも出力
python scripts/verify/pptx_internal_padding.py path/to/your.pptx --slides 17-22 --detail-slides 18-19

# 閾値カスタマイズ（既定 0.10 inch）
python scripts/verify/pptx_internal_padding.py path/to/your.pptx --padding-diff-threshold 0.05

# Exit code: 0=全 PASS, 1=FAIL あり, 2=エラー
```

## 想定追加スクリプト（順次拡充）

- `notion_status_audit.py`: タスク ID 横断で Notion メッセージのステータスを点検（クロージング工程 C 自動化）
- `feedback_compliance_lint.py`: Notion 完了報告に「採用案 / 却下案 / 再考閾値」が揃っているか自動チェック
- `glossary_grain_check.py`: 用語集系の粒度整合チェック

追加時は本 README に簡単な使用例を載せること。

## 設計方針

- 各スクリプトは引数で対象パス・パラメータを受け取り、本リポに依存しない（他のサブリポからも呼べる）
- exit code で PASS/FAIL を返す（CI / pre-commit hook で使えるように）
- 出力は markdown テーブル形式を基本（完了報告に貼り付けやすい）
