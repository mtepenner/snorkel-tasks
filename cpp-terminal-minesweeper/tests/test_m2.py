import os
import subprocess


def test_m2_deterministic_play():
    # Milestone 2 expects the compiled binary at this exact path.
    assert os.path.exists("/app/workspace/client"), "Client binary missing"

    # Use the documented scripted command protocol.
    scripted_input = "reveal 0 0\nquit\n"

    # First execution validates command handling and output behavior.
    process1 = subprocess.Popen(
        ["/app/workspace/client"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out1, err1 = process1.communicate(input=scripted_input, timeout=10)
    assert process1.returncode == 0, (
        "Client should exit cleanly after scripted reveal/quit commands.\n"
        f"stdout={out1}\n"
        f"stderr={err1}"
    )

    # Require observable terminal output so scripted play can be validated.
    assert out1.strip() != "", "Client produced no stdout for scripted play"
    assert (
        "reveal" in out1.lower()
        or "revealed" in out1.lower()
        or any(ch.isdigit() for ch in out1)
    ), "Client output does not reflect reveal command handling"

    # Second execution must be byte-for-byte identical for deterministic CI play.
    process2 = subprocess.Popen(
        ["/app/workspace/client"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out2, err2 = process2.communicate(input=scripted_input, timeout=10)
    assert process2.returncode == 0, (
        "Second deterministic run should also exit cleanly.\n"
        f"stdout={out2}\n"
        f"stderr={err2}"
    )
    assert out1 == out2, "Scripted play must be deterministic across repeated runs"
