import math
import re
from pathlib import Path

import requests
from fpdf import FPDF

API_PATH = Path("/app/workspace/src/api.py")
UI_PATH = Path("/app/workspace/src/static/index.html")
BASE_URL = "http://localhost:8000"
EXPECTED_KEYS = {"author", "title", "topics", "total_chunks", "filename", "total_words"}
STOP_WORDS = {"the", "to", "a", "an", "is", "in", "and", "of", "for", "it"}
PDF_TOPIC_WORDS = {"dummy", "long", "context", "line", "test", "chunking", "mechanisms"}


def create_dummy_pdf(path, with_metadata=False):
    """Generate a long PDF with repeated topic-heavy text and optional metadata."""
    pdf = FPDF()
    if with_metadata:
        pdf.set_author("Jane Doe")
        pdf.set_title("My Report")

    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i in range(1, 300):
        line = f"Dummy long context line {i} to test chunking mechanisms. " * 2
        pdf.cell(200, 10, txt=line, ln=True, align="L")
    pdf.output(path)


def create_boundary_pdf(path, word_count=1001):
    """Generate a PDF that should require exactly two chunks with a 1000-word cap."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    words = ["alpha"] * word_count
    for start in range(0, word_count, 20):
        pdf.multi_cell(190, 8, " ".join(words[start:start + 20]))
    pdf.output(path)


def post_extract(pdf_path, filename):
    with open(pdf_path, "rb") as handle:
        files = {"file": (filename, handle, "application/pdf")}
        return requests.post(f"{BASE_URL}/extract", files=files, timeout=10)


def test_required_files_exist():
    """1. Verify the API and UI files exist at the required absolute paths."""
    assert API_PATH.exists(), "API file missing."
    assert UI_PATH.exists(), "GUI file missing."


def test_api_source_uses_required_frameworks():
    """2. Verify the API source uses the expected app name, PDF reader, and static mount."""
    api_source = API_PATH.read_text(encoding="utf-8")
    assert re.search(r"^app\s*=\s*FastAPI\(", api_source, re.MULTILINE), (
        "FastAPI application instance must be named 'app' for uvicorn api:app to resolve."
    )
    assert "PyPDF2" in api_source or "PdfReader" in api_source, (
        "api.py must use PyPDF2.PdfReader — no other PDF library is installed."
    )
    assert "StaticFiles" in api_source, "api.py must mount /static using StaticFiles."
    assert re.search(r"app\.mount\(\s*[\"']\/static[\"']", api_source), (
        "api.py must mount the /static path explicitly."
    )


def test_static_ui_accessible_and_functional():
    """3. Verify /static/index.html loads and contains the required manual test UI."""
    response = requests.get(f"{BASE_URL}/static/index.html", timeout=3)
    assert response.status_code == 200, "GUI endpoint non-200."
    html = response.text.lower()
    assert 'type="file"' in html, "UI missing file upload."
    assert "fetch(" in html or "xmlhttprequest" in html, "UI missing API call logic."
    assert any(token in html for token in ("json.stringify", "textcontent", "innerhtml", "innertext")), (
        "UI does not render the API response."
    )


def test_extract_rejects_get_requests():
    """4. GET /extract must be rejected because the contract is POST-only."""
    response = requests.get(f"{BASE_URL}/extract", timeout=3)
    assert response.status_code == 405, "GET /extract should not be allowed."


def test_extraction_fallback_and_chunking():
    """5. Verify fallback metadata, exact chunk math, and topic quality for long PDFs."""
    pdf_path = "/tmp/fallback_test.pdf"
    create_dummy_pdf(pdf_path, with_metadata=False)

    response = post_extract(pdf_path, "fallback_test.pdf")
    assert response.status_code == 200, "API endpoint failed."
    data = response.json()

    assert set(data.keys()) == EXPECTED_KEYS, f"Unexpected response keys: {sorted(data.keys())}"
    assert data["author"] == "Unknown Author"
    assert data["title"] == "Untitled"
    assert data["filename"] == "fallback_test.pdf"

    assert isinstance(data["total_words"], int)
    assert 2000 <= data["total_words"] <= 10000, (
        f"total_words={data['total_words']} is outside the plausible range for this PDF."
    )
    assert data["total_chunks"] >= 3, "Expected >=3 chunks for large dummy PDF."

    expected_chunks = math.ceil(data["total_words"] / 1000)
    assert data["total_chunks"] == expected_chunks, (
        f"Expected exactly {expected_chunks} chunks for {data['total_words']} words with a 1000-word cap, "
        f"got {data['total_chunks']}."
    )

    assert isinstance(data["topics"], list), "topics must be a list."
    assert 3 <= len(data["topics"]) <= 10, "topics must contain between 3 and 10 keywords."
    assert all(isinstance(topic, str) and topic.strip() for topic in data["topics"]), (
        "topics must be valid non-empty strings."
    )

    found_topics = {topic.lower() for topic in data["topics"]}
    assert not found_topics & STOP_WORDS, f"Topics contain obvious stop words: {sorted(found_topics & STOP_WORDS)}"
    matches = PDF_TOPIC_WORDS & found_topics
    assert len(matches) >= 3, (
        f"Expected >=3 topic keywords from the PDF text {PDF_TOPIC_WORDS}, got {sorted(matches)} in topics {sorted(found_topics)}."
    )


def test_chunk_boundary_uses_1000_word_cap():
    """6. A PDF just over the boundary must require exactly two chunks."""
    pdf_path = "/tmp/boundary_test.pdf"
    create_boundary_pdf(pdf_path, word_count=1001)

    response = post_extract(pdf_path, "boundary_test.pdf")
    assert response.status_code == 200
    data = response.json()

    assert 1001 <= data["total_words"] < 2000, (
        f"Boundary test expected between 1001 and 1999 words, got {data['total_words']}."
    )
    assert data["total_chunks"] == math.ceil(data["total_words"] / 1000) == 2, (
        f"Expected exactly 2 chunks for the boundary PDF, got {data['total_chunks']} for {data['total_words']} words."
    )


def test_extraction_positive_metadata():
    """7. Verify real metadata is extracted from a PDF that contains it."""
    pdf_path = "/tmp/meta_test.pdf"
    create_dummy_pdf(pdf_path, with_metadata=True)

    response = post_extract(pdf_path, "meta_test.pdf")
    assert response.status_code == 200
    data = response.json()

    assert data["author"] == "Jane Doe", "Failed to extract correct author from metadata."
    assert data["title"] == "My Report", "Failed to extract correct title from metadata."
