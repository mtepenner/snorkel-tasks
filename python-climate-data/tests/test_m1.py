import os
import json
import subprocess
import sys

def test_milestone_1_anti_cheat():
    """Verify cleaned.json is dynamically regenerated with correct schema, types, and filters."""
    script_path = '/app/workspace/src/analyzer.py'
    output_path = '/app/workspace/data/cleaned.json'
    csv_path = '/app/workspace/data/climate.csv'
    meta_path = '/app/workspace/data/metadata.json'

    with open(csv_path, 'r') as f:
        csv_content = f.read()
    if '3,2021,30.0' not in csv_content:
        with open(csv_path, 'a') as f:
            f.write('3,2021,30.0\n')

    with open(meta_path, 'r') as f:
        meta = json.load(f)
    if "3" not in meta:
        meta["3"] = "Asia"
        with open(meta_path, 'w') as f:
            json.dump(meta, f)

    if os.path.exists(output_path):
        os.remove(output_path)

    subprocess.run([sys.executable, script_path], check=False)
    assert os.path.exists(output_path), "Script did not generate cleaned.json when executed."

    with open(output_path, 'r') as f:
        data = json.load(f)

    assert isinstance(data, list), "Output should be a list of records."
    assert len(data) == 3, "Expected exactly 3 filtered records after dynamic data injection."

    regions = {r.get("region") for r in data}
    assert {"North America", "Europe", "Asia"}.issubset(regions), "Region mapping failed for dynamic data."

    expected_temps = {"North America": 15.0, "Europe": 22.5, "Asia": 30.0}

    for rec in data:
        assert "region" in rec, "region field missing."
        assert "temperature" in rec, "temperature field missing."
        assert "year" in rec, "year field missing."
        
        assert isinstance(rec["region"], str), "region must be a string"
        assert isinstance(rec["year"], int), "year must be an integer"
        assert isinstance(rec["temperature"], float), "temperature must be a float"
        assert rec["year"] >= 2021, "Failed to filter out records before 2021!"

        region = rec["region"]
        assert region in expected_temps, f"Unexpected region: {region}"
        assert abs(rec["temperature"] - expected_temps[region]) < 1e-9, \
            f"Wrong temperature for {region}: expected {expected_temps[region]}, got {rec['temperature']}"
