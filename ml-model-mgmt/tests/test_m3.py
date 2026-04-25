import os
import re

def test_m3_inference_endpoint(client):
    """1 pt: add a dummy prediction route POST /api/v1/predict."""
    assert client is not None
    response = client.post('/api/v1/predict', json={"features": [1, 2, 3]})
    assert response.status_code == 200
    data = response.get_json()
    assert "prediction" in data, "Response missing 'prediction' key"
    assert isinstance(data["prediction"], (int, float)), \
        "prediction value must be a number (int or float)"
    # Verify the output depends on input features — not a hardcoded constant
    r2 = client.post('/api/v1/predict', json={"features": [10, 20, 30]})
    assert r2.get_json()["prediction"] != data["prediction"], \
        "Prediction must depend on input features, not be a hardcoded constant"

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

    # Remove dead code patterns — if(false){...} blocks that would never execute
    content = re.sub(r'if\s*\(\s*false\s*\)\s*\{[^}]*\}', '', content, flags=re.DOTALL)
    content = re.sub(r'if\s*\(\s*0\s*\)\s*\{[^}]*\}', '', content, flags=re.DOTALL)
    
    content_lower = content.lower()
    
    assert 'fetch(' in content or 'xmlhttprequest' in content_lower, "No fetch/XHR call found in active code"
    assert '/api/v1/predict' in content, "Fetch does not target /predict endpoint"
    assert 'e.preventdefault' in content_lower or 'event.preventdefault' in content_lower or 'return false' in content_lower, "Missing preventDefault to stop page reload"
    assert 'spinner' in content_lower or 'loading' in content_lower or 'display: block' in content_lower or 'display:block' in content_lower, "Missing loading state/spinner"
    assert '.catch(' in content or 'catch ' in content or 'onerror' in content_lower, "Missing error handling for failed API call"
    
    # Verify DOM update logic exists
    dom_update = any(kw in content_lower for kw in ['innerhtml', 'textcontent', 'appendchild', 'innertext', '.text(', '.html('])
    assert dom_update, "No DOM/chart update logic found after fetch"
