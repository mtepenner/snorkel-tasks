import os
import subprocess
import glob
import re

def test_source_code_structures():
    """Test that the C++ code contains a class hierarchy."""
    cpp_files = glob.glob('/app/workspace/**/*.cpp', recursive=True)
    assert len(cpp_files) > 0, "No C++ source files found in /app/workspace"
    
    combined_src = ""
    for f in cpp_files:
        with open(f, 'r', encoding='utf-8') as file:
            combined_src += file.read().lower()
            
    assert "class" in combined_src or "struct" in combined_src, "No classes/structs defined."
    
    for tier in ["base", "silver", "gold", "platinum", "diamond"]:
        assert re.search(rf'class\s+\w*{tier}\w*\s*:', combined_src) or \
               re.search(rf'struct\s+\w*{tier}\w*\s*:', combined_src), \
            f"Missing derived class definition for {tier} tier"

    assert combined_src.count("public") >= 4 or combined_src.count("virtual") >= 1, "Missing proper class inheritance structure."
    
    assert "next" in combined_src or "->" in combined_src, "No linked list pointer/node traversal detected"
    assert "week" in combined_src, "No vacation week concept found"

def test_executable_output():
    """Verify the output of the compiled C++ application handles ordering by class correctly."""
    cpp_files = glob.glob('/app/workspace/**/*.cpp', recursive=True)
    assert len(cpp_files) > 0, "No C++ source files found."
    
    # Try to find a compiled executable or compile it for the test
    executable = "/usr/local/bin/vacation-app"
    if not os.path.exists(executable):
        # Fallback compilation if an agent named it differently or just left the source code
        compile_cmd = ["g++", "-O3"] + cpp_files + ["-o", executable]
        subprocess.run(compile_cmd, check=True)
        
    assert os.path.exists(executable), "Executable could not be found or built."

    test_input = "ADD 1 Gold Charlie\nADD 1 Diamond Alice\nADD 1 Platinum Bob\nADD 1 Silver Dave\nADD 1 Base Eve\nPRINT 1\nADD 2 Base Zebra\nADD 2 Diamond Yack\nPRINT 2\n"
    
    try:
        result = subprocess.run([executable], input=test_input, capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        assert False, "Program timed out reading input. Does it have an input loop?"
    output = result.stdout.lower()
    
    lines = [line.strip() for line in output.split('\n') if line.strip() and ("base" in line or "silver" in line or "gold" in line or "platinum" in line or "diamond" in line or "week" in line) and not line.startswith("add ") and not line.startswith("print ")]
    
    # Check Week 1 output
    week1_idx = -1
    for i, line in enumerate(lines):
        if "week 1" in line:
            week1_idx = i
            break
    assert week1_idx >= 0, f"Could not find Week 1 output header in lines: {lines}"
    
    assert "diamond" in lines[week1_idx+1] and "alice" in lines[week1_idx+1], "First item boarding list should be a Diamond member (Alice)."
    assert "platinum" in lines[week1_idx+2] and "bob" in lines[week1_idx+2], "Second item should be Platinum (Bob)."
    assert "gold" in lines[week1_idx+3] and "charlie" in lines[week1_idx+3], "Third item should be Gold (Charlie)."
    assert "silver" in lines[week1_idx+4] and "dave" in lines[week1_idx+4], "Fourth item should be Silver (Dave)."
    assert "base" in lines[week1_idx+5] and "eve" in lines[week1_idx+5], "Fifth item should be Base (Eve)."

    # Check Week 2 output
    week2_idx = -1
    for i, line in enumerate(lines[week1_idx+6:]):
        if "week 2" in line:
            week2_idx = i + week1_idx + 6
            break
    assert week2_idx >= 0, "Could not find Week 2 output header"
    
    assert "diamond" in lines[week2_idx+1] and "yack" in lines[week2_idx+1], "First item boarding list for Week 2 should be a Diamond member (Yack)."
    assert "base" in lines[week2_idx+2] and "zebra" in lines[week2_idx+2], "Second item for Week 2 should be Base (Zebra)."