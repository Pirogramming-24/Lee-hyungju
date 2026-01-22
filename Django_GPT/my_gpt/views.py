import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from urllib.parse import urlencode

from .models import Conversation, Message
from .services.huggingface import run_chat_pipeline
from .services.nlp import translate_ko_en, translate_en_ko, summarize_en

def _need_login_redirect(request):
    login_url = reverse("login")
    q = urlencode({
        "next": request.get_full_path(),
        "need_login": "1",
    })
    return redirect(f"{login_url}?{q}")

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


def translate_page(request):
    if not request.user.is_authenticated:
        return _need_login_redirect(request)
    return render(request, "my_gpt/translate.html")

@csrf_exempt
@require_POST
def api_translate(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    text = (body.get("text") or "").strip()
    direction = (body.get("direction") or "ko_en").strip()  # "ko_en" | "en_ko"

    if not text:
        return JsonResponse({"error": "empty text"}, status=400)

    if direction == "en_ko":
        out = translate_en_ko(text)
    else:
        out = translate_ko_en(text)

    return JsonResponse({"result": out})


def summarize_page(request):
    if not request.user.is_authenticated:
        return _need_login_redirect(request)
    return render(request, "my_gpt/summarize.html")

@csrf_exempt
@require_POST
def api_summarize(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    text = (body.get("text") or "").strip()
    output_lang = (body.get("output_lang") or "en").strip()  # "en" | "ko"

    if not text:
        return JsonResponse({"error": "empty text"}, status=400)

    # 1) 입력이 한국어든 영어든, 일단 영어로 맞춰서 요약
    en_text = translate_ko_en(text)
    if not en_text:
        # 입력이 이미 영어라서 번역 결과가 빈값일 가능성 대비(드물지만)
        en_text = text

    summary_en = summarize_en(en_text)

    # 2) 출력 언어 토글
    if output_lang == "ko":
        result = translate_en_ko(summary_en)
    else:
        result = summary_en

    return JsonResponse({"result": result})


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