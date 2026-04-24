import os

def test_m3_inference_endpoint(client):
    """1 pt: add a dummy prediction route POST /api/v1/predict."""
    assert client is not None
    response = client.post('/api/v1/predict', json={"features": [1, 2, 3]})
    assert response.status_code == 200
    assert "prediction" in response.get_json(), "Response missing 'prediction' key"

def test_m3_frontend_fetch_logic():
    """1 pt: write some fetch logic in frontend to hit the /predict endpoint."""
    js_logic_found = False
    
    # Check index.html for embedded JS
    if os.path.exists('/app/workspace/src/templates/index.html'):
        with open('/app/workspace/src/templates/index.html', 'r') as f:
            if '/api/v1/predict' in f.read():
                js_logic_found = True
    
    # Check external JS if it exists
    js_path = '/app/workspace/src/static/js/app.js'
    if os.path.exists(js_path):
        with open(js_path, 'r') as f:
            if '/api/v1/predict' in f.read():
                js_logic_found = True

    assert js_logic_found, "Fetch logic for /predict not found in frontend files"