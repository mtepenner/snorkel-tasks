import os
import requests
from fpdf import FPDF

def create_dummy_pdf(path):
    """Generates a dummy PDF with no metadata to test fallbacks, and >2000 words to test chunking."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Generate ~2400 words
    for i in range(1, 300):
        pdf.cell(200, 10, txt=f"Dummy long context line {i} to test chunking mechanisms. " * 2, ln=True, align='L')
    pdf.output(path)

def test_absolute_paths_and_code_constraints():
    """1. Verify paths and enforce the 1000-word chunking constraint statically"""
    api_path = "/app/workspace/src/api.py"
    gui_path = "/app/workspace/src/static/index.html"
    
    assert os.path.exists(api_path), "API file is missing from target path."
    assert os.path.exists(gui_path), "GUI file is missing from target path."
    
    # Anti-Cheating: Check that the agent actually programmed the 1000 word limit
    with open(api_path, "r") as f:
        api_code = f.read()
        assert "1000" in api_code, "The 1000-word per chunk max limit is not enforced in the API code."

def test_gui_is_served_and_valid():
    """2. Verify the GUI is served and contains valid upload/print logic"""
    try:
        res = requests.get("http://localhost:8000/static/index.html", timeout=3)
        assert res.status_code == 200, "GUI endpoint returned a non-200 status code."
        
        # Anti-Cheating: Validate the UI actually contains upload and fetch functionality
        html_content = res.text.lower()
        assert 'type="file"' in html_content, "UI does not contain a file upload input."
        assert 'fetch(' in html_content or 'xmlhttprequest' in html_content, "UI does not contain API calling logic."
    except requests.exceptions.RequestException:
        assert False, "Failed to connect to the GUI server on port 8000."

def test_extraction_endpoint():
    """3. Test the extraction API endpoint types, fallbacks, and logic"""
    pdf_path = "/tmp/long_context_test.pdf"
    create_dummy_pdf(pdf_path)

    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('long_context_test.pdf', f, 'application/pdf')}
            response = requests.post("http://localhost:8000/extract", files=files, timeout=10)
    except requests.exceptions.RequestException:
        assert False, "Failed to connect to the backend extraction endpoint."
        
    assert response.status_code == 200, "API endpoint did not return a 200 Success status."
    data = response.json()
    
    # Enforce Exact Schema Presence
    required_keys = ['author', 'title', 'topics', 'total_chunks', 'filename', 'total_words']
    for key in required_keys:
        assert key in data, f"Required key '{key}' is missing from the JSON response."
        
    # Enforce Data Types explicitly
    assert isinstance(data['total_words'], int), "'total_words' must be an integer"
    assert isinstance(data['total_chunks'], int), "'total_chunks' must be an integer"
    assert isinstance(data['topics'], list), "'topics' must be an array/list"
        
    # Verify Fallback Values (Our FPDF dummy has no metadata attached to it)
    assert data['author'] == "Unknown Author", f"Expected fallback 'Unknown Author', got {data['author']}"
    assert data['title'] == "Untitled", f"Expected fallback 'Untitled', got {data['title']}"
    
    # Verify Anti-Cheating Chunk Math
    assert data['total_chunks'] >= 3, f"Expected >= 3 chunks for ~2400-word PDF, got {data['total_chunks']}"
    words_per_chunk = data['total_words'] / data['total_chunks']
    assert words_per_chunk <= 1000, f"Average chunk size {words_per_chunk:.0f} words exceeds 1000 limit."