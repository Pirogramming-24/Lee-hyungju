# apps/posts/views_api.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from apps.posts.models import NutritionOCRJob
from apps.posts.services.nutrition_async import enqueue_job

@require_POST
def nutrition_ocr_create(request):
    print("[NUTRI-OCR] create called")
    print("[NUTRI-OCR] method:", request.method)
    print("[NUTRI-OCR] FILES keys:", list(request.FILES.keys()))

    f = request.FILES.get("image")
    if not f:
        print("[NUTRI-OCR] no image in FILES")
        return JsonResponse({"ok": False, "error": "image is required"}, status=400)

    print("[NUTRI-OCR] image name:", f.name, "size:", f.size, "content_type:", getattr(f, "content_type", None))

    job = NutritionOCRJob.objects.create(image=f, status="PENDING")
    print("[NUTRI-OCR] job created id:", job.id)

    enqueue_job(job.id)
    print("[NUTRI-OCR] job enqueued id:", job.id)

    return JsonResponse({"ok": True, "job_id": job.id, "status": job.status})

@require_GET
def nutrition_ocr_status(request, job_id: int):
    print("[NUTRI-OCR] status called job_id:", job_id)
    try:
        job = NutritionOCRJob.objects.get(id=job_id)
    except NutritionOCRJob.DoesNotExist:
        print("[NUTRI-OCR] job not found:", job_id)
        return JsonResponse({"ok": False, "error": "not found"}, status=404)

    print("[NUTRI-OCR] job status:", job.status)

    return JsonResponse({
        "ok": True,
        "job_id": job.id,
        "status": job.status,
        "result": job.result,
        "error": job.error,
    })
