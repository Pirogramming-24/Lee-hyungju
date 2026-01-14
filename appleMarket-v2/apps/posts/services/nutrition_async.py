# posts/services/nutrition_async.py
import cv2
from threading import Thread

from apps.posts.models import NutritionOCRJob
from apps.posts.services.nutrition_ocr.ocr_runner import get_ocr, run_ocr
from apps.posts.services.nutrition_ocr.row_extract import extract_pipeline

_OCR = None
def _get_ocr():
    global _OCR
    if _OCR is None:
        _OCR = get_ocr(lang="korean", use_textline_orientation=True)
    return _OCR

def _worker(job_id: int):
    job = NutritionOCRJob.objects.get(id=job_id)
    job.status = "RUNNING"
    job.save(update_fields=["status"])

    try:
        img = cv2.imread(job.image.path)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        d = run_ocr(rgb, ocr=_get_ocr())
        out, _ = extract_pipeline(d)

        job.status = "SUCCESS"
        job.result = out
        job.error = None
        job.save(update_fields=["status", "result", "error"])

    except Exception as e:
        job.status = "FAIL"
        job.error = str(e)
        job.save(update_fields=["status", "error"])

def enqueue_job(job_id: int):
    Thread(target=_worker, args=(job_id,), daemon=True).start()
