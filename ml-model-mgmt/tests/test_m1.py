import numpy as np


def _binary_indicator_columns(rows, exclude=None):
    exclude = set(exclude or [])
    if not rows:
        return []
    return [
        key
        for key in rows[0]
        if key not in exclude and all(row[key] in (0, 1) for row in rows)
    ]

def test_m1_upload_endpoint_exists(client):
    """POST /api/v1/data/upload accepts JSON arrays and applies the full preprocessing pipeline to CSV uploads."""
    assert client is not None, "API not implemented"
    response = client.post('/api/v1/data/upload', json=[{"A": 1, "B": None}, {"A": 2, "B": 4}])
    assert response.status_code == 200, "JSON Upload endpoint failed"
    
    csv_data = "X,Y,color\n1,,red\n2,4,blue\n100,6,red\n"
    response_csv = client.post('/api/v1/data/upload', data=csv_data, content_type='text/csv')
    assert response_csv.status_code == 200, "CSV Upload endpoint failed"
    processed = client.get('/api/v1/data/processed').get_json()
    assert len(processed) == 3
    assert "Y" in processed[0], "CSV numeric column 'Y' not preserved in processed rows"
    assert None not in [row["Y"] for row in processed], "Missing CSV numeric values were not imputed"
    assert abs(processed[0]["Y"]) < 0.01, "CSV upload did not apply mean imputation before scaling"
    assert abs(np.mean([row["Y"] for row in processed])) < 0.1, "CSV upload did not apply z-score scaling"
    assert "color" not in processed[0], "Original CSV categorical column must be dropped after encoding"
    csv_indicator_cols = _binary_indicator_columns(processed, exclude={"X", "Y"})
    assert len(csv_indicator_cols) >= 2, "CSV upload did not apply one-hot encoding"
    for row in processed:
        assert sum(row[column] for column in csv_indicator_cols) == 1, \
            "CSV one-hot encoded columns must be mutually exclusive"

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
    rows2 = resp2.get_json()
    assert "color" not in rows2[0], \
        "Original categorical column must be dropped after one-hot encoding"
    indicator_cols = _binary_indicator_columns(rows2)
    assert len(indicator_cols) >= 2, \
        "One-hot encoding must produce at least two binary indicator columns"
    for row in rows2:
        assert sum(row[column] for column in indicator_cols) == 1, \
            "One-hot columns must be mutually exclusive (exactly one column should be 1 per row)"

def test_m1_error_handling(client):
    """Verify malformed or unsupported uploads fail gracefully with non-500 responses."""
    assert client is not None

    cases = [
        ("empty json", {"json": [], "content_type": 'application/json'}, 400),
        ("empty csv", {"data": "", "content_type": 'text/csv'}, 400),
        ("malformed json", {"data": "not json", "content_type": 'application/json'}, 400),
        ("headerless csv", {"data": "1,2\n3,4\n", "content_type": 'text/csv'}, 400),
        ("unsupported xml", {"data": "<root/>", "content_type": 'application/xml'}, 415),
    ]

    for label, kwargs, expected_status in cases:
        response = client.post('/api/v1/data/upload', **kwargs)
        assert response.status_code == expected_status, f"Unexpected status for {label}"
        assert response.status_code < 500, f"{label} should not raise a 500 error"
