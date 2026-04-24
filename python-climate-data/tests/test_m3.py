import os
import json
import subprocess

def test_milestone_3_anti_cheat_and_edges():
    """Verify PNG and DOT source exist; check directed region->temp edges are present in the graph."""
    script_path = '/app/workspace/src/analyzer.py'
    png_path = '/app/workspace/output/climate_graph.png'
    dot_path = '/app/workspace/output/climate_graph'
    csv_path = '/app/workspace/data/climate.csv'
    meta_path = '/app/workspace/data/metadata.json'

    # Anti-cheat data injection
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

    if os.path.exists(png_path):
        os.remove(png_path)

    subprocess.run(['/usr/local/bin/python3', script_path], check=False)
    
    assert os.path.exists(png_path), "PNG missing"
    assert os.path.getsize(png_path) > 100, "PNG too small to be valid"
    
    actual_dot = dot_path if os.path.exists(dot_path) else dot_path + '.gv'
    assert os.path.exists(actual_dot), "DOT source missing"

    with open(actual_dot, 'r') as f:
        dot_src = f.read().lower()

    assert 'digraph' in dot_src, "DOT source must be a directed graph"
    assert '->' in dot_src, "No directed edges found in DOT source"
    
    assert 'north america' in dot_src, "Missing North America region node"
    assert 'europe' in dot_src, "Missing Europe region node"
    assert 'asia' in dot_src, "Missing dynamically injected Asia region node"
    
    assert '15.0' in dot_src or '15.00' in dot_src, "Mean temp node missing for North America"
    assert '22.5' in dot_src or '22.50' in dot_src, "Mean temp node missing for Europe"
    assert '30.0' in dot_src or '30.00' in dot_src, "Mean temp node missing for Asia"
