from transformers import pipeline

# 1) 번역 파이프라인
# _translate_ko_en = pipeline(
#     "translation",
#     model="Helsinki-NLP/opus-mt-ko-en",
# )

# _translate_en_ko = pipeline(
#     "translation",
#     model="facebook/nllb-200-distilled-600M",
#     src_lang="eng_Latn",
#     tgt_lang="kor_Hang",
# )

# 2) 생성 파이프라인 (영어)
_gen = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
)

def run_chat_pipeline(messages):
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = (m.get("content") or "").strip()
            break

    if not last_user:
        return "I didn't get your message."

    prompt = (
        "Answer in English.\n"
        "Write 5-8 sentences.\n"
        "Be factual. If you are unsure, say \"I don't know\".\n"
        f"Question: {last_user}\n"
        "Answer:"
    )

    out = _gen(
        prompt,
        max_new_tokens=180,     # gpt2의 100보다 조금 늘리는게 자연스러움
        min_new_tokens=60,      # 단답 방지 핵심

        do_sample=True,
        temperature=0.4,
        top_p=0.9,

        repetition_penalty=1.15,   # FLAN은 1.2까지 안 줘도 됨(과하면 문장 끊김)
        no_repeat_ngram_size=4,
    )[0]["generated_text"].strip()

    return out or "I couldn't generate a good answer."