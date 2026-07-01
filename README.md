# 감성 여행 엽서: AI가 안내하는 감성 도시 여행

React(Vite + Tailwind) 프론트엔드와 Python FastAPI 백엔드로
구성되어 있으며, 여행자의 기분을 도시 추천으로 연결하고, 방문 후에는 AI 생성 엽서(텍스트 + 이미지)로 마무리 됩니다.

## 아키텍처

- `/backend` — FastAPI + SQLite. NVIDIA NIM API를 다음 용도로 사용합니다:
  - 기분 분석 및 엽서 텍스트 생성 (`deepseek-ai/deepseek-v4-pro`)
  - 엽서 사진 생성 (`black-forest-labs/flux.1-dev`, NVIDIA가 호스팅하는
    `ai.api.nvidia.com/v1/genai/...` NIM 엔드포인트 — 채팅 모델과 동일한 API 키 사용)
- `/frontend` — React(Vite) + Tailwind CSS, 한국어/영어(KO/EN) 언어 토글 포함.

## 설치 및 실행

`backend/venv`와 `frontend/node_modules` 설정을 먼저 마치면(아래 참고), 다음 명령으로
두 서버를 한 번에 실행할 수 있습니다:

```bash
start-dev.bat
```

새 창 두 개가 열립니다 — 백엔드는 8000번 포트, 프론트엔드는 5173번 포트입니다. 종료하려면:

```bash
stop-dev.bat
```

### 백엔드

```bash
cd backend
python -m venv venv
./venv/Scripts/activate   # Windows 기준; macOS/Linux에서는 `source venv/bin/activate`
pip install -r requirements.txt
```

`backend/.env` 파일을 만들고 NVIDIA NIM API 키를 넣어주세요:

```
NVIDIA_NIM_API_KEY=nvapi-...
```

> 키가 없다면 https://build.nvidia.com/ 에서 무료로 가입 후, 아무 모델 페이지에서
> "Get API Key"를 눌러 발급받으면 됩니다. (`start-dev.bat`을 실행하면 키가 없을 때
> 이 안내가 자동으로 표시됩니다.)

API 서버 실행 (시작 시 SQLite 데이터베이스를 자동으로 초기화하고 시드 데이터를 채웁니다):

```bash
uvicorn main:app --reload --port 8000
```

API 문서: http://127.0.0.1:8000/docs

> 참고: NVIDIA NIM 트라이얼 엔드포인트는 요청당 30~90초 이상 걸릴 수 있습니다. 정상적인
> 현상이며, 프론트엔드는 별도의 타임아웃 없이 여유 있는 로딩 상태를 보여줍니다.

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

앱 주소: http://127.0.0.1:5173 — `/api/*` 요청은 백엔드로 프록시됩니다 (`vite.config.js` 참고).

## API 엔드포인트

- `POST /api/analyze` — `{ city, mood_text, language }` → 은유적 단서, 태그, 매칭된 장소 목록을
  반환합니다. `language`는 `"ko"` 또는 `"en"`이며, 태그는 장소 매칭을 위해 항상 영어로 반환됩니다.
- `POST /api/postcard` — `{ city, place_name, review, language }` → 생성된 엽서를 저장하고
  반환합니다. FLUX.1-dev가 그린 사진이 base64로 인코딩된 `image_base64` 필드에 포함됩니다.
- `GET /api/archive` — 저장된 모든 엽서를 최신순으로 반환합니다.
- `GET /api/places?city=` — 시드된 관광지 목록 (디버그/조회용).
