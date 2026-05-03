# [SIM-88] Fluid Dynamics API (Java) — need this by EOD

yo we keep doing these pipe-flow calculations by hand every time someone tweaks viscosity or inlet speed and it's killing us, just automate it already

**Where to put it:** Single Java file at `/app/workspace/src/FluidDynamicsApi.java`. Compile with javac using `--add-modules jdk.httpserver` — no Maven, no Gradle, no external jars, standard JDK only. Bind to `0.0.0.0:8080`. Make sure `/app/workspace/data/` exists before any writes.

**POST /simulate**

Takes JSON body: `viscosity` (float), `inlet_velocity` (float), `grid_points` (int), `steps` (int).

Must return EXACTLY these top-level keys — no extras, no missing:
- `viscosity` — echo back what came in
- `inlet_velocity` — echo back what came in
- `grid_points` — echo back what came in
- `steps` — echo back what came in
- `reynolds_number` — Re = (inlet_velocity * grid_points) / viscosity (that's our simplified pipe model, don't swap in the standard textbook formula)
- `velocity_profile` — float array of length exactly `grid_points`, inlet value must be greater than outlet value
- `pressure_profile` — float array of length exactly `grid_points`, must be non-increasing (pressure drops along pipe, every element >= the next)
- `analysis` — sub-object with these exact field names:
  - `mean_velocity`: arithmetic mean of the full velocity_profile array
  - `velocity_stddev`: **population** standard deviation of velocity_profile (divide by N, NOT N-1)
  - `pressure_drop`: pressure_profile[0] minus pressure_profile[grid_points-1]
  - `dominant_regime`: `"laminar"` when Re < 50, `"transitional"` when Re is 50–149, `"turbulent"` when Re >= 150

The simulation must be physically reactive — a run with higher viscosity at the same inlet speed must produce a lower Reynolds number AND a lower mean_velocity compared to a lower-viscosity run. Same deal the other way: higher inlet_velocity must produce a higher Reynolds number AND higher mean_velocity.

**GET /health** → `{"status": "ok"}`

**GET /latest-report** → return the analysis sub-object saved from the last /simulate call

**Persistence (both files required after every /simulate):**
- `/app/workspace/data/latest_simulation.json` — the full 8-field response
- `/app/workspace/data/latest_analysis.json` — just the analysis sub-object

**Offline script:** also need `/app/workspace/src/postprocess.py`. Takes a simulation JSON file path as a CLI argument, reads it, computes the same `mean_velocity`, `velocity_stddev`, `pressure_drop`, and `dominant_regime` using the identical formulas, and prints the resulting JSON object to stdout. Output must match the API numerically for the same input data.

