"""Prescription OCR and structured extraction. The API key stays on the server."""
import json
import os
import re
from pathlib import Path
from typing import Any


def _client():
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    key = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
    if not key:
        return None
    from groq import Groq
    return Groq(api_key=key)


def parse_prescription_llm(ocr_text: str) -> dict[str, Any]:
    client = _client()
    if not client:
        raise RuntimeError("AI is not configured. Add GROQ_API_KEY to server/.env.")
    response = client.chat.completions.create(
        model=os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b"),
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Read prescriptions carefully. Extract only information explicitly visible; never infer missing names, doses, or instructions. Return valid JSON only."},
            {"role": "user", "content": f'''Extract this prescription into JSON. Use empty strings for unknown fields and [] when no medicines are legible. Include a concise plain-language summary based only on the document.\nSchema: {{"patient_name":"","age":"","sex":"","doctor_name":"","clinic":"","date_issued":"","vitals":{{"temperature":"","bp":""}},"medications":[{{"medicine_name":"","dosage":"","frequency":"","duration":""}}],"notes":"","summary":""}}\nDocument OCR:\n{ocr_text[:12000]}'''}
        ],
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(re.search(r"\{[\s\S]*\}", content).group(0))


def parse_jpg_to_structured(filename: str) -> dict[str, Any]:
    """Analyze the actual prescription image with a multimodal vision model.

    Tesseract is intentionally not in this path: conventional OCR often drops
    handwritten medicine names before a language model can inspect them.
    """
    import base64
    import io
    from PIL import Image, ImageOps

    path = Path(__file__).resolve().parents[1] / "uploads" / Path(filename).name
    if not path.is_file():
        raise FileNotFoundError("Uploaded image was not found")
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((2600, 2600))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=92, optimize=True)
    encoded_image = base64.b64encode(buffer.getvalue()).decode("ascii")
    data_url = f"data:image/jpeg;base64,{encoded_image}"

    client = _client()
    if not client:
        raise RuntimeError("AI is not configured. Add GROQ_API_KEY to server/.env.")
    response = client.chat.completions.create(
        model=os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b"),
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You read medical prescription images, including handwriting. Never guess a medicine name or instruction. Inspect the handwritten prescription area carefully; ignore printed clinic menus, service lists, advertisements, and examples. Include only medicines that the prescriber appears to have written for this patient. If handwriting is uncertain, preserve the visible characters in written_as, set confidence to low or medium, and leave medicine_name empty rather than completing a guess. Extract directions only when legible. Return one valid JSON object only."},
            {"role": "user", "content": [
                {"type": "text", "text": '''Read this prescription image. Return exactly this JSON shape. For each apparent medicine line include a row even if its name is unclear, and set confidence to "low" in that case. `written_as` should be a short literal transcription of the medicine line; do not silently correct it. Do not treat printed clinic service menus as prescribed medicine.\n{"patient_name":"","age":"","sex":"","doctor_name":"","clinic":"","date_issued":"","vitals":{"temperature":"","bp":""},"medications":[{"medicine_name":"","written_as":"","confidence":"low","dosage":"","frequency":"","duration":"","common_use":""}],"notes":"","summary":""}'''},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]},
        ],
    )
    content = response.choices[0].message.content or "{}"
    match = re.search(r"\{[\s\S]*\}", content)
    if not match:
        raise ValueError("The image model did not return readable prescription details. Try a closer, sharper image.")
    parsed = json.loads(match.group(0))
    parsed["summary"] = (parsed.get("summary") or "Prescription details were extracted. Please verify every medicine and instruction with your pharmacist.").strip()
    parsed["medications"] = parsed.get("medications") if isinstance(parsed.get("medications"), list) else []
    for med in parsed["medications"]:
        if not isinstance(med, dict):
            continue
        med["confidence"] = med.get("confidence") if med.get("confidence") in {"high", "medium", "low"} else "low"
        med.setdefault("written_as", "")
        med.setdefault("medicine_name", "")
        med.setdefault("common_use", "")

    clear_medicines = [m for m in parsed["medications"] if isinstance(m, dict) and m["confidence"] == "high" and m.get("medicine_name", "").strip()]
    if clear_medicines:
        guidance = client.chat.completions.create(
            model=os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b"),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Provide cautious, general educational information about likely common uses of medicines. Identify medicines only when the name is clear. Do not infer why this specific patient was prescribed them. For ambiguous brands or unreadable names use an empty string. No dosing or treatment advice. JSON only."},
                {"role": "user", "content": "For each clearly identified medicine, return JSON with a `medications` array in the same order, each item having `common_use` as one short general educational sentence. Do not infer why it was prescribed to this patient. Medicines: " + json.dumps([m.get("medicine_name", "") for m in clear_medicines])},
            ],
        )
        uses = json.loads(guidance.choices[0].message.content or "{}").get("medications", [])
        for i, med in enumerate(clear_medicines):
            med["common_use"] = uses[i].get("common_use", "") if i < len(uses) and isinstance(uses[i], dict) else ""
    parsed["nlp_entities"] = []
    parsed["disclaimer"] = "AI can misread handwriting. Confirm medicine names and directions with your prescriber or pharmacist before acting."
    return parsed
