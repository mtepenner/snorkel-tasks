import os
import re
import json
import subprocess
import sys

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

    subprocess.run([sys.executable, script_path], check=False)
    
    assert os.path.exists(png_path), "PNG missing"
    assert os.path.getsize(png_path) > 100, "PNG too small to be valid"
    with open(png_path, 'rb') as f:
        header = f.read(8)
    assert header[:4] == b'\x89PNG', "File is not a valid PNG image"

    actual_dot = dot_path if os.path.exists(dot_path) else dot_path + '.gv'
    assert os.path.exists(actual_dot), "DOT source missing"

    with open(actual_dot, 'r') as f:
        dot_src = f.read().lower()

    assert 'digraph' in dot_src, "DOT source must be a directed graph"
    assert '->' in dot_src, "No directed edges found in DOT source"

    def has_edge(dot, src, dst):
        pat = re.escape(src) + r'[^;]*->[^;]*' + re.escape(dst)
        return re.search(pat, dot) is not None

    assert has_edge(dot_src, 'north america', '15.0') or has_edge(dot_src, 'north america', '15.00'), \
        "North America must have a directed edge to its mean temperature 15.0"
    assert has_edge(dot_src, 'europe', '22.5') or has_edge(dot_src, 'europe', '22.50'), \
        "Europe must have a directed edge to its mean temperature 22.5"
    assert has_edge(dot_src, 'asia', '30.0') or has_edge(dot_src, 'asia', '30.00'), \
        "Asia must have a directed edge to its mean temperature 30.0"
