from transformers import pipeline
from .nlp import translate_ko_en, translate_en_ko


# 2) 생성 파이프라인 (영어)
_gen = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
)

def _run_en_chat(en_question: str) -> str:
    en_question = (en_question or "").strip()
    if not en_question:
        return "I didn't get your message."

    prompt = (
        "Answer in English.\n"
        "Write 4-8 sentences.\n"
        "Be factual. If unsure, say you don't know.\n"
        f"Question: {en_question}\n"
        "Answer:"
    )

    result = _gen(
        prompt,
        max_new_tokens=180,     # gpt2의 100보다 조금 늘리는게 자연스러움
        min_new_tokens=60,      # 단답 방지 핵심

        do_sample=True,
        temperature=0.4,
        top_p=0.9,

        repetition_penalty=1.15,   # FLAN은 1.2까지 안 줘도 됨(과하면 문장 끊김)
        no_repeat_ngram_size=4,
    )

    out = (result[0].get("generated_text") or "").strip()
    return out or "I couldn't generate a good answer."

def run_chat_pipeline(messages):
    # 마지막 user만 사용 (기존 유지)
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = (m.get("content") or "").strip()
            break

    if not last_user:
        return "메시지를 이해하지 못했습니다."

    # 1) 한글 -> 영어
    en_q = translate_ko_en(last_user)
    if not en_q:
        en_q = last_user  # 혹시 번역이 실패하면 그대로

    # 2) 영어로 답 생성
    en_a = _run_en_chat(en_q)

    # 3) 영어 -> 한글
    ko_a = translate_en_ko(en_a)
    if not ko_a:
        ko_a = "답변 생성은 됐는데 번역이 실패했습니다."

    return ko_a