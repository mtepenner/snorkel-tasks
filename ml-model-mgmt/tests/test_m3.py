import os
import re


def _strip_frontend_comments_and_dead_code(content):
    """Remove comments and a few trivial dead-code wrappers before static checks."""
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content)

    dead_patterns = [
        r'if\s*\(\s*(?:false|0|null|undefined|!1|1\s*===\s*0)\s*\)\s*\{[^}]*\}',
    ]
    for pattern in dead_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)

    return content


def _predict_flow_windows(content_lower, radius=1400):
    windows = []
    for match in re.finditer(r'/api/v1/predict', content_lower):
        start = max(0, match.start() - radius)
        end = min(len(content_lower), match.end() + radius)
        windows.append(content_lower[start:end])
    return windows

def test_m3_inference_endpoint(client):
    """POST /api/v1/predict computes and returns a non-constant prediction value from input features."""
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
    # Verify the output is deterministic — same features must always return the same result
    r3 = client.post('/api/v1/predict', json={"features": [1, 2, 3]})
    assert r3.get_json()["prediction"] == data["prediction"], \
        "Prediction must be deterministic — same features must always return the same value"

def test_m3_frontend_fetch_logic():
    """Verify frontend correctly wires up the prediction fetch request with preventDefault, loading state, error handling, and JSON serialization."""
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
    
    content = _strip_frontend_comments_and_dead_code(content)
    content_lower = content.lower()

    # Require handler wiring, not just free-floating keywords.
    has_submit_or_click_handler = bool(
        re.search(r'addEventListener\s*\(\s*["\'](?:submit|click)["\']', content, flags=re.IGNORECASE)
        or re.search(r'on(?:submit|click)\s*=\s*["\']', content_lower)
    )
    assert has_submit_or_click_handler, "Missing submit/click handler wiring for prediction flow"

    # Require /predict request inside executable logic.
    predict_fetch_pattern = re.compile(
        r'(fetch\s*\(|xmlhttprequest).*?/api/v1/predict',
        flags=re.IGNORECASE | re.DOTALL,
    )
    assert predict_fetch_pattern.search(content), "No executable fetch/XHR targeting /api/v1/predict found"

    request_windows = _predict_flow_windows(content_lower)
    assert request_windows, "Missing a local request flow around /api/v1/predict"

    flow_with_loading_dom_and_error = [
        window for window in request_windows
        if ('spinner' in window or 'loading' in window)
        and any(kw in window for kw in ['innerhtml', 'textcontent', 'appendchild', 'innertext', '.text(', '.html('])
        and bool(re.search(r'\.catch\s*\(|\bcatch\s*\(|onerror', window))
    ]
    assert flow_with_loading_dom_and_error, (
        "Prediction flow must keep loading state, DOM updates, and error handling "
        "near the /api/v1/predict request"
    )

    # preventDefault should be present in event-driven code paths.
    assert (
        any(
            re.search(r'(?:e|event)\.preventdefault\s*\(', window)
            or re.search(r'return\s+false\s*;', window)
            for window in flow_with_loading_dom_and_error
        )
    ), "Missing preventDefault to stop page reload"

    # Require a JSON request body shaped around a features payload.
    assert any(
        'json.stringify' in window and 'features' in window
        for window in flow_with_loading_dom_and_error
    ), "Prediction request must serialize a JSON body containing features"
