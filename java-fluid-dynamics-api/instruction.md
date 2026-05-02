# [SIM-88] Fluid Dynamics API (Java)

**Description:**
Need this quickly. The engineers are doing repeated manual flow checks whenever viscosity or inlet speed changes and we need to automate it. 

**System Architecture:**
The system must consist of a Java HTTP service (`/app/workspace/src/FluidDynamicsApi.java`) bound to `0.0.0.0:8080`. 

**Endpoint: POST /simulate**
Accepts a JSON payload with `viscosity`, `inlet_velocity`, `grid_points`, and `steps`.
The endpoint must return a JSON response with the following observable behaviors:
* The JSON response must contain exactly these top-level fields: `viscosity` (echoed from request), `inlet_velocity` (echoed from request), `grid_points` (echoed from request), `steps` (echoed from request), `reynolds_number`, `velocity_profile`, `pressure_profile`, and `analysis`.
* Includes `velocity_profile` and `pressure_profile` arrays (length must be exactly `grid_points`) that satisfy basic physical laws: pressure must drop along the pipe, and velocity must be higher at the inlet than at the outlet.
* Includes a `reynolds_number` field. The system must dynamically react to inputs: e.g., a higher input viscosity must produce a lower Reynolds number and lower mean velocity.
* Includes an `analysis` object with these exact computed fields: `mean_velocity`, `velocity_stddev` (population standard deviation using all grid points), `pressure_drop`, and `dominant_regime` (must evaluate to exactly `"laminar"`, `"transitional"`, or `"turbulent"` based on the Reynolds number).

**Offline Analysis Script:**
We have legacy CLI tools that need to run the math offline, so we also need a standalone Python script at `/app/workspace/src/postprocess.py`. It must accept the path to a raw simulation JSON file as a CLI argument, compute the exact same `analysis` fields mentioned above, and print the resulting JSON object to `stdout`. 

**Persistence & Extra Endpoints:**
* `POST /simulate` must write its raw simulation output to `/app/workspace/data/latest_simulation.json` and its analysis object to `/app/workspace/data/latest_analysis.json`.
* `GET /latest-report` must return the saved analysis JSON.
* `GET /health` must return `{"status": "ok"}` for the harness readiness check.
