import os
import subprocess
import glob
import time

def test_m1_api_connected():
    """Verify client.cpp compiles, connects to the board endpoint, and outputs parsed fields."""
    assert os.path.exists("/app/workspace/src/client.cpp")
    compile_result = subprocess.run(
        [
            "bash",
            "-lc",
            "g++ /app/workspace/src/client.cpp -o /app/workspace/client -lcurl $(Magick++-config --cxxflags --libs)",
        ],
        capture_output=True,
        text=True,
    )
    assert compile_result.returncode == 0, f"C++ code failed to compile:\n{compile_result.stderr}"
    
    run_result = subprocess.run(
        ["/app/workspace/client"],
        input="quit\n",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert run_result.returncode == 0, "Client binary failed to run."
    stdout_lower = run_result.stdout.lower()
    assert any(k in stdout_lower for k in ("ok", "hidden", "mines", "10")), "Client must use and print board data fields from API"

def test_m2_deterministic_play():
    """Verify client correctly parses stdin commands, stays alive until quit, makes POST requests, and is deterministic."""
    proc = subprocess.Popen(
        ["/app/workspace/client"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    proc.stdin.write("reveal 0 0\n")
    proc.stdin.flush()
    time.sleep(0.5)
    assert proc.poll() is None, "Process must stay alive until quit"
    
    proc.stdin.write("quit\n")
    proc.stdin.flush()
    out_a, err_a = proc.communicate(timeout=5)
    assert proc.returncode == 0
    
    assert "0" in out_a, "Output must echo the revealed coordinates"
    assert any(word in out_a.lower() for word in ["reveal", "cleared", "mine", "safe", "cell", "ok"]), "Output must contain a game-state keyword from reveal action"
    
    proc2 = subprocess.Popen(["/app/workspace/client"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out_b, err_b = proc2.communicate(input="reveal 1 1\nquit\n", timeout=5)
    assert out_a != out_b, "Output must vary with different coordinates"
    
    proc3 = subprocess.Popen(["/app/workspace/client"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out_c, err_c = proc3.communicate(input="reveal 0 0\nquit\n", timeout=5)
    assert out_a == out_c, "Scripted play must be deterministic"

    with open("/tmp/server.log", "r") as f:
        logs = f.read()
    assert "POST /move" in logs, "Client must make a POST request to /move when processing a reveal command"

def test_m3_imagemagick_metadata():
    """Verify client generates distinct PNG replays with distinct metadata and sufficient visual complexity."""
    subprocess.run(
        ["/app/workspace/client"],
        input="reveal 0 0\nreveal 2 2\nquit\n",
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    replays = glob.glob("/app/workspace/data/replays/*.png")
    assert len(replays) >= 2, "Expected multiple replay frames"
    
    all_meta = set()
    for replay in replays:
        dim = subprocess.run(["identify", "-format", "%wx%h", replay], capture_output=True, text=True)
        assert dim.returncode == 0
        width, height = [int(v) for v in dim.stdout.strip().split("x")]
        assert width >= 16 and height >= 16, f"Replay image too small: {width}x{height}"
        
        colors_result = subprocess.run(["identify", "-format", "%k", replay], capture_output=True, text=True)
        num_colors = int(colors_result.stdout.strip())
        assert num_colors >= 3, f"Replay {replay} has only {num_colors} color(s); expected a visual board representation"
        
        meta_result = subprocess.run(["identify", "-format", "%[Game-Metadata]", replay], capture_output=True, text=True)
        meta = meta_result.stdout.strip()
        assert meta != "", f"No metadata injected into {replay}"
        assert any(token in meta.lower() for token in ["board", "move", "mine", "status"]), "Metadata is present but not informative"
        all_meta.add(meta)
        
    assert len(all_meta) > 1, "All replays have identical metadata"
