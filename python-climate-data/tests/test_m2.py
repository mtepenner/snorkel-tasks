import os
import json
import subprocess

def test_milestone_2_anti_cheat():
    """Verify trends.json dynamically calculates the correct mean temperature for filtered data."""
    script_path = '/app/workspace/src/analyzer.py'
    output_path = '/app/workspace/data/trends.json'
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

    subprocess.run(['/usr/local/bin/python3', script_path], check=False)
    assert os.path.exists(output_path), "Script did not generate trends.json when executed."

    with open(output_path, 'r') as f:
        data = json.load(f)

    assert "Asia" in data, "Script does not process CSV dynamically (missing Asia key)."
    
    # 2020 Data is excluded. New expected means:
    assert abs(data["North America"] - 15.0) < 1e-9, "Incorrect average for North America. Did you filter out pre-2021 data?"
    assert abs(data["Europe"] - 22.5) < 1e-9, "Incorrect average for Europe."
    assert abs(data["Asia"] - 30.0) < 1e-9, "Incorrect dynamic average for Asia."
