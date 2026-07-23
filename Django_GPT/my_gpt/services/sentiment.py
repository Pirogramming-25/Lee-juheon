from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    return pipeline(
        task="text-classification",
        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
        top_k=None,
        device=get_pipeline_device(),
    )


def run_sentiment(text: str) -> dict:
    """
    입력 문장의 감정을 분석합니다.
    반환값 예시:
    {
        "label": "positive",
        "score": 92.48,
        "all_scores": [
            {"label": "positive", "score": 92.48},
            {"label": "neutral", "score": 5.31},
            {"label": "negative", "score": 2.21},
        ]
    }
    """
    classifier = get_sentiment_pipeline()
    raw_result = classifier(text)[0]

    # top_k=None이면 모든 라벨 점수가 리스트로 나옴
    sorted_scores = sorted(
        raw_result, key=lambda x: x["score"], reverse=True
    )

    all_scores = [
        {
            "label": item["label"],
            "score": round(item["score"] * 100, 2),
        }
        for item in sorted_scores
    ]

    top = all_scores[0]

    return {
        "label": top["label"],
        "score": top["score"],
        "all_scores": all_scores,
    }