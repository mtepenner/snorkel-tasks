# [SIM-88] Fluid Dynamics API (Java)

**Description:**
Need this quickly. The engineers are doing repeated manual flow checks whenever viscosity or inlet speed changes and there's way too much copy/paste math happening.

**Scope:**
* Keep it lightweight. We do NOT need a full CFD build here.
* Output MUST react dynamically to input changes (no canned/mock responses!).

**Technical AC:**
* **File location:** Java service MUST be at `/app/workspace/src/FluidDynamicsApi.java`
* **Bind:** `0.0.0.0:8080`
* **Endpoint:** `POST /simulate`
* **Request JSON payload keys:** `viscosity`, `inlet_velocity`, `grid_points`, `steps`

**Simulation Behavior for `/simulate`:**
* Run a lightweight numerical simulation.
* Return JSON with `velocity_profile` and `pressure_profile` across the grid.
* Both arrays MUST contain exactly `grid_points` number of values.
* Physics check: Pressure MUST drop along the pipe.
* Sanity check: Different inputs MUST produce genuinely different profiles.

Get this unblocked so the team can automate their checks. Thx.

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
