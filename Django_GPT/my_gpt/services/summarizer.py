from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device


@lru_cache(maxsize=1)
def get_summarizer_pipeline():
    return pipeline(
        task="summarization",
        model="sshleifer/distilbart-cnn-6-6",
        device=get_pipeline_device(),
    )


def run_summarize(text: str, do_sample: bool = False) -> dict:
    """
    긴 영어 문서를 요약합니다.
    """
    summarizer = get_summarizer_pipeline()

    kwargs = {
        "max_length": 180,
        "min_length": 40,
    }

    if do_sample:
        # beam search(num_beams)를 끄고 순수 샘플링만 사용해야
        # 매번 다른 결과가 나옵니다.
        kwargs.update(
            {
                "do_sample": True,
                "num_beams": 1,
                "top_p": 0.9,
                "top_k": 50,
                "temperature": 1.0,
            }
        )
    else:
        kwargs.update(
            {
                "do_sample": False,
                "num_beams": 4,
            }
        )

    result = summarizer(text, truncation=True, **kwargs)[0]
    summary_text = result["summary_text"].strip()

    original_length = len(text)
    summary_length = len(summary_text)
    summary_ratio = round(
        (summary_length / original_length) * 100, 2
    )

    return {
        "original_length": original_length,
        "summary_length": summary_length,
        "summary_ratio": summary_ratio,
        "summary": summary_text,
    }