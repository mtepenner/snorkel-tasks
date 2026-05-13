import os
import subprocess


def test_m1_api_connected():
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
    assert compile_result.returncode == 0, (
        "C++ code failed to compile:\n"
        f"stdout={compile_result.stdout}\n"
        f"stderr={compile_result.stderr}"
    )
    with open("/app/workspace/src/client.cpp", "r", encoding="utf-8") as fh:
        source = fh.read()

    assert "http://localhost:8080/board" in source, (
        "client.cpp must fetch board state from http://localhost:8080/board"
    )
    run_result = subprocess.run(
        ["/app/workspace/client"],
        input="quit\n",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert run_result.returncode == 0, (
        "Client binary failed to run against the local backend.\n"
        f"stdout={run_result.stdout}\n"
        f"stderr={run_result.stderr}"
    )
