import os
import re
import pytest

def test_m3_inference_endpoint(client):
    """1 pt: add a dummy prediction route POST /api/v1/predict."""
    assert client is not None
    response = client.post('/api/v1/predict', json={"features": [1, 2, 3]})
    assert response.status_code == 200
    assert "prediction" in response.get_json(), "Response missing 'prediction' key"

def test_m3_frontend_fetch_logic():
    """1 pt: write some fetch logic in frontend to hit the /predict endpoint."""
    js_or_html_path = '/app/workspace/src/templates/index.html'
    js_path = '/app/workspace/src/static/js/app.js'
    
    content = ""
    if os.path.exists(js_or_html_path):
        with open(js_or_html_path, 'r') as f:
            content += f.read()
    if os.path.exists(js_path):
        with open(js_path, 'r') as f:
            content += f.read()
            
    assert content, "Frontend files missing"
    
    # Strip HTML and JS comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content)
    
    content_lower = content.lower()
    
    # STRENGTHENED: Must be inside an event listener!
    listener_pattern = re.compile(r'(addEventListener\s*\(\s*['"](?:click|submit)['"]|onsubmit\s*=|onclick\s*=).*?(?:fetch|XMLHttpRequest)', re.IGNORECASE | re.DOTALL)
    assert listener_pattern.search(content), "Fetch logic must be triggered by a genuine event listener (click/submit), not floating standalone"

    assert 'fetch(' in content or 'xmlhttprequest' in content_lower, "No fetch/XHR call found"
    assert '/api/v1/predict' in content, "Fetch does not target /predict endpoint"
    assert 'e.preventdefault' in content_lower or 'event.preventdefault' in content_lower or 'return false' in content_lower, "Missing preventDefault"
    assert 'spinner' in content_lower or 'loading' in content_lower or 'display: block' in content_lower or 'display:block' in content_lower, "Missing loading state"
    assert '.catch(' in content or 'catch ' in content or 'onerror' in content_lower, "Missing error handling"
    
    dom_update = any(kw in content_lower for kw in ['innerhtml', 'textcontent', 'appendchild', 'innertext', '.text(', '.html('])
    assert dom_update, "No DOM/chart update logic found after fetch"
