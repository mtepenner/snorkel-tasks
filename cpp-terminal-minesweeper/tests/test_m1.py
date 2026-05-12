import os
import subprocess

def test_m1_api_connected():
    assert os.path.exists("/app/workspace/src/client.cpp")
    
    res = subprocess.run(["g++", "/app/workspace/src/client.cpp", "-o", "/app/workspace/client", "-lcurl"], capture_output=True)
    assert res.returncode == 0, "C++ code failed to compile"
