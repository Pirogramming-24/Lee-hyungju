import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Conversation, Message
from .services.huggingface import run_chat_pipeline

@csrf_exempt
@require_POST
def chat(request):
    # 1) JSON 파싱
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid json"}, status=400)

    user_input = (body.get("message") or "").strip()
    conv_id = body.get("conversation_id")  # 있을 수도/없을 수도

    if not user_input:
        return JsonResponse({"error": "empty message"}, status=400)

    # ====== A) 비로그인: 저장 없이 답변만 ======
    if not request.user.is_authenticated:
        # 히스토리 저장 안 하니, 마지막 질문만 넣어서 생성
        messages = [{"role": "user", "content": user_input}]

        try:
            assistant_reply = (run_chat_pipeline(messages) or "").strip()
            if not assistant_reply:
                assistant_reply = "응답을 생성하지 못했습니다."
        except Exception:
            return JsonResponse({"error": "huggingface_failed"}, status=502)

        # 저장 안 함, conversation_id도 굳이 안 줘도 됨
        return JsonResponse({"reply": assistant_reply, "conversation_id": None})

    # ====== B) 로그인: 저장 + 히스토리 기반 생성 ======
    # conv_id가 없거나, 내 대화가 아니면 새로 생성
    conversation = None
    if conv_id:
        conversation = Conversation.objects.filter(id=conv_id, user=request.user).first()

    if conversation is None:
        conversation = Conversation.objects.create(user=request.user)

    # 2) 사용자 메시지 저장 + 히스토리 구성
    with transaction.atomic():
        Message.objects.create(conversation=conversation, role="user", content=user_input)

        messages = list(
            conversation.messages.order_by("created_at").values("role", "content")
        )

    # 3) HF 호출
    try:
        assistant_reply = (run_chat_pipeline(messages) or "").strip()
        if not assistant_reply:
            assistant_reply = "응답을 생성하지 못했습니다."
    except Exception:
        return JsonResponse({"error": "huggingface_failed"}, status=502)

    # 4) 어시스턴트 메시지 저장
    Message.objects.create(
        conversation=conversation, role="assistant", content=assistant_reply
    )

    return JsonResponse({"reply": assistant_reply, "conversation_id": conversation.id})

def main(request):
    if request.user.is_authenticated:
        conv = (
            Conversation.objects.filter(user=request.user)
            .order_by("-created_at")
            .first()
        )
        if conv is None:
            conv = Conversation.objects.create(user=request.user)

        messages = conv.messages.order_by("created_at")
        conversation_id = conv.id
    else:
        # 비로그인: 빈 화면 + 임시 conversation
        messages = []
        conversation_id = None

    return render(
        request,
        "my_gpt/main_chat.html",
        {
            "messages": messages,
            "conversation_id": conversation_id,
        },
    )

def signup(request):
    if request.user.is_authenticated:
        return redirect("main")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 가입 후 바로 로그인
            return redirect("main")
    else:
        form = UserCreationForm()

    return render(request, "my_gpt/signup.html", {"form": form})