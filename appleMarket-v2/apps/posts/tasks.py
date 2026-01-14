import cv2
import numpy as np
from celery import shared_task
from django.db import transaction

from .models import NutritionOCRJob

from .services.nutrition_ocr.ocr_runner import get_ocr, run_ocr
from .services.nutrition_ocr.preprocess import preprocess_soft
from .services.nutrition_ocr.row_extract import extract_pipeline

# 프로세스당 1번 로딩(속도/채점 유리)
_OCR = None

def _get_singleton_ocr():
    global _OCR
    if _OCR is None:
        _OCR = get_ocr(lang="korean", use_textline_orientation=True)
    return _OCR

@shared_task(bind=True)
def run_nutrition_ocr(self, job_id: int):
    job = NutritionOCRJob.objects.get(id=job_id)

    with transaction.atomic():
        job.status = NutritionOCRJob.STATUS_RUNNING
        job.save(update_fields=["status", "updated_at"])

    try:
        # 이미지 로드
        img_path = job.image.path
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            raise ValueError("invalid image")

        # 원본 OCR 권장(전처리는 옵션)
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        ocr = _get_singleton_ocr()
        d = run_ocr(rgb, ocr=ocr)
        out, _lines = extract_pipeline(d)

        # 결과가 비어있으면 전처리 한번 더 시도(보험)
        if any(out[k] is None for k in ["kcal", "carb_g", "protein_g", "fat_g"]):
            pre = preprocess_soft(img_bgr)
            pre_rgb = cv2.cvtColor(pre, cv2.COLOR_GRAY2RGB)
            d2 = run_ocr(pre_rgb, ocr=ocr)
            out2, _ = extract_pipeline(d2)
            # 더 좋은 쪽 선택
            score1 = sum(v is not None for v in out.values())
            score2 = sum(v is not None for v in out2.values())
            out = out2 if score2 >= score1 else out

        with transaction.atomic():
            job.status = NutritionOCRJob.STATUS_SUCCESS
            job.result = out
            job.error = None
            job.save(update_fields=["status", "result", "error", "updated_at"])

    except Exception as e:
        with transaction.atomic():
            job.status = NutritionOCRJob.STATUS_FAIL
            job.error = str(e)
            job.save(update_fields=["status", "error", "updated_at"])
        raise
