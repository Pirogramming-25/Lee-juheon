# 🍎 Piro25-AppleMarket-v2

피로그래밍 25기 5주차 컴퓨터 비전 세션 과제를 위한 스켈레톤 코드입니다.

피로그래밍 25기 5주차 목요일 과제: 중고거래 마켓플레이스 웹 애플리케이션 사과마켓 v2

## 📚 과제 목표
- 컴퓨터 비전을 활용한 웹 서비스 실습

## 🛠 기술 스택
- **Backend**: Django 5.2.4
- **Database**: SQLite3
- **Frontend**: Bootstrap 5.3.0
- **언어**: Python 3.11+

## AI 기능 실행 환경 (OCR / 해시태깅)
PaddleOCR·YOLO11은 별도 conda 환경(Python 3.10)이 필요합니다.
conda 환경의 python 경로가 다르다면 환경변수로 지정해주세요.

\`\`\`bash
conda create --name applemarket-ocr python=3.10
conda activate applemarket-ocr
pip install paddleocr paddlepaddle ultralytics opencv-python

# 경로가 다르면
export APPLEMARKET_AI_PYTHON="/path/to/envs/applemarket-ocr/python.exe"
\`\`\`