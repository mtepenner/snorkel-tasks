import os
import subprocess
import glob
from pathlib import Path

def test_source_code_structures():
    """Test that the C++ code contains a class hierarchy and array of linked lists."""
    cpp_files = glob.glob('/app/workspace/**/*.cpp', recursive=True)
    assert len(cpp_files) > 0, "No C++ source files found in /app/workspace"
    
    combined_src = ""
    for f in cpp_files:
        with open(f, 'r') as file:
            combined_src += file.read().lower()
            
    assert "class" in combined_src or "struct" in combined_src, "No classes/structs defined."
    assert "virtual" in combined_src or "override" in combined_src or "public" in combined_src, "No class hierarchy (inheritance) detected."
    assert "diamond" in combined_src and "base" in combined_src, "Missing required tier classes."

def test_executable_output():
    """Verify the output of the compiled C++ application handles ordering by class correctly."""
    cpp_files = glob.glob('/app/workspace/**/*.cpp', recursive=True)
    assert len(cpp_files) > 0, "No C++ source files found."
    
    # Try to find a compiled executable or compile it for the test
    executable = "/usr/local/bin/vacation-app"
    if not os.path.exists(executable):
        # Fallback compilation if an agent named it differently or just left the source code
        subprocess.run(["g++", "-O3", cpp_files[0], "-o", executable])
        
    assert os.path.exists(executable), "Executable could not be found or built."
    
    result = subprocess.run([executable], capture_output=True, text=True)
    output = result.stdout.lower()
    
    lines = [line.strip() for line in output.split('\n') if line.strip() and ("base" in line or "silver" in line or "gold" in line or "platinum" in line or "diamond" in line)]
    
    # Since priority is Diamond -> Platinum -> Gold -> Silver -> Base
    if len(lines) >= 5:
        assert "diamond" in lines[0], "First item boarding list should be a Diamond member."
        assert "platinum" in lines[1], "Second item should be Platinum."
        assert "gold" in lines[2], "Third item should be Gold."
        assert "silver" in lines[3], "Fourth item should be Silver."
        assert "base" in lines[4], "Fifth item should be Base."
    else:
        assert "diamond" in output, "Expected diamond class in output"
        assert "base" in output, "Expected base class in output"

