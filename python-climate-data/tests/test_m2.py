import os
import json
import subprocess
import sys

def test_milestone_2_anti_cheat():
    """Verify trends.json dynamically calculates the correct mean temperature for filtered data."""
    script_path = '/app/workspace/src/analyzer.py'
    output_path = '/app/workspace/data/trends.json'
    csv_path = '/app/workspace/data/climate.csv'
    meta_path = '/app/workspace/data/metadata.json'

    # Option A – restore original CSV at the start of the test, so the assertion is always stable regardless of run order:
    original_csv = (
        "region_id,year,temperature\n"
        "1,2020,14.5\n"
        "1,2021,15.0\n"
        "2,2020,22.1\n"
        "2,2021,22.5\n"
    )
    with open(csv_path, 'w') as f:
        f.write(original_csv)
    with open(meta_path, 'w') as f:
        json.dump({"1": "North America", "2": "Europe"}, f)

    with open(csv_path, 'r') as f:
        csv_content = f.read()
    if '3,2021,30.0' not in csv_content:
        with open(csv_path, 'a') as f:
            f.write('3,2021,30.0\n')
    # Inject a second post-2021 row for North America to exercise true mean averaging.
    if '1,2022,17.0' not in csv_content:
        with open(csv_path, 'a') as f:
            f.write('1,2022,17.0\n')

    with open(meta_path, 'r') as f:
        meta = json.load(f)
    if "3" not in meta:
        meta["3"] = "Asia"
        with open(meta_path, 'w') as f:
            json.dump(meta, f)

    if os.path.exists(output_path):
        os.remove(output_path)

    subprocess.run([sys.executable, script_path], check=False)
    assert os.path.exists(output_path), "Script did not generate trends.json when executed."

    with open(output_path, 'r') as f:
        data = json.load(f)

    assert "Asia" in data, "Script does not process CSV dynamically (missing Asia key)."
    
    # 2020 Data is excluded. North America has two post-2021 rows (15.0, 17.0) → mean 16.0.
    assert abs(data["North America"] - 16.0) < 1e-9, "Incorrect average for North America. Expected mean(15.0, 17.0)=16.0. Did you filter out pre-2021 data and compute a true mean?"
    assert abs(data["Europe"] - 22.5) < 1e-9, "Incorrect average for Europe."
    assert abs(data["Asia"] - 30.0) < 1e-9, "Incorrect dynamic average for Asia."
