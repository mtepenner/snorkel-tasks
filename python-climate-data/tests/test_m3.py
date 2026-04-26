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
            """Check that a node whose label contains `region` has a directed edge to a node whose label contains `temp_value`.

            Handles three DOT node-ID styles:
            1. Bare unquoted word:    north_america -> 16_00
            2. Quoted plain label:    "north america" -> "16.00"
            3. Quoted compound ID:    "region:north america" [label="north america"]; "mean:north america" [label="16.00"]
            """
            # Build a map: node_id_token -> label text
            # Captures both bare identifiers (\w+) and quoted strings ("...")
            node_labels = {}
            for m in re.finditer(
                r'("(?:[^"\\]|\\.)*"|\w+)\s*\[[^\]]*label\s*=\s*"([^"]*)"',
                dot
            ):
                node_labels[m.group(1).strip('"')] = m.group(2)

            # Also treat a bare quoted string used directly as a node ID (no attrs)
            # e.g.  "north america" -> "16.00"  — add them with label == id
            for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', dot):
                nid = m.group(1)
                if nid not in node_labels:
                    node_labels[nid] = nid

            region_nodes = {nid for nid, lbl in node_labels.items() if region in lbl}
            temp_nodes   = {nid for nid, lbl in node_labels.items() if temp_value in lbl}

            # Build the set of directed edges (src_token -> dst_token)
            edges = set()
            for m in re.finditer(
                r'("(?:[^"\\]|\\.)*"|\w+)\s*->\s*("(?:[^"\\]|\\.)*"|\w+)',
                dot
            ):
                edges.add((m.group(1).strip('"'), m.group(2).strip('"')))

            return any((rn, tn) in edges for rn in region_nodes for tn in temp_nodes)
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
