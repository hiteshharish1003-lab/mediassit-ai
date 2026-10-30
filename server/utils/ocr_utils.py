# server/utils/ocr_utils.py
import re
import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import spacy

nlp = spacy.load("en_core_web_sm")


# -----------------------------
# OCR HELPERS
# -----------------------------

def _pdf_to_text(file_path: str):
    pages = convert_from_path(file_path, dpi=300)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text


def _image_to_text(file_path: str):
    img = Image.open(file_path)
    return pytesseract.image_to_string(img)


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from image or PDF. Returns raw text (not cleaned).
    """
    path = file_path.lower()
    if path.endswith(".pdf"):
        return _pdf_to_text(file_path)
    else:
        return _image_to_text(file_path)


# -----------------------------
# CLEANING
# -----------------------------

def clean_text(text: str) -> str:
    text = re.sub(r"[\r\t]+", " ", text)
    text = re.sub(r"\u2019|\u2018", "'", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# -----------------------------
# REGEX EXTRACTION (YOUR OLD CODE)
# -----------------------------

def regex_extract_medical_info(raw_text: str):
    """
    Extract info using regex (fallback). Your exact old code is kept here.
    """
    text = raw_text or ""
    cleaned = clean_text(text)
    t = cleaned.replace("\n", " ")

    info = {
        "patient_name": None,
        "age": None,
        "sex": None,
        "doctor_name": None,
        "dea_number": None,
        "issue_date": None,
        "medications": [],
    }

    # Patient name
    m = re.search(r"Patient\s*Name[:\-]?\s*([A-Z ,]+)", t, re.IGNORECASE)
    if not m:
        m = re.search(r"Patient[:\-]?\s*([A-Z ,]+)", t, re.IGNORECASE)
    info["patient_name"] = m.group(1).strip() if m else None

    # Age
    m = re.search(r"Age[:\-]?\s*(\d{1,3})", t, re.IGNORECASE)
    if m:
        info["age"] = m.group(1)

    # Sex
    m = re.search(r"Sex[:\-]?\s*(Male|Female|M|F)", t, re.IGNORECASE)
    if m:
        info["sex"] = m.group(1).upper()

    # Doctor
    m = re.search(r"Prescribed by[:\-]?\s*([A-Za-z .]+)", t, re.IGNORECASE)
    if not m:
        m = re.search(r"Prescribed\s*by[:\-]?\s*([A-Za-z .]+)", t, re.IGNORECASE)
    info["doctor_name"] = m.group(1).strip() if m else None

    # DEA
    m = re.search(r"DEA[:#\s\-]*([A-Z0-9]+)", t, re.IGNORECASE)
    if m:
        info["dea_number"] = m.group(1).strip()

    # Date Issued
    m = re.search(r"(Date Issued|Start Date|Date)[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", t, re.IGNORECASE)
    if m:
        info["issue_date"] = m.group(2).strip()

    # Medications
    meds = []
    rx_blocks = re.split(r"\bRx[:\s]", cleaned)
    for block in rx_blocks[1:]:
        sd = re.search(r"Start Date[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", block, re.IGNORECASE)
        start_date = sd.group(1).strip() if sd else None

        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines: continue

        drug_line = lines[0]
        details = " ".join(lines[1:]) if len(lines) > 1 else ""
        if start_date:
            details += f" Start Date: {start_date}"

        meds.append({"drug": drug_line, "details": details})

    info["medications"] = meds

    # NLP (spaCy)
    doc = nlp(cleaned)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    return cleaned, info, entities


# -----------------------------
# COMBINED LLM + REGEX PROCESSOR
# -----------------------------

def extract_medical_info(raw_text: str):
    """
    1. Perform regex extraction (fast local fallback)
    2. Send full OCR text to LLM to enhance/override missing fields
    3. Merge LLM output with regex output
    """

    cleaned, regex_info, entities = regex_extract_medical_info(raw_text)

    # Call LLM (import locally to avoid circular import)
    try:
        from .llm_parser import parse_prescription_llm
    except Exception:
        try:
            # try importing by module name when running as package
            from utils.llm_parser import parse_prescription_llm
        except Exception:
            # Last resort: load file by path
            import importlib.util
            lp = os.path.join(os.path.dirname(__file__), "llm_parser.py")
            spec = importlib.util.spec_from_file_location("llm_parser_local", lp)
            llm_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(llm_mod)
            parse_prescription_llm = llm_mod.parse_prescription_llm

    llm_output = parse_prescription_llm(raw_text)

    # Merge fields (LLM overrides only if present)
    final = {}

    def pick(llm, regex):
        return llm if llm not in ("", None, "N/A") else regex

    final["patient_name"] = pick(llm_output.get("patient_name"), regex_info.get("patient_name"))
    final["age"] = pick(llm_output.get("age"), regex_info.get("age"))
    final["sex"] = pick(llm_output.get("sex"), regex_info.get("sex"))
    final["doctor_name"] = pick(llm_output.get("doctor_name"), regex_info.get("doctor_name"))
    final["dea_number"] = pick(llm_output.get("dea_number"), regex_info.get("dea_number"))
    final["issue_date"] = pick(llm_output.get("date_issued"), regex_info.get("issue_date"))

    # use LLM medications ALWAYS (more accurate)
    final["medications"] = llm_output.get("medications", regex_info["medications"])

    return {
        "cleaned_text": cleaned,
        "structured_info": final,
        "entities": entities,
        "llm_raw": llm_output  # optional, good for debugging
    }


# -----------------------------
# SUMMARY
# -----------------------------

def generate_summary(processed: dict) -> str:
    p = processed.get("structured_info", {})

    lines = []
    lines.append(f"👤 Patient: {p.get('patient_name') or 'N/A'}")
    lines.append(f"🎂 Age: {p.get('age') or 'N/A'} | ⚧ Sex: {p.get('sex') or 'N/A'}")
    lines.append(f"🧑‍⚕️ Doctor: {p.get('doctor_name') or 'N/A'}")
    lines.append(f"🆔 DEA #: {p.get('dea_number') or 'N/A'}")
    lines.append(f"📅 Date Issued: {p.get('issue_date') or 'N/A'}")
    lines.append("\n💊 Prescriptions:")

    meds = p.get("medications", [])
    if meds:
        for med in meds:
            lines.append(f"- {med.get('medicine_name') or med.get('drug')} ({med.get('dosage') or med.get('details')})")
    else:
        lines.append("- No medications detected")

    return "\n".join(lines)
