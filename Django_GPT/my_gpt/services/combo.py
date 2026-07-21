from .sentiment import run_sentiment
from .summarizer import run_summarize
from .moderator import run_moderate


def run_combo(text: str, do_sample: bool = False) -> dict:
    """
    복합 분석 파이프라인:
    원문 → 요약 → (요약문 기준) 감정분석 + 유해표현분석 → 종합 판정

    반환값 예시:
    {
        "summary": "...",
        "sentiment": {"label": "negative", "score": 71.32},
        "toxicity": {
            "highest_label": "insult",
            "highest_score": 12.21,
            "all_scores": [...]
        },
        "verdict": "이 피드백은 ..."
    }
    """
    summary_result = run_summarize(text, do_sample=do_sample)
    summary_text = summary_result["summary"]

    sentiment_result = run_sentiment(summary_text)
    toxicity_result = run_moderate(summary_text)

    verdict = _build_verdict(sentiment_result, toxicity_result)

    return {
        "summary": summary_text,
        "sentiment": {
            "label": sentiment_result["label"],
            "score": sentiment_result["score"],
        },
        "toxicity": toxicity_result,
        "verdict": verdict,
    }


def _build_verdict(sentiment_result: dict, toxicity_result: dict) -> str:
    if sentiment_result["label"] == "negative":
        sentiment_desc = "부정적인 평가를 포함합니다."
    else:
        sentiment_desc = "강한 부정적 평가는 확인되지 않았습니다."

    # unitary/toxic-bert 점수는 0~100 스케일(퍼센트)이므로 50을 기준으로 판단
    if toxicity_result["highest_score"] >= 50:
        toxicity_desc = "유해 표현 가능성이 높습니다."
    else:
        toxicity_desc = "심각한 유해 표현 가능성은 낮습니다."

    return f"이 피드백은 {sentiment_desc} 또한 {toxicity_desc}"