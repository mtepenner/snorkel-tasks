import os
import subprocess

def test_milestone_3_anti_cheat_and_edges():
    """Verify the script generates a valid Graphviz PNG and contains correct edge construction logic."""
    script_path = '/app/workspace/src/analyzer.py'
    output_path = '/app/workspace/output/climate_graph.png'
    
    if os.path.exists(output_path):
        os.remove(output_path)
        
    subprocess.run(['python3', script_path], check=False)
    assert os.path.exists(output_path), "Script did not generate climate_graph.png."
    
    with open(script_path, 'r') as f:
        code = f.read()
    
    assert 'graphviz' in code, "Graphviz library was not used in the script."
    assert '.edge(' in code or '.edges(' in code, "Graph logic missing: Nodes must point to their means using edges."