from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device


@lru_cache(maxsize=1)
def get_moderator_pipeline():
    return pipeline(
        task="text-classification",
        model="unitary/toxic-bert",
        top_k=None,
        device=get_pipeline_device(),
    )


def run_moderate(text: str) -> dict:
    """
    영어 문장의 유해성을 분석합니다.
    반환값 예시:
    {
        "highest_label": "insult",
        "highest_score": 78.43,
        "all_scores": [
            {"label": "insult", "score": 78.43},
            {"label": "toxic", "score": 66.21},
            ...
        ]
    }
    """
    moderator = get_moderator_pipeline()
    raw_result = moderator(text)[0]

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
        "highest_label": top["label"],
        "highest_score": top["score"],
        "all_scores": all_scores,
    }