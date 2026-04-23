import os
import json
import subprocess

def test_milestone_2_anti_cheat():
    """Verify trends.json calculates the correct mean temperature for all regions."""
    script_path = '/app/workspace/src/analyzer.py'
    output_path = '/app/workspace/data/trends.json'
    
    if os.path.exists(output_path):
        os.remove(output_path)
        
    subprocess.run(['python3', script_path], check=False)
    assert os.path.exists(output_path), "Script did not generate trends.json when executed."
    
    with open(output_path, 'r') as f:
        data = json.load(f)
        
    assert isinstance(data, dict), "Output should be a key-value dictionary."
    assert "North America" in data, "Missing North America key."
    assert abs(data["North America"] - 14.75) < 1e-9, "Incorrect average calculation for North America."
    assert "Europe" in data, "Missing Europe key."
    assert abs(data["Europe"] - 22.3) < 1e-9, "Incorrect average calculation for Europe."