import sys
import json
import re
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


def main():
    image_path = sys.argv[1]

    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        lang='korean',
        enable_mkldnn=False,
    )

    result = ocr.predict(image_path)

    texts = []
    for res in result:
        texts.extend(res['rec_texts'])

    parsed = parse_nutrition_text(texts)
    parsed['raw_texts'] = texts

    print(json.dumps(parsed, ensure_ascii=False))


if __name__ == '__main__':
    main()