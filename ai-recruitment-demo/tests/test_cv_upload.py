import io
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Reusable parsed CV result returned by the mocked parser
FAKE_PARSED = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "education": ["BSc Computer Science"],
    "experience": ["Software Engineer at Acme"],
}


def test_valid_pdf_upload():
    """A well-formed PDF upload should return 200 with the parsed CV fields."""
    with (
        patch("routers.cv_router.extract_text_from_pdf", return_value="Jane Doe\njane@example.com"),
        patch("routers.cv_router.parse_cv_data", return_value=FAKE_PARSED),
        patch("routers.cv_router.log_extraction"),
    ):
        response = client.post(
            "/upload-cv",
            files={"file": ("resume.pdf", io.BytesIO(b"fake pdf bytes"), "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "resume.pdf"
    assert body["parsed"] == FAKE_PARSED


def test_invalid_file_type_is_rejected():
    """Uploading a .txt file should return 400 with a clear error message."""
    response = client.post(
        "/upload-cv",
        files={"file": ("notes.txt", io.BytesIO(b"plain text"), "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_file_over_5mb_is_rejected():
    """A file larger than 5 MB should be rejected with a 400 before parsing."""
    # 5 MB + 1 byte — just over the limit
    oversized_content = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/upload-cv",
        files={"file": ("huge_cv.pdf", io.BytesIO(oversized_content), "application/pdf")},
    )

    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()
