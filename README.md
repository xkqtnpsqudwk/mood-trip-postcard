# MoodTrip

개인 여행 성향을 바탕으로 도시 속 장소를 한 번에 한 곳 추천하고, 방문 후 남긴 순간들을 여행 엽서로 마무리하는 AI 솔로 여행 큐레이션 프로토타입입니다.

MoodTrip은 여행 일정을 자동으로 짜주는 서비스라기보다, 혼자 여행하는 사용자가 자신의 성향에 맞는 다음 한 걸음을 선택하고, 방문한 순간을 기록한 뒤 여행을 마칠 때 하나의 엽서로 정리할 수 있게 돕는 경험형 웹 서비스입니다.

## 핵심 흐름

1. 사용자가 로그인합니다.
2. 마이페이지에 자신의 여행 성향을 자유문장으로 입력합니다.
3. 도시와 현재 기분을 입력합니다.
4. AI가 현재 감정을 해석하고, 저장된 성향을 바탕으로 추천 기준을 잡습니다.
5. OpenAI 웹 검색 기반 추천이 현재 도시 안에서 실제 방문 가능한 장소 1곳을 제안합니다.
6. 사용자는 추천 장소를 방문하거나, 방문하지 않고 새로운 감정으로 다시 추천받거나, 언제든 여행을 마무리할 수 있습니다.
7. 방문했다면 후기를 입력하고 선택적으로 사진을 첨부합니다.
8. 사진을 첨부하면 OpenAI 이미지 모델이 장소별 순간 콜라주를 생성합니다.
9. 사진이 없으면 사용자가 입력한 후기를 바탕으로 장소별 순간 이미지를 생성합니다.
10. 장소별 결과물은 엽서가 아니라 `기록`으로 저장됩니다.
11. 여행을 마무리하면 저장된 기록 이미지를 모아 최종 `여행 엽서`를 생성하고 보관합니다.

## 주요 기능

- 한국어/영어 UI 전환
- 라이트/다크 모드
- 회원가입, 로그인, 로그아웃
- 사용자 여행 성향 저장
- 감정 입력 기반 AI 분석 및 경험 톤 설정
- 성향 중심 서울/파리 장소 1곳 추천
- 지도형 그래픽 위 추천 장소 마커 표시
- 추천 장소 클릭 시 상세 카드 표시
- 방문 후 순간 기록 생성
- 사진 첨부 시 기록 이미지 콜라주 생성
- 사진 미첨부 시 사용자 입력 기반 이미지 생성
- 여정 단위 최종 엽서 생성
- 기록/엽서 분리 보관함 및 공유 카드 다운로드

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

- 텍스트 모델: 기분 분석, 사용자 성향 해석, 실제 장소 1곳 추천
- 이미지 모델: 장소별 순간 이미지 생성, 사진 기반 콜라주 생성, 최종 여정 엽서 이미지 생성

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
    database.py        # SQLite 초기화 및 CRUD
    main.py            # FastAPI 엔드포인트
    tags.py            # 시간/태그 라벨 정의
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

사용자의 자유문장 성향 프로필을 저장합니다. 추천 시 OpenAI가 이 문장을 함께 읽고, 장소 선택은 현재 감정보다 사용자의 성향과 여행 스타일을 중심으로 판단합니다.

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

응답에는 감정 단서와 추천 장소 1곳이 포함됩니다. 감정 분석은 화면의 톤과 기록/엽서 이미지 분위기를 잡는 데 쓰이고, 장소 선택은 사용자 성향과 장소의 분위기, 강도, 혼자 방문하기 좋은 정도를 중심으로 판단합니다.

### Records / Postcards

- `POST /api/postcard`
- `PATCH /api/postcard/{postcard_id}/next-place`
- `POST /api/trip/{trip_id}/final-postcard`
- `GET /api/archive`

`POST /api/postcard`는 호환성을 위해 기존 경로를 유지하지만, 현재 역할은 장소별 `기록` 생성입니다. 사용자의 방문 후 입력과 첨부 사진을 바탕으로 순간 이미지 또는 콜라주를 만들고 `artifact_type=record`로 저장합니다.

`POST /api/trip/{trip_id}/final-postcard`는 저장된 기록을 모아 `artifact_type=postcard`인 최종 여행 엽서를 생성합니다. 엽서 문구는 AI가 별도로 작성하지 않으며, 뒷면은 빈 엽서 양식으로 표시됩니다.

## 장소 추천

장소 추천은 고정 DB에서 고르는 방식이 아니라 OpenAI 웹 검색 기반으로 현재 운영 여부를 확인한 장소를 제안하는 방식입니다. 현재 UI는 서울과 파리를 대상으로 지도 배경을 제공하고, 추천 장소의 대략적인 위치를 마커로 표시합니다.

추천은 한 번에 1곳만 보여줍니다. 사용자는 방문하지 않고 새로운 감정으로 다시 추천받을 수 있고, 방문했다면 기록을 저장한 뒤 다음 감정으로 이어가거나 여행을 마무리할 수 있습니다.

추천에 사용하는 시간 라벨과 태그 라벨은 `backend/tags.py`에서 관리합니다.

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
- 서울/파리 단일 장소 추천
- 장소별 순간 기록 이미지 생성
- 여정별 최종 엽서 생성
- 기록/엽서 보관함
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

SQLite 데이터베이스는 서버 시작 시 `database.init_db()`를 통해 필요한 테이블과 컬럼을 초기화합니다.
