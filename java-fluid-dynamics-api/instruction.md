# Fluid Dynamics API

Need this quickly.

Current pain:

- repeated manual flow checks whenever viscosity/inlet speed changes
- too much copy/paste math

Scope:

- keep lightweight
- no full CFD build
- output must react to input changes (no canned response behavior)

Implementation notes:

- Java service file: `/app/workspace/src/FluidDynamicsApi.java`
- bind: `0.0.0.0:8080`
- main endpoint: `POST /simulate`
- request JSON keys for `/simulate`: `viscosity`, `inlet_velocity`, `grid_points`, `steps`

Simulation behavior (`/simulate`):

- run lightweight numerical simulation
- return `velocity_profile` and `pressure_profile` across grid
- both arrays must contain exactly `grid_points` values
- pressure must drop along pipe
- different inputs must produce different profiles

Persistence:

- write raw simulation output on every run to `/app/workspace/data/latest_simulation.json`

Response contract (`/simulate`):

- required top-level keys:
  `viscosity`, `inlet_velocity`, `grid_points`, `steps`, `reynolds_number`, `velocity_profile`, `pressure_profile`, `analysis`

Post-processing split (Python):

- add `/app/workspace/src/postprocess.py`
- Java service calls script after each simulation
- script reads raw simulation JSON
- script computes: `mean_velocity`, `velocity_stddev`, `pressure_drop`, `dominant_regime`
- script writes analysis to `/app/workspace/data/latest_analysis.json`
- same analysis must be returned in API response under `analysis`

Extra endpoints:

- `GET /latest-report` returns saved analysis
- `GET /health` for harness readiness check
