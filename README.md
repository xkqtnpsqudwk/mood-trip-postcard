# MoodTrip

개인 여행 성향을 바탕으로 도시 속 장소를 추천하고, 방문 후 이미지를 엽서 형태로 남기는 AI 솔로 여행 큐레이션 프로토타입입니다.

MoodTrip은 여행 일정을 자동으로 짜주는 서비스라기보다, 혼자 여행하는 사용자가 자신의 취향에 맞는 장소를 고르고, 그 순간의 기분과 방문 경험을 엽서 이미지로 마무리할 수 있게 돕는 경험형 웹 서비스입니다.

## 핵심 흐름

1. 사용자가 도시와 현재 기분을 자유문장으로 입력합니다.
2. 로그인 사용자는 마이페이지에 저장한 여행 성향이 추천에 함께 반영됩니다.
3. AI가 현재 감정을 해석하고, 저장된 성향에서 추천에 사용할 선호/회피 태그를 추출합니다.
4. 백엔드는 사전 구축된 서울/파리 장소 데이터 풀에서 성향과 회피 요소에 맞는 장소를 추천합니다.
5. 사용자가 장소를 선택하고 방문 후 느낌을 입력합니다.
6. 사진을 첨부하면 OpenAI 이미지 모델이 사진 기반 콜라주를 생성합니다.
7. 사진이 없으면 사용자가 입력한 느낌을 바탕으로 엽서 앞면 이미지를 생성합니다.
8. 엽서는 앞면 이미지, 뒷면 빈 엽서 양식으로 보관됩니다.
9. 여행을 마무리하면 해당 여정의 엽서 이미지들을 모아 최종 여정 엽서를 생성합니다.

## 주요 기능

- 한국어/영어 UI 전환
- 라이트/다크 모드
- 회원가입, 로그인, 로그아웃
- 사용자 여행 성향 저장
- 감정 입력 기반 AI 분석 및 경험 톤 설정
- 서울/파리 장소 추천
- 지도형 그래픽 위 추천 장소 마커 표시
- 추천 장소 클릭 시 상세 카드 표시
- 방문 후 엽서 생성
- 사진 첨부 시 이미지 콜라주 생성
- 사진 미첨부 시 사용자 입력 기반 이미지 생성
- 여정 단위 최종 엽서 생성
- 엽서 보관함 및 공유 카드 다운로드

## 기술 스택

### Frontend

- React 19
- Vite
- Tailwind CSS 4
- Axios

### Backend

- Python
- FastAPI
- SQLite
- Pydantic
- python-dotenv
- OpenAI Python SDK

### AI 사용 범위

- 텍스트 모델: 기분 분석, 감정 태그 생성, 사용자 성향 추출
- 이미지 모델: 엽서 앞면 이미지 생성, 사진 기반 콜라주 생성, 최종 여정 엽서 이미지 생성

현재 기본 모델명은 `backend/ai_service.py`와 환경변수 기준으로 설정됩니다.

```env
OPENAI_TEXT_MODEL=gpt-5.4
OPENAI_IMAGE_MODEL=gpt-image-1.5
```

모델 접근 권한이 없거나 모델명이 변경된 경우 OpenAI API에서 오류가 발생할 수 있습니다.

## 프로젝트 구조

```text
middle-project/
  backend/
    ai_service.py      # OpenAI 호출 및 AI 처리 로직
    auth.py            # 비밀번호 해시 및 토큰 생성
    database.py        # SQLite 초기화, 시드 데이터, CRUD
    main.py            # FastAPI 엔드포인트
    tags.py            # 추천용 선호/회피 태그 정의
    requirements.txt
  frontend/
    public/
      maps/            # 서울/파리 지도 배경 이미지
    src/
      components/      # 화면 컴포넌트
      api.js           # API 클라이언트
      i18n.js          # KO/EN 문구
      App.jsx
    package.json
  outputs/             # 문서/PPT 산출물, git 제외
  start-dev.bat
  stop-dev.bat
```

## 실행 준비

### 1. 백엔드 환경 구성

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

`backend/.env` 파일을 만들고 OpenAI API 키와 모델명을 설정합니다.

```env
OPENAI_API_KEY=sk-...
OPENAI_TEXT_MODEL=gpt-5.4
OPENAI_IMAGE_MODEL=gpt-image-1.5
```

이미지 생성과 편집 API를 사용하므로, 사용하는 계정에 해당 모델 접근 권한이 필요합니다.

### 2. 프론트엔드 환경 구성

```bash
cd frontend
npm install
```

## 개발 서버 실행

루트 폴더에서 다음 파일을 실행하면 백엔드와 프론트엔드가 각각 새 창으로 실행됩니다.

```bash
start-dev.bat
```

수동 실행이 필요하면 아래처럼 실행할 수 있습니다.

### Backend

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm run dev
```

프론트엔드 주소:

```text
http://127.0.0.1:5173
```

프론트엔드의 `/api/*` 요청은 `frontend/vite.config.js` 설정에 따라 `http://127.0.0.1:8000`으로 프록시됩니다.

## 서버 종료

```bash
stop-dev.bat
```

`8000`, `5173` 포트에서 실행 중인 개발 서버를 종료합니다.

## 주요 API

### Auth

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Preferences

- `GET /api/preferences`
- `PUT /api/preferences`

사용자의 자유문장 성향 프로필을 저장합니다. 추천 시 OpenAI가 이 문장에서 선호 태그와 회피 태그를 추출하고, 장소 추천은 이 성향 태그를 중심으로 계산됩니다.

### Recommendation

- `POST /api/analyze`

요청 예시:

```json
{
  "city": "Seoul",
  "mood_text": "오늘은 좀 신나고 사람 구경도 할 수 있는 곳에 가고 싶어.",
  "language": "ko"
}
```

응답에는 감정 단서, 감정 태그, 회피 태그, 추천 장소 목록이 포함됩니다. 감정 분석은 화면의 톤과 엽서 이미지 분위기를 잡는 데 쓰이고, 추천 순위는 사용자 성향과 장소 태그 매칭을 중심으로 계산됩니다.

### Postcard

- `POST /api/postcard`
- `PATCH /api/postcard/{postcard_id}/next-place`
- `POST /api/trip/{trip_id}/final-postcard`
- `GET /api/archive`

`POST /api/postcard`는 사용자의 방문 후 입력과 첨부 사진을 바탕으로 엽서 앞면 이미지를 생성합니다. 엽서 문구는 AI가 별도로 작성하지 않으며, 뒷면은 빈 엽서 양식으로 표시됩니다.

## 장소 데이터

장소 데이터는 `backend/database.py`의 시드 데이터로 관리합니다.

현재 데이터 풀은 서울과 파리를 중심으로 구성되어 있으며, 다음 유형을 포함합니다.

- 강변 산책로
- 공원
- 역사 장소
- 미술관/전시 공간
- 카페
- 도서관/서점
- 시장/푸드홀
- 신나는 밤거리/거리 상권

추천에 사용하는 주요 선호 태그는 `backend/tags.py`에서 관리합니다.

예시:

- `walking`
- `riverside`
- `photo`
- `quiet`
- `night_view`
- `lively`
- `exhibition`
- `shopping`
- `reading`
- `cafe`
- `history`

## 현재 구현 범위

포함:

- 웹 기반 프로토타입
- 로그인 기반 개인화 성향 저장
- 서울/파리 추천
- 엽서 이미지 생성
- 여정별 최종 엽서 생성
- 보관함
- 공유 카드 다운로드

제외:

- 실제 지도 API 연동
- 길찾기/내비게이션
- 예약/결제
- 실시간 위치 추적 기반 추천
- 외부 SNS API 직접 연동
- 운영 배포 및 관리자 페이지

## 개발 참고

프론트엔드 빌드:

```bash
cd frontend
npm run build
```

백엔드 문법 확인:

```bash
backend\venv\Scripts\python.exe -m py_compile backend\main.py backend\ai_service.py backend\database.py backend\tags.py
```

SQLite 데이터베이스는 서버 시작 시 `database.init_db()`를 통해 초기화 및 시드 반영됩니다.
