# pptx タスク受入基準チェックリスト（既定 12 項目）

> pptx 系タスク（slide 修正・font 変更・layout 変更等）の Designer 完了報告に対する PM 受入レビュー時に使う。
> タスク固有項目は本リストの 12 項目に追加する。

## 既定 12 項目

### 機械検証（4 項目）

- [ ] **1. 文字列削除/置換の正確性**: script grep + pptx grep で対象文字列が期待通り（grep 0 件 / N 件）
- [ ] **2. ビルド成功・slide 総数不変**: `python scripts/build_*.py` 成功、slide 総数が期待値
- [ ] **3. P17 等のスコープ外スライド副作用ゼロ**: 全 shape 座標・auto_shape_type・テキストが before/after 完全一致
- [ ] **4. 改修後 pptx 構造ダンプ**: 対象スライドの shape 列挙と座標を完了報告に添付

### shape padding 検証（3 項目）

- [ ] **5. shape 内部 padding 対称**: 各 box / col について top_pad と bottom_pad の差が 0.10 inch 以内
- [ ] **6. inter-element gap 均等**: 隣接 child element 間の gap のばらつきが 0.10 inch 以内（局所的不対称禁止）
- [ ] **7. 内部 padding ダンプ表添付**: 完了報告に表形式で `top_pad / bottom_pad / diff / max_gap / gap_range / grid8 / verdict`

### Designer 領域検証（3 項目）

- [ ] **8. textbox / body 領域の実テキスト中央寄せ**: vertical anchor MIDDLE / 高さ縮小 / padding 増のいずれかで領域中央付近に配置
- [ ] **9. 8pt baseline grid 整合**: vertical 間隔が 8pt = 0.111 inch の倍数（明示した別 grid を採用する場合は理由明示）
- [ ] **10. Squint test 実施記録**: 各対象スライドのヒエラルキー / 重心 / バランスを 1-2 行で記述

### プロセス検証（2 項目）

- [ ] **11. 実描画 PDF 添付**: PowerPoint COM or LibreOffice CLI で対象スライドを PDF 化、Designer 目視確認結果を明記
- [ ] **12. 完了報告必須項目**: 成果物リンク・受入基準照合・残課題・学び・採用案理由 + 却下案の再考閾値

## PM 独立検証スクリプト

機械検証と shape padding 検証は `scripts/verify/pptx_internal_padding.py` で独立実行できる:

```bash
cd <target_repo>
PYTHONIOENCODING=utf-8 python <multi-agent-team>/scripts/verify/pptx_internal_padding.py <pptx_path> --slides 17-22
```

PM は Designer 完了報告の数値主張を信頼せず、本スクリプトを独立実行して 14/14 PASS 等を再現すること。

## logical element merge（誤検出防止）

raw shape を flat に children として扱うと、装飾 shape（bullet circle・pill rect・装飾 band）を独立子要素と数えて gap 計算が歪む。検証スクリプトは:
1. y range で装飾を吸収（child A の y range が child B の y range に完全包含されるとき、A は B の装飾として merge）
2. top + height 同一 shape（許容 0.025 inch）を 1 論理要素にマージ
3. 負 gap が出たら logical merge の漏れを疑う

## 不合格時の対応

- 不合格理由は **数値で提示**（「気持ち悪い」だけで終わらない）
- 再修正方針は **Designer 領域**に委ねる（PM が pt 値・anchor 等を裁量で確定しない）
- 撤回された完了報告は Notion ステータス「却下」マーク
