import os
import math
import requests
from fpdf import FPDF

def create_dummy_pdf(path, with_metadata=False):
    """Generates a dummy PDF with >2000 words. Can conditionally add metadata."""
    pdf = FPDF()
    if with_metadata:
        pdf.set_author("Jane Doe")
        pdf.set_title("My Report")
        
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i in range(1, 300):
        pdf.cell(200, 10, txt=f"Dummy long context line {i} to test chunking mechanisms. " * 2, ln=True, align='L')
    pdf.output(path)

def test_absolute_paths_and_ui():
    """1. Verify paths and static UI contents"""
    assert os.path.exists("/app/workspace/src/api.py"), "API file missing."
    assert os.path.exists("/app/workspace/src/static/index.html"), "GUI file missing."
    
    try:
        res = requests.get("http://localhost:8000/static/index.html", timeout=3)
        assert res.status_code == 200, "GUI endpoint non-200."
        html = res.text.lower()
        assert 'type="file"' in html, "UI missing file upload."
        assert 'fetch(' in html or 'xmlhttprequest' in html, "UI missing API call logic."
        assert 'json.stringify' in html or 'textcontent' in html or 'innerhtml' in html or 'innertext' in html, "UI does not render the API response."
    except requests.exceptions.RequestException:
        assert False, "Failed to connect to GUI server."

def test_extraction_fallback_and_chunking():
    """2. Test fallback metadata, robust chunking math, and topic schemas"""
    pdf_path = "/tmp/fallback_test.pdf"
    create_dummy_pdf(pdf_path, with_metadata=False)

    with open(pdf_path, 'rb') as f:
        files = {'file': ('fallback_test.pdf', f, 'application/pdf')}
        response = requests.post("http://localhost:8000/extract", files=files, timeout=10)
        
    assert response.status_code == 200, "API endpoint failed."
    data = response.json()
    
    for key in ['author', 'title', 'topics', 'total_chunks', 'filename', 'total_words']:
        assert key in data, f"Missing key: {key}"
        
    assert data['author'] == "Unknown Author"
    assert data['title'] == "Untitled"
    assert data['filename'] == "fallback_test.pdf"
    
    assert isinstance(data['total_words'], int)
    assert data['total_words'] >= 2000, "total_words must accurately reflect PDF length."
    assert data['total_chunks'] >= 3, "Expected >=3 chunks for large dummy PDF."
    
    expected_min_chunks = math.ceil(data['total_words'] / 1000)
    assert data['total_chunks'] >= expected_min_chunks, (
        f"Expected at least {expected_min_chunks} chunks for "
        f"{data['total_words']} words with 1000-word cap, "
        f"got {data['total_chunks']}."
    )
    
    assert isinstance(data['topics'], list), "topics must be a list."
    assert len(data['topics']) > 0, "topics list cannot be empty."
    assert all(isinstance(t, str) and len(t) > 0 for t in data['topics']), "topics must be valid strings."
    
    expected_any = {"chunking", "context", "testing", "mechanisms", "dummy"}
    found = [t.lower() for t in data['topics']]
    assert any(kw in " ".join(found) for kw in expected_any), \
        f"Topics {found} do not reflect PDF content."

def test_extraction_positive_metadata():
    """3. Verify actual metadata extraction from a valid PDF"""
    pdf_path = "/tmp/meta_test.pdf"
    create_dummy_pdf(pdf_path, with_metadata=True)

    with open(pdf_path, 'rb') as f:
        files = {'file': ('meta_test.pdf', f, 'application/pdf')}
        response = requests.post("http://localhost:8000/extract", files=files, timeout=10)
        
    assert response.status_code == 200
    data = response.json()
    
    assert data['author'] == "Jane Doe", "Failed to extract correct author from metadata."
    assert data['title'] == "My Report", "Failed to extract correct title from metadata."
