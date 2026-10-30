import os
import json
import utils.llm_parser as llm_parser
UPLOAD_DIR = "uploads"
SUMMARY_DIR = "summaries"

def get_insights():
    """
    Collects summary statistics for the dashboard.
    These can later be computed dynamically based on processed OCR data.
    """
    # Count uploaded files
    total_uploads = len(os.listdir(UPLOAD_DIR)) if os.path.exists(UPLOAD_DIR) else 0

    # Count summaries saved
    total_summaries = len(os.listdir(SUMMARY_DIR)) if os.path.exists(SUMMARY_DIR) else 0

    # Load recent summaries (mock example)
    recent_files = os.listdir(SUMMARY_DIR)[-5:] if total_summaries > 0 else []
    recent_data = []

    for file in recent_files:
        file_path = os.path.join(SUMMARY_DIR, file)
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                recent_data.append({
                    "file": file,
                    "patient": data.get("structured_data", {}).get("patient_name", "Unknown"),
                    "doctor": data.get("structured_data", {}).get("doctor_name", "Unknown"),
                    "drug_count": len(data.get("structured_data", {}).get("medications", []))
                })
        except Exception:
            continue

    # Mocked analytics (could be improved later)
    insights = {
        "total_uploads": total_uploads,
        "total_summaries": total_summaries,
        "average_age": 54,
        "most_common_drug": "Oxycodone",
        "recent_reports": recent_data
    }

    return insights

