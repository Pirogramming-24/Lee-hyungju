from functools import lru_cache
from transformers import pipeline
import torch

# NLLB 언어 코드
KO = "kor_Hang"
EN = "eng_Latn"

def _device():
    return 0 if torch.cuda.is_available() else -1

@lru_cache(maxsize=1)
def get_translator():
    # NLLB: 한<->영 둘 다 가능
    return pipeline(
        "translation",
        model="facebook/nllb-200-distilled-600M",
        device=_device(),
        max_length=400
    )

@lru_cache(maxsize=1)
def get_summarizer():
    # BART 요약(영어 요약에 강함)
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=_device(),
    )

def translate_ko_en(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    tr = get_translator()
    out = tr(text, src_lang=KO, tgt_lang=EN, max_length=256)
    return (out[0].get("translation_text") or "").strip()

def translate_en_ko(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    tr = get_translator()
    out = tr(text, src_lang=EN, tgt_lang=KO, max_length=256)
    return (out[0].get("translation_text") or "").strip()

def summarize_en(text: str) -> str:
    """
    bart-large-cnn은 영어 요약에 최적.
    한국어 입력이 오면, '한->영 번역 후 요약'으로 처리하는 게 안전함.
    """
    text = (text or "").strip()
    if not text:
        return ""

    sm = get_summarizer()
    out = sm(
        text,
        max_length=120,
        min_length=40,
        do_sample=False,  # 요약은 샘플링 끄는 게 더 안정적
    )
    return (out[0].get("summary_text") or "").strip()
