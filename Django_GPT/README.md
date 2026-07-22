# 🤖 Django GPT — Hugging Face AI 웹 서비스

Django 웹 서비스 위에서 Hugging Face `pipeline()`을 이용해
감정 분석, 문서 요약, 유해 표현 분석, 복합 분석(챌린지)을 제공합니다.

## 기술 스택

- Django 5.2
- Hugging Face Transformers (`pipeline()`)
- SQLite
- Vanilla JavaScript (fetch API)

## 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# source venv/bin/activate      # macOS / Linux

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 DJANGO_SECRET_KEY 값을 채워주세요

# 4. DB 마이그레이션
python manage.py migrate

# 5. 관리자 계정 생성 (로그인 기능 확인을 위해 필수)
python manage.py createsuperuser

# 6. 서버 실행
python manage.py runserver

> 별도의 회원가입 기능은 없으며, `createsuperuser`로 생성한 계정으로 로그인하여
> `/summarize/`, `/moderate/`, `/combo/` 등 로그인 필요 기능을 확인할 수 있습니다.
```

브라우저에서 `http://127.0.0.1:8000/sentiment/` 로 접속합니다.

## 환경변수 (.env)

| 변수명 | 설명 |
|---|---|
| `DJANGO_SECRET_KEY` | Django 시크릿 키 (settings.py 최초 생성 값 사용 가능) |
| `DEBUG` | 개발 모드 여부 (`True`/`False`) |

`.env` 파일은 Git에 포함하지 않으며, `.env.example`만 포함합니다.
본 프로젝트에서 사용하는 모든 Hugging Face 모델은 Public 모델이므로
별도의 Hugging Face Token은 필요하지 않습니다.

## 사용 모델

### 1. 감정 분석 (`/sentiment/`) — 비로그인 허용

- **Model ID**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Task**: `text-classification`
- **입력 언어**: 영어
- **출력 레이블**: `positive` / `neutral` / `negative`
- **라이선스**: CC-BY-4.0

#### 입력 예시
```
I absolutely love this product! It exceeded all my expectations and works perfectly.
```

#### 출력 예시
```
감정: positive
신뢰도: 99.06%
```

#### 실행 화면
[스크린샷 첨부]

---

### 2. 문서 요약 (`/summarize/`) — 로그인 필요

- **Model ID**: `sshleifer/distilbart-cnn-6-6`
- **Task**: `summarization`
- **입력 언어**: 영어
- **출력**: 원문 길이, 요약문 길이, 요약 비율, 요약문
- **라이선스**: Apache-2.0

#### 입력 예시
```
Artificial intelligence has rapidly transformed various industries over the past decade...
```

#### 출력 예시
```
원문 길이: 788자
요약문 길이: 340자
요약 비율: 43.15%
요약 결과: AI-powered systems are being used to analyze massive amounts of data...
```

#### 실행 화면
[스크린샷 첨부]

---

### 3. 유해 표현 분석 (`/moderate/`) — 로그인 필요

- **Model ID**: `unitary/toxic-bert`
- **Task**: `text-classification` (multi-label)
- **입력 언어**: 영어
- **출력 레이블**: `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`
- **라이선스**: Apache-2.0

#### 입력 예시
```
You are so stupid, I can't believe how useless you are at everything.
```

#### 출력 예시
```
최고 위험 레이블: toxic
위험 점수: 98.54%
```

#### 실행 화면
[스크린샷 첨부]

---

## 🔴 챌린지 과제 — 복합 AI 분석 (`/combo/`)

**주제**: AI 고객 피드백 분석 리포트

원문 → 요약 → (요약문 기준) 감정 분석 → (요약문 기준) 유해 표현 분석 순서로
3개 모델을 체이닝하여 하나의 분석 리포트를 생성합니다.

- 입력: 영어 고객 리뷰/피드백 (200자 ~ 5,000자)
- 재생성 버튼: 동일한 원문으로 파이프라인을 다시 실행 (요약 단계에서
  `do_sample=True`, `num_beams=1` 옵션을 사용하여 실행할 때마다 다른 요약 결과 생성)

#### 실행 화면
[스크린샷 첨부: 복합 분석 결과]
[스크린샷 첨부: 재생성 결과]

---

## URL 및 접근 권한

| URL | 기능 | 접근 권한 |
|---|---|---|
| `/sentiment/` | 감정 분석 | 비로그인 허용 |
| `/summarize/` | 문서 요약 | 로그인 필요 |
| `/moderate/` | 유해 표현 분석 | 로그인 필요 |
| `/combo/` | 복합 분석 (챌린지) | 로그인 필요 |

비로그인 사용자가 로그인 필요 페이지에 접근 시
`/accounts/login/?next=원래경로&required=1` 로 리다이렉트되며,
로그인 페이지에서 "로그인 후 이용해주세요" alert이 표시됩니다.
로그인 성공 시 원래 접근하려던 페이지로 자동 복귀합니다.

## 실행 기록 관리

- 로그인 사용자의 모델 실행 결과는 `InferenceHistory` 모델에 저장됩니다.
- 각 기능 페이지에는 본인의 최근 실행 기록 5개만 표시됩니다.
- 비로그인 사용자의 감정 분석 기록은 DB에 저장되지 않고,
  브라우저 화면(JS 메모리)에서만 유지되며 새로고침 시 초기화됩니다.

## 보안

- 모든 POST 요청은 CSRF 보호가 적용되어 있으며 `@csrf_exempt`를 사용하지 않습니다.
- 모델 실행 실패 시 사용자에게는 일반화된 오류 메시지만 노출되며,
  실제 오류 내용은 서버 로그(`logger.exception`)에만 기록됩니다.
- Hugging Face Token은 코드에 직접 작성하지 않으며, 필요 시 `.env`를 통해 관리합니다.