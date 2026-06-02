import io
import re
import json
from datetime import datetime
from pathlib import Path

import PyPDF2
import docx

LOG_FILE = Path(__file__).parent.parent / "logs" / "cv_log.json"


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Read all pages from a PDF and return concatenated plain text."""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Read all paragraphs from a DOCX and return concatenated plain text."""
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def parse_cv_data(text: str) -> dict:
    """
    Extract structured fields from raw CV text using simple heuristics.
    Returns a dict with: name, email, education, experience.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Email — standard regex pattern
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    email = email_match.group(0) if email_match else None

    # Name — assume the very first non-empty line is the candidate's name
    name = lines[0] if lines else None

    # Education — lines following a heading that contains an education keyword
    education_keywords = ["education", "university", "college", "bachelor", "master", "phd", "degree", "diploma"]
    education = _extract_section(lines, education_keywords)

    # Experience — lines following a heading that contains a work/experience keyword
    experience_keywords = ["experience", "work history", "employment", "career", "position", "job", "role"]
    experience = _extract_section(lines, experience_keywords)

    return {
        "name": name,
        "email": email,
        "education": education,
        "experience": experience,
    }


def _extract_section(lines: list, keywords: list, max_lines: int = 10) -> list:
    """
    Scan lines for a heading matching any keyword, then collect up to
    max_lines lines that follow it before stopping.
    """
    result = []
    capturing = False
    captured = 0

    for line in lines:
        if any(kw in line.lower() for kw in keywords):
            # Found a section heading — start capturing what follows
            capturing = True
            captured = 0
            continue

        if capturing:
            if captured >= max_lines:
                break
            result.append(line)
            captured += 1

    return result


def log_extraction(filename: str, parsed_data: dict) -> None:
    """Append one JSON line to the audit log recording what was extracted and when."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "filename": filename,
        "extracted": parsed_data,
    }
    # Ensure the logs directory exists (safe to call even if it already does)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
