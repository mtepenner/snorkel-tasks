import os
import requests
from fpdf import FPDF

def create_dummy_pdf(path):
    """Generates a dummy PDF with enough text to trigger the chunking simulation"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i in range(1, 300):
        pdf.cell(200, 10, txt=f"Dummy long context line {i} to test chunking mechanisms.", ln=True, align='L')
    pdf.output(path)

def test_absolute_paths_exist():
    """1. Verify High Severity Requirement: Absolute Paths"""
    assert os.path.exists("/app/workspace/src/api.py"), "API file is missing from target path."
    assert os.path.exists("/app/workspace/src/static/index.html"), "GUI file is missing from target path."

def test_gui_is_served():
    """2. Verify the GUI is actively being served on the port"""
    try:
        res = requests.get("http://localhost:8000/static/index.html", timeout=3)
        assert res.status_code == 200, "GUI endpoint returned a non-200 status code."
    except requests.exceptions.RequestException:
        assert False, "Failed to connect to the GUI server on port 8000."

def test_extraction_endpoint():
    """3. Test the extraction API endpoint with a real PDF"""
    pdf_path = "/tmp/long_context_test.pdf"
    create_dummy_pdf(pdf_path)

    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('long_context_test.pdf', f, 'application/pdf')}
            response = requests.post("http://localhost:8000/extract", files=files, timeout=10)
    except requests.exceptions.RequestException:
        assert False, "Failed to connect to the backend extraction endpoint."
        
    # Verify successful status code
    assert response.status_code == 200, "API endpoint did not return a 200 Success status."
        
    data = response.json()
    
    # Verify the required keys from the instruction.md are present
    required_keys = ['author', 'title', 'total_chunks', 'topics']
    for key in required_keys:
        assert key in data, f"Required key '{key}' is missing from the JSON response."
        
    # Verify chunking logic actually processed the long document
    assert int(data.get('total_chunks', 0)) >= 1, "Chunking logic failed; 0 chunks reported."