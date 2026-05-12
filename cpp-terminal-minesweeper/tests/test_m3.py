import os
import subprocess
import glob

def test_m3_imagemagick_metadata():
    replays = glob.glob("/app/workspace/data/replays/*.png")
    assert len(replays) > 0, "No PNG replays found in /app/workspace/data/replays/"
    
    for replay in replays:
        result = subprocess.run(["identify", "-format", "%[Game-Metadata]", replay], capture_output=True, text=True)
        assert len(result.stdout.strip()) > 0, f"No metadata injected into {replay}"
