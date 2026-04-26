import numpy as np

def test_m1_upload_endpoint_exists(client):
    """POST /api/v1/data/upload accepts JSON arrays and CSV payloads."""
    assert client is not None, "API not implemented"
    response = client.post('/api/v1/data/upload', json=[{"A": 1, "B": None}, {"A": 2, "B": 4}])
    assert response.status_code == 200, "JSON Upload endpoint failed"
    
    csv_data = "A,B\n1,\n2,4\n"
    response_csv = client.post('/api/v1/data/upload', data=csv_data, content_type='text/csv')
    assert response_csv.status_code == 200, "CSV Upload endpoint failed"
    processed = client.get('/api/v1/data/processed').get_json()
    assert len(processed) == 2
    assert "A" in processed[0], "CSV column 'A' not parsed into processed rows"
    assert "B" in processed[0], "CSV column 'B' not parsed into processed rows"

def test_m1_preprocessing_and_retrieval(client):
    """GET /api/v1/data/processed retrieves the cleaned dataset with missing values handled, scaled, and encoded."""
    assert client is not None
    # Skewed column ensures mean-imputation is distinguishable from median/constant fill.
    client.post('/api/v1/data/upload', json=[{"A": 1}, {"A": None}, {"A": 2}, {"A": 100}])
    response = client.get('/api/v1/data/processed')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list) and len(data) == 4, "Processed data malformed"
    
    vals = [row["A"] for row in data]
    assert None not in vals, "Missing values not handled"

    # If mean-imputation is used, the row that had None (second row) becomes column mean,
    # then scales to ~0 after StandardScaler.
    assert abs(vals[1]) < 0.01, "Missing numeric value was not imputed with column mean"
    
    mean_val = np.mean(vals)
    std_val = np.std(vals)
    assert abs(mean_val) < 0.01, f"Standard scaling not applied: mean is {mean_val} (expected 0)"
    assert abs(std_val - 1.0) < 0.2, f"Standard scaling not applied: std is {std_val} (expected 1)"

    client.post('/api/v1/data/upload', json=[{"color": "red"}, {"color": "blue"}])
    resp2 = client.get('/api/v1/data/processed')
    cols = list(resp2.get_json()[0].keys())
    assert "color_red" in cols or "color_blue" in cols, "One-hot encoding failed"
    assert "color" not in cols, "Original categorical column must be dropped after one-hot encoding"

def test_m1_error_handling(client):
    """Verify HTTP 400 and HTTP 415 error handling for invalid input and unsupported content types."""
    assert client is not None
    
    # Test empty JSON body
    resp_empty_json = client.post('/api/v1/data/upload', json=[], content_type='application/json')
    assert resp_empty_json.status_code == 400

    # Test empty CSV body
    resp_empty_csv = client.post('/api/v1/data/upload', data="", content_type='text/csv')
    assert resp_empty_csv.status_code == 400

    # Malformed JSON with correct content type -> 400
    resp_bad = client.post('/api/v1/data/upload', data="not json", content_type='application/json')
    assert resp_bad.status_code == 400

    # Unsupported content type -> 415
    resp_xml = client.post('/api/v1/data/upload', data="<root/>", content_type='application/xml')
    assert resp_xml.status_code == 415
