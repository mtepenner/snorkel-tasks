import os
import json
import subprocess

def test_milestone_3_anti_cheat_and_edges():
    """Verify the script generates a valid Graphviz PNG and dynamic edge construction."""
    script_path = '/app/workspace/src/analyzer.py'
    png_path = '/app/workspace/output/climate_graph.png'
    dot_path = '/app/workspace/output/climate_graph'
    
    with open('/app/workspace/data/climate.csv', 'a') as f:
        f.write('3,2020,30.0\n')
    with open('/app/workspace/data/metadata.json', 'r') as f:
        meta = json.load(f)
    meta["3"] = "Asia"
    with open('/app/workspace/data/metadata.json', 'w') as f:
        json.dump(meta, f)
        
    if os.path.exists(png_path):
        os.remove(png_path)
        
    with open(script_path, 'r') as f:
        code = f.read()
    code = code.replace('cleanup=True', 'cleanup=False')
    with open(script_path, 'w') as f:
        f.write(code)
        
    subprocess.run(['/usr/local/bin/python3', script_path], check=False)
    assert os.path.exists(png_path), "Script did not generate climate_graph.png."
    

    if not os.path.exists(dot_path):
        dot_path += '.gv' 
        
    assert os.path.exists(dot_path), "Graphviz DOT source file was not preserved."
    
    with open(dot_path, 'r') as f:
        dot_src = f.read()
        
    assert 'North America' in dot_src, "Graph missing North America node."
    assert '14.75' in dot_src, "Graph missing North America mean."
    assert 'Europe' in dot_src, "Graph missing Europe node."
    assert '22.3' in dot_src or '22.30' in dot_src, "Graph missing Europe mean."
    assert 'Asia' in dot_src, "Graph missing dynamically injected Asia node. Agent hardcoded values!"
    assert '30.0' in dot_src or '30.00' in dot_src, "Graph missing dynamic Asia mean."