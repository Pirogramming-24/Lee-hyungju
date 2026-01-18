import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .services import retrieve_context, generate_answer

def chat_page(request):
    return render(request, "chatbot/chat.html")

@require_POST
def chat_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"answer": "질문을 입력해 주세요."}, status=400)

    context = retrieve_context(message, k=6)
    answer = generate_answer(message, context)

    return JsonResponse({"answer": answer})
