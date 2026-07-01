# Context: Project Specification (React + Python FastAPI version)
You are an expert full-stack engineer. I need you to implement a web service project titled "Mood Trip Postcard: AI-guided Emotional City Travel" based on the following requirements. This is a 1-week MVP project, so we will use a decoupled architecture: a Python FastAPI backend and a React (Vite) frontend with Tailwind CSS.

## Core Features to Implement
1. **City & Mood Input**: A UI page where users select a city (e.g., Paris, Seoul) and input their current mood/desired atmosphere in natural language.
2. **AI Emotional Analysis & Recommendation**: 
   - Analyze user input using NVIDIA NIM API (`meta/llama-3.3-70b-instruct`) to extract emotional keywords and generate a "metaphorical clue".
   - Match these keywords with a pre-seeded SQLite database of tourist spots containing emotion/vibe tags.
3. **Travel Log & Postcard Generation**: 
   - After "visiting", the user inputs a short review.
   - AI generates a personalized "Digital Travel Postcard" containing a poetic title, an emotional message, and a next recommended spot.
4. **Postcard Archive**: Save generated postcards in SQLite and display them in a beautiful React grid sorted by date.

---

## Task Instructions for Claude Code

Please generate the complete, production-ready codebase separated into `/backend` and `/frontend` folders.

### 1. Backend (`/backend`)
- **`database.py`**: SQLite setup for `places` and `postcards` tables. Include a seed function that pre-populates at least 5 emotional spots for Paris (e.g., Seine riverside, Pont des Arts, Montmartre) and 5 for Seoul with rich mood tags.
- **`ai_service.py`**: Wrapper for NVIDIA NIM API (`https://integrate.api.nvidia.com/v1`) using the `meta/llama-3.3-70b-instruct` model to perform:
  1. Mood analysis (returns structured JSON with tags and clue).
  2. Postcard generation (returns title and poetic content).
- **`main.py`**: FastAPI application with CORS enabled for the React frontend. Implement endpoints:
  - `POST /api/analyze` (returns clue and recommended places)
  - `POST /api/postcard` (creates and saves a postcard)
  - `GET /api/archive` (fetches all saved postcards)

### 2. Frontend (`/frontend`)
- Setup a React project using Vite and Tailwind CSS.
- Create an intuitive, emotional UI containing:
  - **Mood Form**: Elegant text area for mood entry and dropdown for city.
  - **Recommendation View**: Displays the AI's metaphorical clue in a beautiful typography block, followed by tourist spots rendered as interactive UI cards.
  - **Postcard Creator & Viewer**: A dedicated component that styled like a real physical postcard (front: title/message, back: review/date) with clean CSS transitions.
  - **Archive Tab**: A grid layout displaying all archived postcards like a gallery.

Please write clean, documented, modular code. Initialize the backend database automatically on startup and provide a simple setup instruction.