# apps/posts/services/nutrition_ocr/ocr_runner.py
from paddleocr import PaddleOCR

def get_ocr(lang="korean", use_textline_orientation=True):
    # 최신 파이프라인: predict() 사용
    return PaddleOCR(lang=lang, use_textline_orientation=use_textline_orientation)

def ocr_to_dict_first(raw):
    """
    paddlex OCRResult -> dict로 풀기
    raw: ocr.predict(...) 결과(보통 [OCRResult])
    """
    if not isinstance(raw, list) or not raw:
        raise ValueError("Empty OCR raw result")

    first = raw[0]
    try:
        d = dict(first)
    except Exception as e:
        raise ValueError(f"OCRResult dict conversion failed: {e}")
    return d

def run_ocr(image_rgb, ocr=None):
    """
    image_rgb: RGB numpy array
    return: OCRResult dict (rec_texts/rec_scores/rec_polys/rec_boxes 포함)
    """
    if ocr is None:
        ocr = get_ocr()
    raw = ocr.predict(image_rgb)
    return ocr_to_dict_first(raw)
