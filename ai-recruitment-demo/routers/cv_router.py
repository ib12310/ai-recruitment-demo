from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.cv_parser import (
    extract_text_from_docx,
    extract_text_from_pdf,
    log_extraction,
    parse_cv_data,
)

router = APIRouter(tags=["CV"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Accept a CV file upload, validate it, extract text, parse structured
    data, log the result, and return the parsed fields.
    """
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    # Reject any file that is not a PDF or DOCX
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload a PDF or DOCX.",
        )

    content = await file.read()

    # Reject files larger than 5 MB
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum allowed size is 5 MB.",
        )

    # Extract plain text using the appropriate parser
    if ext == ".pdf":
        text = extract_text_from_pdf(content)
    else:
        text = extract_text_from_docx(content)

    # Parse structured fields from the extracted text
    parsed = parse_cv_data(text)

    # Write an audit log entry
    log_extraction(filename, parsed)

    return {"filename": filename, "parsed": parsed}
