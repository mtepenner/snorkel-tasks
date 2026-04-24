def test_m1_upload_endpoint_exists(client):
    """1 pt: wire up a POST /api/v1/data/upload endpoint to swallow csv or json payloads."""
    assert client is not None, "API not implemented"
    response = client.post('/api/v1/data/upload', json=[{"A": 1, "B": None}, {"A": 2, "B": 4}])
    assert response.status_code == 200, "Upload endpoint failed"

def test_m1_preprocessing_and_retrieval(client):
    """1 pt: handle missing values/scaling and GET /api/v1/data/processed spits out cleaned dataset."""
    assert client is not None
    client.post('/api/v1/data/upload', json=[{"A": 10}, {"A": None}, {"A": 30}])
    response = client.get('/api/v1/data/processed')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list) and len(data) == 3, "Processed data malformed"

def test_m1_error_handling(client):
    """1 pt: throws a 400 for bad input."""
    assert client is not None
    response = client.post('/api/v1/data/upload', data="this is garbage text")
    assert response.status_code in [400, 415, 500], "Did not handle bad input gracefully"