import os
import subprocess


def test_m2_deterministic_play():
    assert os.path.exists("/app/workspace/client"), "Client binary missing"
    scripted_input = "reveal 0 0\nquit\n"
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
    assert out1.strip() != "", "Client produced no stdout for scripted play"
    assert (
        "reveal" in out1.lower()
        or "revealed" in out1.lower()
        or any(ch.isdigit() for ch in out1)
    ), "Client output does not reflect reveal command handling"
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
