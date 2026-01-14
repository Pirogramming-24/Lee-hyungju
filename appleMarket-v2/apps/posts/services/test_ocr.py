# apps/posts/services/test_nutrition_ocr.py
import cv2

from nutrition_ocr.ocr_runner import get_ocr, run_ocr
from nutrition_ocr.preprocess import preprocess_soft
from nutrition_ocr.row_extract import extract_pipeline

def run_one(path, ocr):
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        raise FileNotFoundError(path)

    # 원본(보통 원본이 더 정확)
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    d = run_ocr(rgb, ocr=ocr)
    out, lines = extract_pipeline(d)

    print(f"\n=== {path} (ORIGINAL) ===")
    print(out)
    for ln in lines:
        print("-", ln["text"])

    # 전처리(옵션)
    pre = preprocess_soft(img_bgr)
    pre_rgb = cv2.cvtColor(pre, cv2.COLOR_GRAY2RGB)
    d2 = run_ocr(pre_rgb, ocr=ocr)
    out2, lines2 = extract_pipeline(d2)

    print(f"\n=== {path} (PREPROCESSED) ===")
    print(out2)
    for ln in lines2:
        print("-", ln["text"])

def main():
    ocr = get_ocr(lang="korean", use_textline_orientation=True)

    # 파일명은 본인 환경에 맞게
    run_one("image.png", ocr)
    run_one("image2.png", ocr)

if __name__ == "__main__":
    main()
