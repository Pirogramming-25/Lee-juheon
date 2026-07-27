def clean_nutrition_result(data: dict) -> dict:
    """analyze.py가 반환한 JSON에서 필요한 키만 안전하게 추출"""
    return {
        'calorie': data.get('calorie'),
        'carbohydrate': data.get('carbohydrate'),
        'protein': data.get('protein'),
        'fat': data.get('fat'),
    }