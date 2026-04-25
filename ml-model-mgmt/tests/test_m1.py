import numpy as np

def test_m1_upload_endpoint_exists(client):
    """1 pt: wire up a POST /api/v1/data/upload endpoint to swallow csv or json payloads."""
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
    """1 pt: handle missing values/scaling/encoding and GET /api/v1/data/processed spits out cleaned dataset."""
    assert client is not None
    client.post('/api/v1/data/upload', json=[{"A": 10}, {"A": None}, {"A": 30}])
    response = client.get('/api/v1/data/processed')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list) and len(data) == 3, "Processed data malformed"
    
    vals = [row["A"] for row in data]
    assert None not in vals, "Missing values not handled"
    
    mean_val = np.mean(vals)
    std_val = np.std(vals)
    assert abs(mean_val) < 0.01, f"Standard scaling not applied: mean is {mean_val} (expected 0)"
    assert abs(std_val - 1.0) < 0.2, f"Standard scaling not applied: std is {std_val} (expected 1)"

    client.post('/api/v1/data/upload', json=[{"color": "red"}, {"color": "blue"}])
    resp2 = client.get('/api/v1/data/processed')
    cols = list(resp2.get_json()[0].keys())
    assert "color_red" in cols or "color_blue" in cols, "One-hot encoding failed"

def test_m1_error_handling(client):
    """1 pt: throws a 400 for bad input."""
    assert client is not None
    response = client.post('/api/v1/data/upload', data="this is garbage text")
    assert response.status_code in [400, 415], "Did not handle bad input gracefully. Expected 4xx, not 5xx."
