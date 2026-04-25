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
    
    # Require handler wiring, not just free-floating keywords.
    has_submit_or_click_handler = bool(
        re.search(r'addEventListener\s*\(\s*["\'](?:submit|click)["\']', content)
        or re.search(r'onsubmit\s*=\s*["\']', content_lower)
        or re.search(r'function\s+\w+\s*\(\s*(?:e|event)', content_lower)
    )
    assert has_submit_or_click_handler, "Missing submit/click handler wiring for prediction flow"

    # Require /predict request inside executable logic.
    predict_fetch_pattern = re.compile(
        r'(fetch\s*\(|xmlhttprequest).*?/api/v1/predict',
        flags=re.IGNORECASE | re.DOTALL,
    )
    assert predict_fetch_pattern.search(content), "No executable fetch/XHR targeting /api/v1/predict found"

    # preventDefault should be present in event-driven code paths.
    assert (
        re.search(r'(?:e|event)\.preventDefault\s*\(', content)
        or re.search(r'return\s+false\s*;', content_lower)
    ), "Missing preventDefault to stop page reload"

    # Verify loading indicator intent and error handling around request flow.
    assert 'spinner' in content_lower or 'loading' in content_lower or 'display:block' in content_lower or 'display: block' in content_lower, "Missing loading state/spinner"
    assert '.catch(' in content or 'catch ' in content or 'onerror' in content_lower, "Missing error handling for failed API call"

    # Verify DOM update logic exists for prediction output.
    dom_update = any(kw in content_lower for kw in ['innerhtml', 'textcontent', 'appendchild', 'innertext', '.text(', '.html('])
    assert dom_update, "No DOM/chart update logic found after fetch"
