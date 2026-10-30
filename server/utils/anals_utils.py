# server/utils/analytics_utils.py
import re

def detect_medical_risks(structured_data: dict):
    """
    Simple heuristics to detect risks (opioid co-prescription, duplicate dosages, missing patient info).
    """
    insights = []
    meds = structured_data.get("medications", []) or []
    med_names = [m.get("drug", "").lower() for m in meds]

    opioids = ["morphine", "oxycodone", "codeine", "hydrocodone", "fentanyl", "norco"]
    found_opioids = [m for m in med_names if any(o in m for o in opioids)]
    if len(found_opioids) > 1:
        insights.append({
            "type": "warning",
            "title": "Opioid Combination Alert",
            "detail": f"Multiple opioids detected: {', '.join(found_opioids)}"
        })

    if not structured_data.get("patient_name"):
        insights.append({
            "type": "info",
            "title": "Missing Patient Info",
            "detail": "Patient name not detected in the uploaded document."
        })

    # duplicate dosage detection
    seen = {}
    for m in meds:
        d = m.get("details", "")
        dose_match = re.search(r"(\d+\s*mg)", d, re.IGNORECASE)
        dose = dose_match.group(1) if dose_match else None
        if dose:
            seen.setdefault(dose.lower(), 0)
            seen[dose.lower()] += 1
    for dose, count in seen.items():
        if count > 1:
            insights.append({
                "type": "warning",
                "title": "Duplicate Dosage",
                "detail": f"Dosage {dose} appears {count} times across medications."
            })

    if not meds:
        insights.append({
            "type": "alert",
            "title": "No Medications Found",
            "detail": "No medication blocks were detected in the document."
        })

    return insights
