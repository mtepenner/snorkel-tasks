import json
import math
import statistics
import subprocess
import time
from pathlib import Path

import requests

SERVER_PROCESS = None
BASE_URL = "http://127.0.0.1:8080"
SIMULATION_FILE = Path("/app/workspace/data/latest_simulation.json")
ANALYSIS_FILE = Path("/app/workspace/data/latest_analysis.json")


def wait_for_server():
    for _ in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                return
        except requests.RequestException:
            time.sleep(0.5)

    raise AssertionError("Java API did not become ready on port 8080")


def setup_module(module):
    java_file = Path("/app/workspace/src/FluidDynamicsApi.java")
    python_file = Path("/app/workspace/src/postprocess.py")
    assert java_file.exists(), "FluidDynamicsApi.java is missing"
    assert python_file.exists(), "postprocess.py is missing"

    subprocess.run(
        ["javac", "--add-modules", "jdk.httpserver", str(java_file)],
        check=True,
        cwd="/app/workspace/src",
    )

    global SERVER_PROCESS
    SERVER_PROCESS = subprocess.Popen(
        ["java", "--add-modules", "jdk.httpserver", "-cp", "/app/workspace/src", "FluidDynamicsApi"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    wait_for_server()


def teardown_module(module):
    global SERVER_PROCESS
    if SERVER_PROCESS is not None:
        SERVER_PROCESS.terminate()
        try:
            SERVER_PROCESS.wait(timeout=5)
        except subprocess.TimeoutExpired:
            SERVER_PROCESS.kill()


def run_simulation(payload):
    response = requests.post(f"{BASE_URL}/simulate", json=payload, timeout=5)
    assert response.status_code == 200, response.text
    return response.json()


def assert_close(left, right, tolerance=1e-6):
    assert math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance), f"{left} != {right}"


def assert_analysis_close(actual, expected):
    """Helper to safely compare analysis dictionaries with floating-point tolerance."""
    assert_close(actual["mean_velocity"], expected["mean_velocity"])
    assert_close(actual["velocity_stddev"], expected["velocity_stddev"])
    assert_close(actual["pressure_drop"], expected["pressure_drop"])
    assert actual["dominant_regime"] == expected["dominant_regime"]


def test_health_and_required_files():
    """Verify that the health endpoint returns status ok and both required source files exist."""
    response = requests.get(f"{BASE_URL}/health", timeout=3)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert Path("/app/workspace/src/FluidDynamicsApi.java").exists()
    assert Path("/app/workspace/src/postprocess.py").exists()


def test_simulation_response_and_saved_files():
    """Verify /simulate returns all required keys, correct array lengths, decreasing pressure and velocity profiles, and that both persistence files are written with matching content."""
    payload = {"viscosity": 0.12, "inlet_velocity": 2.4, "grid_points": 6, "steps": 4}
    data = run_simulation(payload)

    assert set(data.keys()) == {
        "viscosity",
        "inlet_velocity",
        "grid_points",
        "steps",
        "reynolds_number",
        "velocity_profile",
        "pressure_profile",
        "analysis",
    }
    assert data["grid_points"] == payload["grid_points"]
    assert data["steps"] == payload["steps"]
    assert len(data["velocity_profile"]) == payload["grid_points"]
    assert len(data["pressure_profile"]) == payload["grid_points"]
    assert data["velocity_profile"][0] > data["velocity_profile"][-1]
    assert all(
        data["pressure_profile"][index] >= data["pressure_profile"][index + 1]
        for index in range(len(data["pressure_profile"]) - 1)
    ), "pressure profile should decrease across the grid"

    assert SIMULATION_FILE.exists(), "latest_simulation.json was not written"
    assert ANALYSIS_FILE.exists(), "latest_analysis.json was not written"

    saved_simulation = json.loads(SIMULATION_FILE.read_text())
    saved_analysis = json.loads(ANALYSIS_FILE.read_text())
    assert saved_simulation["grid_points"] == payload["grid_points"]
    assert saved_simulation["velocity_profile"] == data["velocity_profile"]
    assert_analysis_close(saved_analysis, data["analysis"])


def test_python_postprocess_matches_api_analysis_and_latest_report():
    """Verify that running the postprocess.py script directly matches the analysis from the API, and that /latest-report serves it correctly."""
    payload = {"viscosity": 0.18, "inlet_velocity": 3.1, "grid_points": 7, "steps": 5}
    data = run_simulation(payload)

    helper = subprocess.run(
        ["python3", "/app/workspace/src/postprocess.py", str(SIMULATION_FILE)],
        check=True,
        text=True,
        capture_output=True,
    )
    helper_analysis = json.loads(helper.stdout.strip())

    assert_analysis_close(helper_analysis, data["analysis"])

    report_response = requests.get(f"{BASE_URL}/latest-report", timeout=3)
    assert report_response.status_code == 200
    assert_analysis_close(report_response.json(), helper_analysis)


def test_analysis_fields_are_consistent_with_profiles():
    """Verify that the computed analysis fields (mean, stddev, pressure drop, regime) mathematically match the generated simulation profiles."""
    payload = {"viscosity": 0.08, "inlet_velocity": 2.8, "grid_points": 8, "steps": 6}
    data = run_simulation(payload)

    velocity_profile = [float(value) for value in data["velocity_profile"]]
    pressure_profile = [float(value) for value in data["pressure_profile"]]
    analysis = data["analysis"]

    assert_close(analysis["mean_velocity"], statistics.mean(velocity_profile))
    assert_close(analysis["velocity_stddev"], statistics.pstdev(velocity_profile))
    assert_close(analysis["pressure_drop"], pressure_profile[0] - pressure_profile[-1])
    assert analysis["dominant_regime"] in {"laminar", "transitional", "turbulent"}


def test_inputs_change_the_simulation():
    """Verify that changing input parameters genuinely modifies the physics output, checking the inverse relationships between viscosity/inlet_velocity and Reynolds number."""
    # Viscosity sensitivity
    low_viscosity = run_simulation({"viscosity": 0.05, "inlet_velocity": 3.0, "grid_points": 6, "steps": 4})
    high_viscosity = run_simulation({"viscosity": 0.25, "inlet_velocity": 3.0, "grid_points": 6, "steps": 4})

    assert low_viscosity["reynolds_number"] > high_viscosity["reynolds_number"]
    assert low_viscosity["analysis"]["mean_velocity"] > high_viscosity["analysis"]["mean_velocity"]
    assert not math.isclose(low_viscosity["analysis"]["pressure_drop"], high_viscosity["analysis"]["pressure_drop"], rel_tol=1e-6, abs_tol=1e-6)

    # Inlet velocity sensitivity
    slow_velocity = run_simulation({"viscosity": 0.1, "inlet_velocity": 1.0, "grid_points": 6, "steps": 4})
    fast_velocity = run_simulation({"viscosity": 0.1, "inlet_velocity": 5.0, "grid_points": 6, "steps": 4})

    assert fast_velocity["reynolds_number"] > slow_velocity["reynolds_number"]
    assert fast_velocity["analysis"]["mean_velocity"] > slow_velocity["analysis"]["mean_velocity"]

    # Regime change check: ensure dominant_regime varies with Reynolds number
    very_low_re = run_simulation({"viscosity": 5.0, "inlet_velocity": 1.0, "grid_points": 6, "steps": 4})
    very_high_re = run_simulation({"viscosity": 0.01, "inlet_velocity": 5.0, "grid_points": 6, "steps": 4})
    assert very_low_re["analysis"]["dominant_regime"] != very_high_re["analysis"]["dominant_regime"], "dominant_regime must vary with Reynolds number"
