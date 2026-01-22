from functools import lru_cache
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# M2M100 언어 코드
KO = "ko"
EN = "en"

def _device():
    return torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

@lru_cache(maxsize=1)
def get_m2m():
    """
    facebook/m2m100_418M
    - 한<->영 번역 지원
    - NLLB 금지 대체용
    """
    model_name = "facebook/m2m100_418M"
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.to(_device())
    model.eval()
    return tok, model

@lru_cache(maxsize=1)
def get_summarizer():
    # 영어 요약 전용(안정적)
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=0 if torch.cuda.is_available() else -1,
    )

def _translate(text: str, src_lang: str, tgt_lang: str, max_new_tokens: int = 256) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    tok, model = get_m2m()

    # source language 지정
    tok.src_lang = src_lang

    inputs = tok(text, return_tensors="pt", truncation=True).to(_device())

    # target language 강제
    forced_bos_token_id = tok.get_lang_id(tgt_lang)

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_new_tokens=max_new_tokens,
            num_beams=4,          # 번역은 빔서치가 안정적
            do_sample=False,      # 번역은 샘플링 끄는 게 정답
        )

    out = tok.batch_decode(generated, skip_special_tokens=True)[0].strip()
    return out

def translate_ko_en(text: str) -> str:
    return _translate(text, src_lang=KO, tgt_lang=EN)

def translate_en_ko(text: str) -> str:
    return _translate(text, src_lang=EN, tgt_lang=KO)

def summarize_en(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    sm = get_summarizer()
    out = sm(
        text,
        max_length=120,
        min_length=40,
        do_sample=False,
    )
    return (out[0].get("summary_text") or "").strip()
