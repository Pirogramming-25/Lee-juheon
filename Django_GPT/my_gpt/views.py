import json
import logging

from django.http import JsonResponse
from django.shortcuts import render

from .decorators import model_login_required
from .models import InferenceHistory
from .services.combo import run_combo
from .services.moderator import run_moderate
from .services.sentiment import run_sentiment
from .services.summarizer import run_summarize

logger = logging.getLogger(__name__)


SENTIMENT_MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"
SUMMARIZE_MODEL_ID = "sshleifer/distilbart-cnn-6-6"
MODERATE_MODEL_ID = "unitary/toxic-bert"


SENTIMENT_MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"


def sentiment_page(request):
    histories = []
    if request.user.is_authenticated:
        histories = InferenceHistory.objects.filter(
            user=request.user,
            task=InferenceHistory.Task.SENTIMENT,
        ).order_by("-created_at")[:5]

    return render(
        request,
        "my_gpt/sentiment.html",
        {
            "model_id": SENTIMENT_MODEL_ID,
            "histories": histories,
        },
    )


def sentiment_run(request):
    if request.method != "POST":
        return JsonResponse({"error": "허용되지 않은 요청입니다."}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = body.get("text", "")

    if not isinstance(text, str):
        return JsonResponse({"error": "텍스트 형식이 올바르지 않습니다."}, status=400)

    stripped = text.strip()

    if stripped == "":
        return JsonResponse({"error": "분석할 문장을 입력해주세요."}, status=400)

    if len(stripped) > 1000:
        return JsonResponse(
            {"error": "문장은 1,000자 이하로 입력해주세요."}, status=400
        )

    try:
        result = run_sentiment(stripped)
    except Exception:
        logger.exception("Sentiment inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    if request.user.is_authenticated:
        InferenceHistory.objects.create(
            user=request.user,
            task=InferenceHistory.Task.SENTIMENT,
            input_text=stripped,
            output_text=result["label"],
            result_data=result,
        )

    return JsonResponse({"success": True, "data": result})

# ---------------- 문서 요약 ----------------

@model_login_required
def summarize_page(request):
    histories = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.SUMMARIZE,
    ).order_by("-created_at")[:5]

    return render(
        request,
        "my_gpt/summarize.html",
        {
            "model_id": SUMMARIZE_MODEL_ID,
            "histories": histories,
        },
    )


@model_login_required
def summarize_run(request):
    if request.method != "POST":
        return JsonResponse({"error": "허용되지 않은 요청입니다."}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = body.get("text", "")

    if not isinstance(text, str):
        return JsonResponse({"error": "텍스트 형식이 올바르지 않습니다."}, status=400)

    stripped = text.strip()

    if len(stripped) < 100:
        return JsonResponse(
            {"error": "요약할 문서는 100자 이상 입력해주세요."}, status=400
        )

    if len(stripped) > 5000:
        return JsonResponse(
            {"error": "문서는 5,000자 이하로 입력해주세요."}, status=400
        )

    try:
        result = run_summarize(stripped)
    except Exception:
        logger.exception("Summarize inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.SUMMARIZE,
        input_text=stripped,
        output_text=result["summary"],
        result_data=result,
    )

    return JsonResponse({"success": True, "data": result})


# ---------------- 유해 표현 분석 ----------------

@model_login_required
def moderate_page(request):
    histories = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.MODERATE,
    ).order_by("-created_at")[:5]

    return render(
        request,
        "my_gpt/moderate.html",
        {
            "model_id": MODERATE_MODEL_ID,
            "histories": histories,
        },
    )


@model_login_required
def moderate_run(request):
    if request.method != "POST":
        return JsonResponse({"error": "허용되지 않은 요청입니다."}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = body.get("text", "")

    if not isinstance(text, str):
        return JsonResponse({"error": "텍스트 형식이 올바르지 않습니다."}, status=400)

    stripped = text.strip()

    if stripped == "":
        return JsonResponse({"error": "분석할 문장을 입력해주세요."}, status=400)

    if len(stripped) > 1000:
        return JsonResponse(
            {"error": "문장은 1,000자 이하로 입력해주세요."}, status=400
        )

    try:
        result = run_moderate(stripped)
    except Exception:
        logger.exception("Moderate inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.MODERATE,
        input_text=stripped,
        output_text=result["highest_label"],
        result_data=result,
    )

    return JsonResponse({"success": True, "data": result})


# ---------------- 복합 분석 ----------------

@model_login_required
def combo_page(request):
    histories = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.COMBO,
    ).order_by("-created_at")[:5]

    return render(
        request,
        "my_gpt/combo.html",
        {
            "histories": histories,
        },
    )


@model_login_required
def combo_run(request):
    if request.method != "POST":
        return JsonResponse({"error": "허용되지 않은 요청입니다."}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = body.get("text", "")
    regenerate = body.get("regenerate", False)

    if not isinstance(regenerate, bool):
        regenerate = False

    if not isinstance(text, str):
        return JsonResponse({"error": "텍스트 형식이 올바르지 않습니다."}, status=400)

    stripped = text.strip()

    if len(stripped) < 200:
        return JsonResponse(
            {"error": "복합 분석 입력은 200자 이상이어야 합니다."}, status=400
        )

    if len(stripped) > 5000:
        return JsonResponse(
            {"error": "문서는 5,000자 이하로 입력해주세요."}, status=400
        )

    try:
        result = run_combo(stripped, do_sample=bool(regenerate))
    except Exception:
        logger.exception("Combo inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.COMBO,
        input_text=stripped,
        output_text=result["summary"],
        result_data=result,
    )

    return JsonResponse({"success": True, "data": result, "original_text": stripped})