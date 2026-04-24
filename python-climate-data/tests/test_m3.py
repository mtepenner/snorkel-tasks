import os
import subprocess

def test_milestone_3_anti_cheat_and_edges():
    """Verify the script generates a valid Graphviz PNG and preserves the DOT source."""
    script_path = '/app/workspace/src/analyzer.py'
    png_path = '/app/workspace/output/climate_graph.png'
    dot_path = '/app/workspace/output/climate_graph'
    csv_path = '/app/workspace/data/climate.csv'
    meta_path = '/app/workspace/data/metadata.json'

    with open(csv_path, 'r') as f:
        csv_content = f.read()
    if '3,2021,30.0' not in csv_content:
        with open(csv_path, 'a') as f:
            f.write('3,2021,30.0\n')

    if os.path.exists(png_path):
        os.remove(png_path)

    subprocess.run(['/usr/local/bin/python3', script_path], check=False)
    assert os.path.exists(png_path), "Script did not generate climate_graph.png."

    if not os.path.exists(dot_path):
        dot_path += '.gv'

    assert os.path.exists(dot_path), "Graphviz DOT source file was not preserved. Agent ignored cleanup=False."

    with open(dot_path, 'r') as f:
        dot_src = f.read()

    assert 'North America' in dot_src, "Graph missing North America node."
    assert '15.0' in dot_src or '15.00' in dot_src, "Graph missing North America mean (must be filtered)."
    assert 'Asia' in dot_src, "Graph missing dynamically injected Asia node."
