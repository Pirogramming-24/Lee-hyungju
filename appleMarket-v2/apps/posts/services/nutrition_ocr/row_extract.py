# apps/posts/services/nutrition_ocr/row_extract.py
import re
from statistics import median

KCAL_RE = re.compile(r'(\d+(?:\.\d+)?)\s*\.?\s*kcal', re.IGNORECASE)
G_RE = re.compile(r'(\d+(?:\.\d+)?)\s*g', re.IGNORECASE)

def _clean(s: str) -> str:
    return s.replace(" ", "").replace(",", "").strip()

def _poly_to_bbox(poly):
    # poly: Nx2 (보통 4x2) numpy array
    pts = poly.tolist()
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

def build_items_from_ocr_dict(d):
    """
    OCRResult dict -> items
    item: {text, conf, cx, cy, h, bbox}
    """
    texts = d.get("rec_texts", [])
    scores = d.get("rec_scores", [])
    polys = d.get("rec_polys", None)

    if polys is None:
        raise ValueError("rec_polys not found in OCRResult dict")

    items = []
    for i, (t, p) in enumerate(zip(texts, polys)):
        text = _clean(str(t))
        if text == "":
            continue
        conf = float(scores[i]) if i < len(scores) else 0.0

        x1, y1, x2, y2 = _poly_to_bbox(p)
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        h = (y2 - y1)

        items.append({
            "text": text,
            "conf": conf,
            "cx": cx,
            "cy": cy,
            "h": h,
            "bbox": (x1, y1, x2, y2),
        })
    return items

def cluster_rows(items, row_tol=None):
    """
    cy 기준으로 행 묶기
    row_tol: None이면 글자 높이 기반 자동 추정
    return: rows (각 row는 item list)
    """
    if not items:
        return []

    items_sorted = sorted(items, key=lambda x: x["cy"])
    heights = [max(1.0, it["h"]) for it in items_sorted]
    med_h = median(heights)

    # 자동 허용치: 너무 작으면 분리되고, 너무 크면 두 행이 합쳐짐
    if row_tol is None:
        row_tol = max(12.0, 0.45 * med_h)

    rows = []
    for it in items_sorted:
        if not rows:
            rows.append([it])
            continue
        last_row = rows[-1]
        last_cy = median([x["cy"] for x in last_row])
        if abs(it["cy"] - last_cy) <= row_tol:
            last_row.append(it)
        else:
            rows.append([it])
    return rows

def rows_to_text(rows):
    """
    각 행: cx 기준 정렬 후 join
    """
    line_infos = []
    for row in rows:
        row_sorted = sorted(row, key=lambda x: x["cx"])
        line = "".join([x["text"] for x in row_sorted])
        line_cy = median([x["cy"] for x in row_sorted])
        line_infos.append({"text": line, "cy": line_cy, "items": row_sorted})
    # 위에서 아래 순
    line_infos.sort(key=lambda x: x["cy"])
    return line_infos

def _extract_g_after_keyword(line, keyword):
    """
    '지방15g28%' 같은 라인에서 keyword 이후 첫 g값 추출
    """
    idx = line.find(keyword)
    if idx < 0:
        return None
    tail = line[idx + len(keyword):]
    m = G_RE.search(tail)
    if m:
        return float(m.group(1))
    return None

def extract_nutrition_from_lines(lines):
    """
    lines: rows_to_text() 결과
    """
    out = {"kcal": None, "carb_g": None, "protein_g": None, "fat_g": None}

    # 1) kcal: '2000kcal'(기준치 문장) 제외 + 위쪽 라인 우선
    kcal_candidates = []
    for ln in lines:
        t = ln["text"]
        m = KCAL_RE.search(t)
        if not m:
            continue
        # 기준치 문장(대개 길고 '2000kcal' 포함) 제외
        if "2000kcal" in t or "2,000kcal" in t:
            continue
        kcal_candidates.append((ln["cy"], float(m.group(1))))

    if kcal_candidates:
        kcal_candidates.sort(key=lambda x: x[0])  # 가장 위
        out["kcal"] = kcal_candidates[0][1]

    # 2) 탄수화물/단백질/지방
    for ln in lines:
        t = ln["text"]

        if out["carb_g"] is None and "탄수화물" in t:
            v = _extract_g_after_keyword(t, "탄수화물")
            if v is not None:
                out["carb_g"] = v

        if out["protein_g"] is None and "단백질" in t:
            v = _extract_g_after_keyword(t, "단백질")
            if v is not None:
                out["protein_g"] = v

        # 지방은 트랜스/포화 제외(표에 같이 있어서 오탐 원인)
        if out["fat_g"] is None and "지방" in t and ("트랜스" not in t) and ("포화" not in t):
            v = _extract_g_after_keyword(t, "지방")
            if v is not None:
                out["fat_g"] = v

    return out

def extract_pipeline(ocr_dict, row_tol=None):
    """
    OCRResult dict -> 최종 추출 + 디버그 라인
    """
    items = build_items_from_ocr_dict(ocr_dict)
    rows = cluster_rows(items, row_tol=row_tol)
    lines = rows_to_text(rows)
    out = extract_nutrition_from_lines(lines)
    return out, lines
