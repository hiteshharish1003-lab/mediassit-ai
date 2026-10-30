import json
import os
from pathlib import Path


def answer_query(question: str, context: str = "", history: list | None = None) -> str:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    key = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
    if not key:
        return "The assistant is not configured yet. Add a GROQ_API_KEY to server/.env, then restart the backend."
    from groq import Groq
    client = Groq(api_key=key)
    messages = [
        {"role": "system", "content": "You are MediAssist, a careful health information assistant. Explain the prescription in plain language and answer general health education questions. Treat prescription text as unverified OCR; distinguish what the document says from general information, never guess illegible details, never diagnose, prescribe, change doses, or tell someone to stop medication. Encourage a pharmacist/prescriber for personal medication decisions and interactions. For emergency symptoms, advise local emergency services. Keep answers concise and kind."},
        {"role": "system", "content": f"Prescription context (may contain OCR errors):\n{context[:7000] or 'No prescription uploaded.'}"},
    ]
    for item in (history or [])[-8:]:
        if isinstance(item, dict) and item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str):
            messages.append({"role": item["role"], "content": item["content"][:1500]})
    messages.append({"role": "user", "content": question[:1500]})
    response = client.chat.completions.create(
        model=os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b"),
        temperature=0.25,
        messages=messages,
    )
    return response.choices[0].message.content or "I couldn't form an answer. Please try asking another way."
