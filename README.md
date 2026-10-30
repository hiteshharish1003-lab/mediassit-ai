# MediAssist

MediAssist reads an uploaded prescription image, organizes legible details, provides cautious general information about clearly identified medicines, and answers follow-up questions using the uploaded result as context.

## Run locally

1. Install the system Tesseract OCR package for your OS.
2. In `server/`, install Python dependencies with `pip install -r requirements.txt`.
3. Copy `server/.env.example` to `server/.env` and set your own `GROQ_API_KEY`. The key stays on the backend and must never be added to the client. Prescription images are analyzed directly with Groq's vision model (`qwen/qwen3.8-27b`); text chat uses `openai/gpt-oss-120b` by default.
4. Start the API from `server/` with `uvicorn main:app --reload`.
5. In `client/`, install dependencies with `npm install` and run `npm run dev`.

The frontend defaults to `http://127.0.0.1:8000`. Set `VITE_API_URL` in a client `.env.local` file to use a different backend URL.

## Medical use

OCR can misread handwriting, and medicine explanations are general educational information. Users should verify medicine names, directions, and personal care decisions with a prescriber or pharmacist. MediAssist is not a diagnostic or prescribing service.
