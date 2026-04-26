import os
import re
import json
import subprocess
import sys

def test_milestone_3_anti_cheat_and_edges():
    """Verify PNG and DOT source exist; check directed region->temp edges are present in the graph."""
    script_path = '/app/workspace/src/analyzer.py'
    png_path = '/app/workspace/output/climate_graph.png'
    dot_path = '/app/workspace/output/climate_graph.gv'
    csv_path = '/app/workspace/data/climate.csv'
    meta_path = '/app/workspace/data/metadata.json'

    # Anti-cheat data injection
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    if '3,2021,30.0' not in csv_content:
        with open(csv_path, 'a') as f:
            f.write('3,2021,30.0\n')
    # Inject a second post-2021 row for North America (same as test_m2) to verify consistent filtering.
    if '1,2022,17.0' not in csv_content:
        with open(csv_path, 'a') as f:
            f.write('1,2022,17.0\n')

    with open(meta_path, 'r') as f:
        meta = json.load(f)
    if "3" not in meta:
        meta["3"] = "Asia"
        with open(meta_path, 'w') as f:
            json.dump(meta, f)

    for path in (png_path, dot_path):
        if os.path.exists(path):
            os.remove(path)

    subprocess.run([sys.executable, script_path], check=False)
    
    assert os.path.exists(png_path), "PNG missing"
    assert os.path.getsize(png_path) > 100, "PNG too small to be valid"
    with open(png_path, 'rb') as f:
        header = f.read(8)
    assert header[:4] == b'\x89PNG', "File is not a valid PNG image"

    assert os.path.exists(dot_path), \
        "DOT source missing: instruction requires climate_graph.gv at /app/workspace/output/climate_graph.gv"

    with open(dot_path, 'r') as f:
        dot_src = f.read().lower()

    assert 'digraph' in dot_src, "DOT source must be a directed graph"
    assert '->' in dot_src, "No directed edges found in DOT source"

    def has_region_temp_edge(dot, region, temp_value):
        """Check that a node with `region` in its label has a directed edge to a node with `temp_value` in its label.

        Handles two DOT styles:
        - Quoted labels as node IDs: "north america" -> "16.00"
        - Symbolic node IDs with separate label attrs: n_region_north_america -> n_mean_north_america
        """
        # Method 1: label text used directly as node ID
        pat = re.escape(region) + r'[^;\n]*->[^;\n]*' + re.escape(temp_value)
        if re.search(pat, dot):
            return True
        # Method 2: symbolic node IDs — build label map then check edges
        node_labels = {}
        for m in re.finditer(r'(\w+)\s*\[[^\]]*label\s*=\s*"([^"]*)"', dot):
            node_labels[m.group(1)] = m.group(2)
        region_nodes = {nid for nid, lbl in node_labels.items() if region in lbl}
        temp_nodes   = {nid for nid, lbl in node_labels.items() if temp_value in lbl}
        for rn in region_nodes:
            for tn in temp_nodes:
                if re.search(re.escape(rn) + r'\s*->\s*' + re.escape(tn), dot):
                    return True
        return False

    # North America has two post-2021 rows (15.0, 17.0) → mean 16.0
    assert has_region_temp_edge(dot_src, 'north america', '16.0'), \
        "North America must have a directed edge to its mean temperature 16.0 (mean of 15.0 and 17.0)"
    assert has_region_temp_edge(dot_src, 'europe', '22.5'), \
        "Europe must have a directed edge to its mean temperature 22.5"
    assert has_region_temp_edge(dot_src, 'asia', '30.0'), \
        "Asia must have a directed edge to its mean temperature 30.0"

    # Pre-2021 rows must not affect graph edges. If pre-2021 data were included, the contaminated
    # means would be: North America=(14.5+15.0+17.0)/3≈15.5, Europe=(22.1+22.5)/2=22.3
    assert not has_region_temp_edge(dot_src, 'north america', '15.5'), \
        "Pre-2021 rows must not affect graph edges (North America contaminated mean 15.5 detected)"
    assert not has_region_temp_edge(dot_src, 'europe', '22.3'), \
        "Pre-2021 rows must not affect graph edges (Europe contaminated mean 22.3 detected)"
