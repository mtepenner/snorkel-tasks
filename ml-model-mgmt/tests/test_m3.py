import os
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
    
    if not os.path.exists(js_or_html_path):
        pytest.fail("HTML missing")
        
    with open(js_or_html_path, 'r') as f:
        content = f.read()
        
    # STRENGTHENED: Verify actual fetch/XHR call exists, not just string literal
    assert 'fetch(' in content or 'XMLHttpRequest' in content, "No fetch/XHR call found"
    assert '/api/v1/predict' in content, "Fetch does not target /predict endpoint"
    
    # STRENGTHENED: Verify no-reload
    assert 'e.preventdefault' in content.lower() or 'return false' in content.lower() or 'event.preventdefault' in content.lower(), "Missing preventDefault to stop page reload"
    
    # STRENGTHENED: Verify loading spinner
    assert 'spinner' in content.lower() or 'loading' in content.lower(), "Missing loading state/spinner"
    
    # STRENGTHENED: Verify error handling
    assert '.catch(' in content or 'catch ' in content or 'onerror' in content.lower(), "Missing error handling for failed API call"
