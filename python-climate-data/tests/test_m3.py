import os
import subprocess
import pytest

def test_milestone_3_anti_cheat_and_edges():
    script_path = '/app/workspace/src/analyzer.py'
    png_path = '/app/workspace/output/climate_graph.png'
    dot_path = '/app/workspace/output/climate_graph'
    csv_path = '/app/workspace/data/climate.csv'

    # Ensure clean state
    if os.path.exists(png_path):
        os.remove(png_path)

    subprocess.run(['/usr/local/bin/python3', script_path], check=False)
    
    assert os.path.exists(png_path), "PNG missing"
    
    # Check for DOT file (handle extensions)
    actual_dot = dot_path if os.path.exists(dot_path) else dot_path + '.gv'
    assert os.path.exists(actual_dot), "DOT source missing"
