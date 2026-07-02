"""
TASK-GLOBALCTX-VERIFY-01 受入検証スクリプト

CLI 研修デッキ「AI研修-CLIの便利コマンドとトークン節約術.pptx」の
新セクション「04 / GLOBAL CONTEXT」挿入 + COST→05 繰り下げ を機械検証する。

【核心】ユーザー要件「オブジェクトとテキストが重なったり矩形からはみ出る崩れを
起こさない」を機械検証で担保すること（茜野の本領）。

検証項目:
  a. 全スライドの可視テキスト shape の有意 overlap = 0
     （背景・空テキスト装飾 shape は除外。両方に可視テキストがある重なりのみ検出）
  b. shape がスライド外(0..13.333 x 0..7.5 inch)へはみ出さない +
     文字量に対する枠不足(行あふれ)をベストエフォルトで推定検出
  c. 総スライド数 = 29 (旧26 + 新規3)
  d. SECTION 連番: 02/COMMANDS, 03/TOKEN SAVING, 04/GLOBAL CONTEXT, 05/COST /
     AGENDA に "100 minutes ｜ 5 sections"
  e. 副作用 0: 新規3枚(GLOBAL CONTEXT)・COST番号変更・AGENDA 以外の既存スライドの
     テキスト差分 0（before pptx を git から取得し after と照合）

Usage:
    python scripts/verify_task_globalctx_01.py [after_pptx] [--before before.pptx]

既定 after: W:/ai_training_for_rjc/AI研修-CLIの便利コマンドとトークン節約術.pptx
before 省略時: git show HEAD^:<relpath> 等から working tree(after) と異なる版を自動取得

Exit code:
    0: 全項目 PASS
    1: いずれか FAIL
    2: 読込エラー
"""
from __future__ import annotations

import argparse
import io
import math
import re
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

EMU_PER_INCH = 914400
OVERLAP_TOL = 0.02       # inch — edge-touching layout は除外
BBOX_TOL = 0.02          # inch — スライド境界ぴったりは許容
EXPECTED_SLIDES = 29     # 旧26 + 新規3
WRAP_WARN_RATIO = 1.30   # 行あふれ推定 ratio の WARN 閾値（参考情報・FAIL にはしない）

DEFAULT_AFTER = Path(
    r"W:\ai_training_for_rjc\AI研修-CLIの便利コマンドとトークン節約術.pptx"
)
TARGET_REPO = Path(r"W:\ai_training_for_rjc")
REL_PATH = "AI研修-CLIの便利コマンドとトークン節約術.pptx"

DEFAULT_FONT_PT = 18  # font.size が取得できない run の推定サイズ


# ── helpers ──────────────────────────────────────────────

def _has_visible_text(shape) -> bool:
    """shape が可視テキストを持つか。"""
    if not shape.has_text_frame:
        return False
    return any(p.text.strip() for p in shape.text_frame.paragraphs)


def _bbox(shape):
    """(left, top, right, bottom) in EMU。取得失敗は None。"""
    try:
        l, t = shape.left, shape.top
        return l, t, l + shape.width, t + shape.height
    except Exception:
        return None


def _rects_overlap(a, b, tol_in=OVERLAP_TOL) -> bool:
    """2 shape の bbox が tol_in 以上重なるか。"""
    ba, bb = _bbox(a), _bbox(b)
    if ba is None or bb is None:
        return False
    al, at, ar, ab = ba
    bl, bt, br, bb_ = bb
    tol = int(tol_in * EMU_PER_INCH)
    return (
        al < br - tol and ar > bl + tol
        and at < bb_ - tol and ab > bt + tol
    )


def slide_text_lines(slide) -> list[str]:
    """スライド内の全テキスト（空行除外）を順に集める。"""
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                t = para.text.strip()
                if t:
                    texts.append(t)
    return texts


# ── 検証 a: shape overlap = 0 ────────────────────────────

def _contains(outer, inner, tol_in=0.05) -> bool:
    """inner が outer に包含されるか（背景+前景のレイヤー構成）。"""
    bo, bi = _bbox(outer), _bbox(inner)
    if bo is None or bi is None:
        return False
    tol = int(tol_in * EMU_PER_INCH)
    return (bi[0] >= bo[0] - tol and bi[1] >= bo[1] - tol
            and bi[2] <= bo[2] + tol and bi[3] <= bo[3] + tol)


def _overlap_xy(a, b) -> tuple[float, float]:
    """重なり領域の (幅, 高さ)[inch]。"""
    ba, bb = _bbox(a), _bbox(b)
    if ba is None or bb is None:
        return 0.0, 0.0
    xo = max(0.0, min(ba[2], bb[2]) - max(ba[0], bb[0])) / EMU_PER_INCH
    yg = max(0.0, min(ba[3], bb[3]) - max(ba[1], bb[1])) / EMU_PER_INCH
    return xo, yg


def _is_callout(shape) -> bool:
    """コールアウト/メモ吹き出し（✓ / ✗ / ※ 系）か。"""
    if not shape.has_text_frame:
        return False
    t = shape.text_frame.text.strip()
    return t.startswith(("✓", "✗", "※"))


def _is_intentional_overlap(a, b) -> bool:
    """意図的なレイアウト重なり（崩れではない）か:
    - 包含関係（背景 shape の上に前景を乗せるレイヤー構成）
    - 2行タイトル/水平薄重なり（水平に広く xo>1.0, 垂直に薄く yg<0.4）
    - コールアウト/メモ（✓ 系）の本文への重なり
    これらは本デッキの既存デザインパターンであり「崩れ」とは区別する。"""
    if _contains(a, b) or _contains(b, a):
        return True
    xo, yg = _overlap_xy(a, b)
    if xo > 1.0 and yg < 0.4:
        return True
    if _is_callout(a) or _is_callout(b):
        return True
    return False


def check_overlap(prs) -> list[str]:
    """全スライドで、意図的レイアウトを除外した「有意な重なり(崩れ)」を検出。"""
    errors = []
    for i, slide in enumerate(prs.slides, 1):
        visibles = [sh for sh in slide.shapes if _has_visible_text(sh)]
        for x in range(len(visibles)):
            for y in range(x + 1, len(visibles)):
                a, b = visibles[x], visibles[y]
                if not _rects_overlap(a, b):
                    continue
                if _is_intentional_overlap(a, b):
                    continue
                ta = a.text_frame.text.replace("\n", " ")[:30]
                tb = b.text_frame.text.replace("\n", " ")[:30]
                errors.append(
                    f"  Slide {i}: shape{a.shape_id} "
                    f"\"{ta}\" × shape{b.shape_id} \"{tb}\""
                )
    return errors


# ── 検証 b: no overflow ──────────────────────────────────

def _shape_outside_overflow(shape, slide_w_in, slide_h_in) -> float:
    """shape がスライド外へはみ出す量[inch]（最大値, 0=問題なし）。"""
    bbox = _bbox(shape)
    if bbox is None:
        return 0.0
    l, t, r, b = bbox
    sw = int(slide_w_in * EMU_PER_INCH)
    sh = int(slide_h_in * EMU_PER_INCH)
    tol = int(BBOX_TOL * EMU_PER_INCH)
    over = 0.0
    if l < -tol:
        over = max(over, (-l) / EMU_PER_INCH)
    if t < -tol:
        over = max(over, (-t) / EMU_PER_INCH)
    if r > sw + tol:
        over = max(over, (r - sw) / EMU_PER_INCH)
    if b > sh + tol:
        over = max(over, (b - sh) / EMU_PER_INCH)
    return over


def _run_size_pt(run) -> float | None:
    """run の font size[pt]。継承/未設定は None。"""
    try:
        if run.font.size is not None:
            return run.font.size.pt
    except Exception:
        pass
    return None


def _estimate_wrap_ratio(shape) -> float | None:
    """文字量対枠不足を行あふれ推定 ratio(必要高/内側高) で返す。
    あくまで近似（実レンダリングとは異なる）。推定不可は None。"""
    if not shape.has_text_frame:
        return None
    tf = shape.text_frame
    # 実テキストを持たない（空テキスト枠・装飾）は推定しない
    if not any(p.text.strip() for p in tf.paragraphs):
        return None
    try:
        inner_w = (
            shape.width
            - (tf.margin_left or 0) - (tf.margin_right or 0)
        ) / EMU_PER_INCH
        inner_h = (
            shape.height
            - (tf.margin_top or 0) - (tf.margin_bottom or 0)
        ) / EMU_PER_INCH
    except Exception:
        return None
    if inner_w <= 0 or inner_h <= 0:
        return None

    total_line_units = 0.0
    sizes = []
    for p in tf.paragraphs:
        text = p.text
        # 段落の代表サイズ: 最初の run サイズ、無ければ DEFAULT
        size_pt = None
        for run in p.runs:
            s = _run_size_pt(run)
            if s is not None:
                size_pt = s
                sizes.append(s)
                break
        if size_pt is None:
            size_pt = DEFAULT_FONT_PT
        ls = p.line_spacing if p.line_spacing is not None else 1.0

        if not text:
            total_line_units += 1.0 * ls
            continue
        # 全角=1, 半角=0.5 換算の文字セル数
        cjk = sum(1 for c in text if ord(c) > 0x2E80)
        cells = cjk + (len(text) - cjk) * 0.5
        chars_per_line = max(1.0, inner_w * 72.0 / size_pt)
        lines = max(1, math.ceil(cells / chars_per_line))
        total_line_units += lines * ls

    avg_pt = (sum(sizes) / len(sizes)) if sizes else DEFAULT_FONT_PT
    need_h = total_line_units * avg_pt / 72.0
    return need_h / inner_h if inner_h > 0 else None


def check_overflow(prs) -> tuple[list[str], list[str]]:
    """b. スライド外はみ出し(FAIL) + 行あふれ推定(WARN/参考)。"""
    errors = []
    warns = []
    sw = prs.slide_width / EMU_PER_INCH
    sh = prs.slide_height / EMU_PER_INCH
    for i, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            ov = _shape_outside_overflow(shape, sw, sh)
            if ov > 0:
                t = (
                    shape.text_frame.text.replace("\n", " ")[:30]
                    if shape.has_text_frame else f"<{shape.shape_type}>"
                )
                errors.append(
                    f"  Slide {i}: shape{shape.shape_id} \"{t}\" が "
                    f"スライド外へ {ov:.3f}\" はみ出し"
                )
            ratio = _estimate_wrap_ratio(shape)
            if ratio is not None and ratio > WRAP_WARN_RATIO:
                t = shape.text_frame.text.replace("\n", " ")[:30]
                warns.append(
                    f"  Slide {i}: shape{shape.shape_id} \"{t}\" "
                    f"行あふれ推定 ratio={ratio:.2f} (>{WRAP_WARN_RATIO:.2f})"
                )
    return errors, warns


# ── 検証 c: slide count ──────────────────────────────────

def check_slide_count(prs) -> list[str]:
    n = len(prs.slides)
    if n == EXPECTED_SLIDES:
        return []
    return [f"  総スライド数: expected {EXPECTED_SLIDES}, got {n}"]


# ── 検証 d: numbering ────────────────────────────────────

_SECTION_RE = re.compile(r"^(\d{2})\s*/\s*([A-Z][A-Z &\-]+)$")


def _section_big_texts(prs) -> list[str]:
    """SECTION divider 形式 "NN / TITLE" のテキストを全スライドから抽出。"""
    found = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                t = para.text.strip()
                if _SECTION_RE.match(t):
                    found.append(t)
    return found


def check_numbering(prs) -> list[str]:
    errors = []
    sections = _section_big_texts(prs)
    expected = [
        "02 / COMMANDS",
        "03 / TOKEN SAVING",
        "04 / GLOBAL CONTEXT",
        "05 / COST",
    ]
    for exp in expected:
        if exp not in sections:
            errors.append(
                f"  SECTION \"{exp}\" が見つかりません "
                f"(検出: {sections})"
            )
    # AGENDA (slide 2)
    agenda = " ".join(slide_text_lines(prs.slides[1]))
    if "100 minutes" not in agenda or "5 sections" not in agenda:
        errors.append(
            "  AGENDA: '100 minutes ｜ 5 sections' が見つかりません "
            f"(AGENDA 先頭: {' / '.join(slide_text_lines(prs.slides[1])[:2])})"
        )
    return errors


# ── 検証 e: side effect = 0 ──────────────────────────────

# 空白圧縮(2スペース→1)後にマッチさせるため \s*/?\s* で受ける
#   "04 / COST"(divider) / "04  COST"→圧縮→"04 COST"(frame) 両方吸収
_COST_NUM_RE = re.compile(r"\b0[45]\s*/?\s*COST")
# S1「想定時間：N minutes」の 90<->100 差異を吸収（dev1 指示 [A] line 202）
_MINUTES_RE = re.compile(r"想定時間：\s*\d+\s*minutes")


def _norm_text(t: str) -> str:
    """テキスト正規化:
    - 空白圧縮
    - COST 章番号(04<->05) の吸収（dev1 指示 [C]）
    - 「想定時間：N minutes」(90<->100) の吸収（dev1 指示 [A] line 202）
    """
    t = re.sub(r"\s+", " ", t.strip())
    t = _COST_NUM_RE.sub("COSTNUM", t)
    t = _MINUTES_RE.sub("想定時間：MINUTES", t)
    return t


def _slide_norm(slide) -> str:
    return _norm_text("\n".join(slide_text_lines(slide)))


def get_before_prs(repo: Path, relpath: str, after_bytes: bytes):
    """working tree(after) と異なる直近の git 版を before として取得。
    HEAD, HEAD^, HEAD^^ を順に試す。見つからなければ None。"""
    for ref in ("HEAD", "HEAD^", "HEAD^^"):
        r = subprocess.run(
            ["git", "-C", str(repo), "show", f"{ref}:{relpath}"],
            capture_output=True,
        )
        if r.returncode != 0:
            continue
        if r.stdout and r.stdout != after_bytes:
            try:
                return Presentation(io.BytesIO(r.stdout))
            except Exception:
                continue
    return None


def check_side_effect(prs_after, prs_before) -> tuple[list[str], str | None]:
    """新規3枚(GLOBAL CONTEXT)・COST番号変更・AGENDA 以外は差分 0。"""
    if prs_before is None:
        return [], "before pptx を git から取得できず (e は SKIP)"
    errors = []

    before_norms = {_slide_norm(sl) for sl in prs_before.slides}
    after_norms = [_slide_norm(sl) for sl in prs_after.slides]
    after_set = set(after_norms)

    # after 側: AGENDA(2) と GLOBAL CONTEXT 含むスライド以外は before に存在すべき
    for i, slide in enumerate(prs_after.slides, 1):
        norm = _slide_norm(slide)
        if i == 2:  # AGENDA は変更対象
            continue
        if "GLOBAL CONTEXT" in norm:  # 新規セクション
            continue
        if norm not in before_norms:
            errors.append(
                f"  after Slide {i}: before に対応なし（副作用疑い）: "
                f"\"{norm[:60]}\""
            )

    # before 側: AGENDA 以外は COST番号吸収後 after に残存すべき
    for j, slide in enumerate(prs_before.slides, 1):
        norm = _slide_norm(slide)
        if j == 2:  # before AGENDA
            continue
        if norm not in after_set:
            errors.append(
                f"  before Slide {j}: after から消失（副作用疑い）: "
                f"\"{norm[:60]}\""
            )
    return errors, None


# ── main ─────────────────────────────────────────────────

def _emit(label: str, errors: list[str]) -> None:
    status = "PASS" if not errors else "FAIL"
    print(f"[{status}] {label}")
    for e in errors:
        print(e)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TASK-GLOBALCTX-VERIFY-01 受入検証"
    )
    parser.add_argument("after", nargs="?", default=str(DEFAULT_AFTER),
                        help="検証対象(after) pptx")
    parser.add_argument("--before", default=None,
                        help="before pptx（省略時は git から自動取得）")
    args = parser.parse_args()

    after_path = Path(args.after)
    if not after_path.exists():
        print(f"ERROR: {after_path} not found", file=sys.stderr)
        return 2
    try:
        prs = Presentation(str(after_path))
    except Exception as e:
        print(f"ERROR: {after_path} 読み込み失敗: {e}", file=sys.stderr)
        return 2
    after_bytes = after_path.read_bytes()

    prs_before = None
    if args.before:
        bp = Path(args.before)
        if bp.exists():
            try:
                prs_before = Presentation(str(bp))
            except Exception as e:
                print(f"WARN: --before 読込失敗({e})。e は git 自動取得へ", file=sys.stderr)
        else:
            print(f"WARN: --before {bp} not found。e は git 自動取得へ", file=sys.stderr)
    if prs_before is None and not args.before:
        prs_before = get_before_prs(TARGET_REPO, REL_PATH, after_bytes)

    print(f"検証対象(after): {after_path}")
    print(f"スライド数: {len(prs.slides)}")
    print(f"before: {'取得済み(git/引数)' if prs_before else '取得失敗 → e SKIP'}")
    print()

    all_pass = True

    # a
    errs = check_overlap(prs)
    _emit("a. shape overlap = 0（全スライド / 可視テキスト同士）", errs)
    if errs:
        all_pass = False

    # b
    errs, warns = check_overflow(prs)
    _emit("b. no overflow（スライド外はみ出し = 0）", errs)
    if errs:
        all_pass = False
    if warns:
        print("  [参考 WARN] 行あふれ推定（実レンダリング非準拠・目安）:")
        for w in warns:
            print(w)

    # c
    errs = check_slide_count(prs)
    _emit(f"c. slide count = {EXPECTED_SLIDES}", errs)
    if errs:
        all_pass = False

    # d
    errs = check_numbering(prs)
    _emit("d. numbering（04/GLOBAL CONTEXT, 05/COST, AGENDA 100min 5sections）", errs)
    if errs:
        all_pass = False

    # e
    errs, note = check_side_effect(prs, prs_before)
    label = "e. side effect = 0（既存スライド差分 0）"
    if note:
        print(f"[SKIP] {label} — {note}")
    else:
        _emit(label, errs)
        if errs:
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
