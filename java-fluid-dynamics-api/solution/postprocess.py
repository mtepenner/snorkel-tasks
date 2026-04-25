import json
import math
import sys
from pathlib import Path


def rounded(value: float) -> float:
    return round(float(value), 6)


def dominant_regime(reynolds_number: float) -> str:
    if reynolds_number < 50:
        return "laminar"
    if reynolds_number < 150:
        return "transitional"
    return "turbulent"


def build_analysis(simulation: dict) -> dict:
    velocity_profile = [float(value) for value in simulation["velocity_profile"]]
    pressure_profile = [float(value) for value in simulation["pressure_profile"]]
    mean_velocity = sum(velocity_profile) / len(velocity_profile)
    variance = sum((value - mean_velocity) ** 2 for value in velocity_profile) / len(velocity_profile)
    pressure_drop = pressure_profile[0] - pressure_profile[-1]

    return {
        "mean_velocity": rounded(mean_velocity),
        "velocity_stddev": rounded(math.sqrt(variance)),
        "pressure_drop": rounded(pressure_drop),
        "dominant_regime": dominant_regime(float(simulation["reynolds_number"])),
    }


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: postprocess.py <simulation-json> [output-json]")

    simulation_path = Path(sys.argv[1])
    analysis = build_analysis(json.loads(simulation_path.read_text()))
    encoded = json.dumps(analysis)

    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(encoded)

    print(encoded)


if __name__ == "__main__":
    main()