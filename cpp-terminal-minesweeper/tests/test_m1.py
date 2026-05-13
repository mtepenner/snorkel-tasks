import os
import subprocess


def test_m1_api_connected():
    # Milestone 1 must produce the client source file in the required path.
    assert os.path.exists("/app/workspace/src/client.cpp")

    # Compile the client with both curl and Magick++ support so one source file
    # can be used across all milestones.
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

    # Validate that the implementation references the expected board endpoint.
    with open("/app/workspace/src/client.cpp", "r", encoding="utf-8") as fh:
        source = fh.read()

    assert "http://localhost:8080/board" in source, (
        "client.cpp must fetch board state from http://localhost:8080/board"
    )

    # Runtime smoke test: the client should execute cleanly while the backend is up.
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
