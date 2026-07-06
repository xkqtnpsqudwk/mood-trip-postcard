# MoodTrip

MoodTrip은 혼자 여행하는 사용자가 현재 기분과 자신의 성향을 바탕으로 도시 속 한 장소를 추천받고, 그 장소에서의 대화와 감상을 기록한 뒤 여행을 마무리하며 최종 엽서로 남기는 AI 기반 솔로 여행 큐레이션 프로토타입입니다.

서비스는 일정을 자동으로 짜주는 플래너가 아니라, 혼자 여행 중 감정을 받아주고 다음 경험으로 이어주는 동행자에 가깝습니다. 장소 추천은 여행을 시작하게 만드는 계기이고, 대화와 기록은 그 순간을 개인적인 기억으로 남기는 과정입니다.

## 핵심 흐름

1. 사용자가 로그인합니다.
2. 마이페이지에서 자신의 여행 성향을 자유문장으로 저장합니다.
3. 도시와 현재 기분을 입력합니다.
4. AI가 저장된 성향을 중심으로, 현재 기분은 톤과 강도 조절에 활용해 실제 장소 1곳을 추천합니다.
5. 추천 장소는 도시 전역 미니맵 이미지 위에 대략적인 마커로 표시됩니다.
6. 사용자는 추천 장소를 중심으로 MoodTrip과 친구처럼 대화합니다.
7. 장소를 방문했거나, 방문하지 않더라도 충분히 생각이 정리되면 순간 기록을 작성합니다.
8. 사진을 첨부하면 AI가 여행 콜라주 이미지를 만들고, 사진이 없으면 입력한 내용을 바탕으로 이미지를 생성합니다.
9. 장소별 결과물은 엽서가 아니라 `기록`으로 저장됩니다.
10. 여행을 마무리하면 저장된 기록 이미지들을 모아 최종 `여행 엽서`를 생성합니다.

## 주요 기능

- 한국어 전용 UI
- 라이트/다크 모드
- 회원가입, 로그인, 로그아웃
- 로그인 후 진행 중이던 흐름 복원
- 사용자 성향 저장
- 감정 입력 기반 AI 추천
- OpenAI web_search 기반 실제 장소 추천
- 한 번에 1개 장소 추천
- 같은 여행 안의 중복 장소 추천 방지
- 추천 장소와 이어지는 동행 대화
- 도시 전역 미니맵 기반 대략 위치 마커
- 장소별 순간 기록 생성
- 사진 첨부 시 콜라주 생성
- 사진 미첨부 시 입력 문구 기반 이미지 생성
- 기록과 최종 엽서 분리 보관
- 최종 여행 엽서 이미지 저장 및 공유 보조

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

- 텍스트 모델: 성향/감정 해석, 실제 장소 추천, 장소 동행 대화, 최종 엽서 감정 단서 생성
- 이미지 모델: 장소별 기록 이미지 생성, 사진 기반 콜라주, 최종 여행 엽서 생성

기본 모델명은 환경변수로 설정합니다.

```env
OPENAI_TEXT_MODEL=gpt-5.4
OPENAI_IMAGE_MODEL=gpt-image-1.5
```

## 프로젝트 구조

```text
middle-project/
  backend/
    ai_service.py      # OpenAI 호출 및 AI 처리 로직
    auth.py            # 비밀번호 해시 및 토큰 생성
    database.py        # SQLite 초기화 및 CRUD
    main.py            # FastAPI 엔드포인트
    tags.py            # 시간 라벨 정의
    requirements.txt
  frontend/
    public/
      maps/            # 서울/파리 전역 미니맵 이미지
    src/
      components/      # 화면 컴포넌트
      api.js           # Axios API 클라이언트
      i18n.js          # 한국어 문구
      App.jsx          # 전체 화면 흐름
    package.json
  outputs/             # 문서/PPT 산출물, git 제외
  start-dev.bat
  stop-dev.bat
```

## 실행 준비

### Backend

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

### Frontend

```bash
cd frontend
npm install
```

## 개발 서버 실행

루트 폴더에서 실행하면 백엔드와 프론트엔드가 각각 새 창으로 실행됩니다.

```bash
start-dev.bat
```

수동 실행이 필요하면 아래처럼 실행합니다.

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev
```

프론트엔드 주소:

```text
http://127.0.0.1:5173
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

## 주요 API

### Auth

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Preferences

- `GET /api/preferences`
- `PUT /api/preferences`

사용자의 자유문장 성향 프로필을 저장합니다. 추천 시 장소 선택의 중심 기준으로 사용됩니다.

### Recommendation

- `POST /api/analyze`

도시, 현재 기분, 현재 위치, 이번 여행에서 이미 추천/기록한 장소명을 받아 실제 장소 1곳을 추천합니다. AI는 web_search로 장소 실존 여부를 확인하고, 프론트에 표시되는 도시 미니맵 이미지 기준의 `map_x`, `map_y` 좌표를 반환합니다.

### Trip Chat

- `POST /api/place-chat`

추천 장소를 중심으로 사용자가 여행 전, 이동 중, 방문 후에 이어서 대화할 수 있는 API입니다. 프론트는 장소별 대화 내역을 유지하고, 새 추천을 받을 때 초기화합니다.

### Records / Postcards

- `POST /api/postcard`
- `PATCH /api/postcard/{postcard_id}/next-place`
- `POST /api/trip/{trip_id}/final-postcard`
- `GET /api/archive`

`POST /api/postcard`는 이름은 기존 호환을 위해 유지하지만 현재 역할은 장소별 `기록` 생성입니다. 최종 여행 엽서는 `POST /api/trip/{trip_id}/final-postcard`에서 생성되며 `artifact_type=postcard`로 저장됩니다.

## 현재 구현 범위

포함:

- 웹 기반 프로토타입
- 로그인 기반 개인 성향 저장
- 서울/파리 대상 AI 장소 추천
- 장소별 동행 대화
- 도시 전역 미니맵 기반 대략 위치 표시
- 장소별 기록 이미지 생성
- 사진 기반 콜라주 생성
- 기록/엽서 분리 보관
- 최종 여행 엽서 생성

제외:

- 실제 지도 API 연동 및 길찾기
- 예약/결제
- 실시간 위치 추적 기반 추천
- 외부 SNS API 직접 게시
- 운영 배포 및 관리자 페이지

## 개발 참고

프론트엔드 빌드:

```bash
cd frontend
npm run build
```

프론트엔드 린트:

```bash
cd frontend
npm run lint
```

백엔드 문법 확인:

```bash
python -m py_compile backend\main.py backend\ai_service.py backend\database.py
```

개발 서버 종료:

```bash
stop-dev.bat
```
