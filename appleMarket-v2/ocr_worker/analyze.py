import sys
import json
import re
import cv2
import numpy as np
from paddleocr import PaddleOCR


def to_grams(value, unit):
    """mg -> g 단위 통일"""
    if unit.lower() == 'mg':
        return round(value / 1000, 2)
    return round(value, 2)


def parse_nutrition_text(texts):
    full_text = ' '.join(texts)
    result = {'calorie': None, 'carbohydrate': None, 'protein': None, 'fat': None}

    kcal_match = re.search(r'(\d+(?:\.\d+)?)\s*kcal', full_text, re.IGNORECASE)
    if kcal_match:
        result['calorie'] = float(kcal_match.group(1))

    patterns = {
        'carbohydrate': r'탄수화물\s*(\d+(?:\.\d+)?)\s*(g|mg)',
        'protein': r'단백질\s*(\d+(?:\.\d+)?)\s*(g|mg)',
        'fat': r'지방\s*(\d+(?:\.\d+)?)\s*(g|mg)',
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, full_text)
        if m:
            result[key] = to_grams(float(m.group(1)), m.group(2))

    return result


def preprocess_image(image_path):
    """
    OCR 인식률 향상을 위한 전처리:
    1) 2배 확대 (작은 글씨 인식률 향상)
    2) 그레이스케일 변환
    3) CLAHE로 대비 강화 (조명이 고르지 않은 사진 대응)
    4) 가벼운 노이즈 제거
    처리된 이미지는 다시 3채널(BGR)로 변환해 PaddleOCR에 그대로 전달 가능한 형태로 반환.
    """
    image = cv2.imread(image_path)
    if image is None:
        return None

    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)


def run_ocr(ocr, image_input):
    """image_input: 파일 경로(str) 또는 numpy 배열(전처리된 이미지)"""
    result = ocr.predict(image_input)
    texts = []
    for res in result:
        texts.extend(res['rec_texts'])
    return texts


def count_matched_fields(parsed):
    return sum(1 for v in parsed.values() if v is not None)


def main():
    image_path = sys.argv[1]

    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        lang='korean',
        enable_mkldnn=False,
    )

    # 1차: 원본 이미지로 시도
    original_texts = run_ocr(ocr, image_path)
    original_parsed = parse_nutrition_text(original_texts)

    # 2차: 전처리된 이미지로 시도
    best_texts = original_texts
    best_parsed = original_parsed

    processed = preprocess_image(image_path)
    if processed is not None:
        processed_texts = run_ocr(ocr, processed)
        processed_parsed = parse_nutrition_text(processed_texts)

        # 전처리본이 더 많은 필드를 인식했을 때만 채택 (전처리가 오히려 인식률을 낮추는 경우 방지)
        if count_matched_fields(processed_parsed) > count_matched_fields(best_parsed):
            best_texts = processed_texts
            best_parsed = processed_parsed

    best_parsed['raw_texts'] = best_texts

    print(json.dumps(best_parsed, ensure_ascii=False))


if __name__ == '__main__':
    main()