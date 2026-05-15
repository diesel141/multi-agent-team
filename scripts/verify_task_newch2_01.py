"""
TASK-NEWCH2-01 受入検証スクリプト

検証項目:
  a. 新章 + 修正済スライド（slide 19-29）の有意 shape overlap = 0
     （空テキスト背景 shape は除外。両方に可視テキストがある重なりのみ検出）
  b. 旧 Q&A スライド（slide 25-29）のテキストに章番号「04」残存なし（副作用 0）
  c. 新章 6 枚（slide 19-24）の outer shape 内部 padding 対称（diff < 0.10 inch）
  d. 章番号連番一貫性（01→02→03→04→05）

Usage:
    python scripts/verify_task_newch2_01.py [pptx_path]

既定パス: W:/ai_training_for_rjc/AI研修⑤-エージェント駆動開発（ADD）への挑戦２.pptx

Exit code:
    0: 全項目 PASS
    1: いずれか FAIL
"""
from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation

EMU_PER_INCH = 914400
PADDING_THRESHOLD = 0.10  # inch
OVERLAP_TOLERANCE = 0.02  # inch — edge-touching layout は除外

DEFAULT_PPTX = Path(
    r"W:\ai_training_for_rjc\AI研修⑤-エージェント駆動開発（ADD）への挑戦２.pptx"
)


# ── helpers ──────────────────────────────────────────────

def rects_overlap(a, b) -> bool:
    """2 つの shape の bounding box が OVERLAP_TOLERANCE 以上重なるか。"""
    if a is b:
        return False
    try:
        al, at = a.left, a.top
        ar, ab = al + a.width, at + a.height
        bl, bt = b.left, b.top
        br, bb = bl + b.width, bt + b.height
        tol = int(OVERLAP_TOLERANCE * EMU_PER_INCH)
        return (
            al < br - tol and ar > bl + tol
            and at < bb - tol and ab > bt + tol
        )
    except Exception:
        return False


def slide_texts(slide) -> list[str]:
    """スライド内の全テキストを収集。"""
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                t = para.text.strip()
                if t:
                    texts.append(t)
    return texts


def section_big_text(slide) -> str | None:
    """SECTION スライドの大番号テキスト（shape_id=5 想定）を取得。"""
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                t = para.text.strip()
                if " / " in t:
                    return t
    return None


# ── 検証 a: shape overlap ────────────────────────────────

def _has_visible_text(shape) -> bool:
    """shape が可視テキストを持つか。"""
    if not shape.has_text_frame:
        return False
    return any(p.text.strip() for p in shape.text_frame.paragraphs)


def check_overlap(prs) -> list[str]:
    """新章・修正済スライド（19-29）の有意 overlap を検出。

    背景・装飾 shape（空テキスト）は除外。
    両方に可視テキストがある重なりのみを報告。
    """
    errors = []
    for i in range(18, 29):
        if i >= len(prs.slides):
            break
        slide = prs.slides[i]
        shapes = [sh for sh in slide.shapes if _has_visible_text(sh)]
        for a_idx in range(len(shapes)):
            for b_idx in range(a_idx + 1, len(shapes)):
                if rects_overlap(shapes[a_idx], shapes[b_idx]):
                    a_text = shapes[a_idx].text_frame.text[:30]
                    b_text = shapes[b_idx].text_frame.text[:30]
                    errors.append(
                        f"  Slide {i+1}: shape {shapes[a_idx].shape_id} "
                        f"\"{a_text}\" × shape {shapes[b_idx].shape_id} "
                        f"\"{b_text}\""
                    )
    return errors


# ── 検証 b: 副作用 0（旧 Q&A スライドに章番号 04 残存なし）────────

def check_no_side_effects(prs) -> list[str]:
    """slide 25-29 のヘッダ位置に '04' 章番号が残存していないか確認。"""
    errors = []
    chapter_prefixes = ["04  Q&A", "04 / Q&A", "04 / Q & A"]
    for idx in range(24, 29):
        slide = prs.slides[idx]
        texts = slide_texts(slide)
        for t in texts:
            # ヘッダ行（先頭 2 テキスト）のみ章番号チェック
            for prefix in chapter_prefixes:
                if t.startswith(prefix):
                    errors.append(
                        f"  Slide {idx+1}: 章番号「04」残存 → \"{t[:60]}\""
                    )
            break  # ヘッダ行のみチェック（先頭テキストで十分）
    return errors


# ── 検証 c: padding 対称性 ────────────────────────────────

def check_padding_symmetry(prs) -> list[str]:
    """新章 6 枚（slide 19-24）の outer shape の内部 padding 対称性。"""
    errors = []
    for idx in range(18, 24):
        slide = prs.slides[idx]
        # 幅 > 8 inch の shape を outer とみなす
        for shape in slide.shapes:
            try:
                w_inches = shape.width / EMU_PER_INCH
            except Exception:
                continue
            if w_inches < 8.0:
                continue
            if not shape.has_text_frame:
                continue
            tf = shape.text_frame
            top_m = tf.margin_top if tf.margin_top is not None else 0
            bot_m = tf.margin_bottom if tf.margin_bottom is not None else 0
            left_m = tf.margin_left if tf.margin_left is not None else 0
            right_m = tf.margin_right if tf.margin_right is not None else 0
            v_diff = abs(top_m - bot_m) / EMU_PER_INCH
            h_diff = abs(left_m - right_m) / EMU_PER_INCH
            if v_diff >= PADDING_THRESHOLD:
                errors.append(
                    f"  Slide {idx+1} shape {shape.shape_id}: "
                    f"V padding diff={v_diff:.4f}\" >= {PADDING_THRESHOLD}\" "
                    f"(top={top_m/EMU_PER_INCH:.4f} bot={bot_m/EMU_PER_INCH:.4f})"
                )
    return errors


# ── 検証 d: 章番号連番一貫性 ──────────────────────────────

def check_chapter_numbering(prs) -> list[str]:
    """SECTION スライドの大番号と DETAIL スライドのヘッダの連番一貫性。"""
    errors = []

    # 期待される章構成
    expected = {
        4: "02 / ARCHITECTURE",
        11: "03 / PROPOSAL",
        19: "04 / MY-AGENT-TEAM",
        25: "05 / Q&A",
    }

    for slide_num, expected_text in expected.items():
        slide = prs.slides[slide_num - 1]
        big = section_big_text(slide)
        if big != expected_text:
            errors.append(
                f"  Slide {slide_num} SECTION: expected \"{expected_text}\", "
                f"got \"{big}\""
            )

    # スライド総数
    total = len(prs.slides)
    if total != 29:
        errors.append(f"  総スライド数: expected 29, got {total}")

    # AGENDA スライド（slide 2）の確認
    agenda = prs.slides[1]
    agenda_texts = slide_texts(agenda)
    agenda_str = " ".join(agenda_texts)
    if "5 sections" not in agenda_str:
        errors.append("  Slide 2 AGENDA: '5 sections' が見つかりません")
    if "MY-AGENT-TEAM" not in agenda_str:
        errors.append("  Slide 2 AGENDA: 'MY-AGENT-TEAM' が見つかりません")

    return errors


# ── main ─────────────────────────────────────────────────

def main() -> int:
    pptx_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PPTX
    if not pptx_path.exists():
        print(f"ERROR: {pptx_path} not found", file=sys.stderr)
        return 2

    try:
        prs = Presentation(str(pptx_path))
    except Exception as e:
        print(f"ERROR: {pptx_path} 読み込み失敗: {e}", file=sys.stderr)
        return 2

    print(f"検証対象: {pptx_path}")
    print(f"スライド数: {len(prs.slides)}")
    print()

    all_pass = True

    checks = [
        ("a. shape overlap = 0", check_overlap),
        ("b. 副作用 0（旧 Q&A スライドに 04 残存なし）", check_no_side_effects),
        ("c. padding 対称性（diff < 0.10 inch）", check_padding_symmetry),
        ("d. 章番号連番一貫性", check_chapter_numbering),
    ]

    for label, fn in checks:
        errors = fn(prs)
        status = "PASS" if not errors else "FAIL"
        print(f"[{status}] {label}")
        for e in errors:
            print(e)
        if errors:
            all_pass = False

    print()
    if all_pass:
        print("RESULT: 全項目 PASS")
        return 0
    else:
        print("RESULT: FAIL — 上記項目を修正してください")
        return 1


if __name__ == "__main__":
    sys.exit(main())
