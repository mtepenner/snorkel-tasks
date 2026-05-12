import os
import subprocess

def test_m2_deterministic_play():
    assert os.path.exists("/app/workspace/client"), "Client binary missing"
    
    process = subprocess.Popen(["/app/workspace/client"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out, err = process.communicate(input="reveal 0 0\nquit\n")
    
    assert process.returncode == 0
