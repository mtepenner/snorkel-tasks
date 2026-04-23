import os
import json
import subprocess

def test_milestone_1_anti_cheat():
    """Verify cleaned.json is dynamically regenerated with all 5 records and correct schema."""
    script_path = '/app/workspace/src/analyzer.py'
    output_path = '/app/workspace/data/cleaned.json'
    
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
        
    subprocess.run(['python3', script_path], check=False)
    assert os.path.exists(output_path), "Script did not generate cleaned.json when executed."
    
    with open(output_path, 'r') as f:
        data = json.load(f)
        
    assert isinstance(data, list), "Output should be a list of records."
    assert len(data) >= 5, "Expected at least 5 records after dynamic data injection. Agent hardcoded data."
    
    regions = {r.get("region") for r in data}
    assert {"North America", "Europe", "Asia"}.issubset(regions), "Region mapping failed for dynamic data."
    
    for rec in data:
        assert "temperature" in rec, "temperature field missing from record."
        assert "region" in rec, "region field missing from record."