import subprocess
import json
import os
from django.conf import settings
from .rules import clean_nutrition_result

CONDA_PYTHON = os.environ.get(
    "APPLEMARKET_AI_PYTHON",
    r"C:\Users\user\miniconda3\envs\applemarket-ocr\python.exe",
)

# ocr_worker/analyze.py 스크립트 경로
ANALYZE_SCRIPT = os.path.join(settings.BASE_DIR, 'ocr_worker', 'analyze.py')


def analyze_nutrition_image(image_path: str) -> dict:
    """
    이미지 파일 경로를 받아 conda 환경에서 analyze.py를 실행하고
    결과 JSON을 파싱해서 반환합니다.
    """
    # 자식 프로세스가 무조건 UTF-8로 출력하도록 강제 (Windows cp949 콘솔 문제 우회)
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'

    result = subprocess.run(
        [CONDA_PYTHON, ANALYZE_SCRIPT, image_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=120,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(f"OCR 스크립트 실행 실패: {result.stderr}")

    stdout = (result.stdout or '').strip()
    if not stdout:
        raise RuntimeError(f"OCR 스크립트가 출력이 없습니다. stderr: {result.stderr}")

    last_line = stdout.splitlines()[-1]
    data = json.loads(last_line)

    return clean_nutrition_result(data)