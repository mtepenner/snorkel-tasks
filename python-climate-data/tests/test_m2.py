import os
import json
import subprocess

def test_milestone_2_anti_cheat():
    """Verify trends.json dynamically calculates the correct mean temperature for all regions."""
    script_path = '/app/workspace/src/analyzer.py'
    output_path = '/app/workspace/data/trends.json'
    
    # Anti-cheat: Inject new dynamic data to prevent hardcoding
    with open('/app/workspace/data/climate.csv', 'a') as f:
        f.write('3,2020,30.0\n')
    
    with open('/app/workspace/data/metadata.json', 'r') as f:
        meta = json.load(f)
    meta["3"] = "Asia"
    with open('/app/workspace/data/metadata.json', 'w') as f:
        json.dump(meta, f)
        
    if os.path.exists(output_path):
        os.remove(output_path)
        
    subprocess.run(['/usr/local/bin/python3', script_path], check=False)
    assert os.path.exists(output_path), "Script did not generate trends.json when executed."
    
    with open(output_path, 'r') as f:
        data = json.load(f)
        
    assert isinstance(data, dict), "Output should be a key-value dictionary."
    assert "North America" in data, "Missing North America key."
    assert "Europe" in data, "Missing Europe key."
    assert "Asia" in data, "Script does not process CSV dynamically (missing Asia key)."
    
    assert abs(data["North America"] - 14.75) < 1e-9, "Incorrect average for North America."
    assert abs(data["Europe"] - 22.3) < 1e-9, "Incorrect average for Europe."
    assert abs(data["Asia"] - 30.0) < 1e-9, "Incorrect dynamic average for Asia."