# Fluid Dynamics API

i need a small service for quick fluid-flow experiments. this does not need to be a research-grade cfd package, but it should feel like a real simulation pipeline and it needs to react to the inputs instead of returning canned numbers.

put the java api in /app/workspace/src/FluidDynamicsApi.java and bind it to 0.0.0.0:8080. add a POST /simulate endpoint that accepts json with viscosity, inlet_velocity, grid_points, and steps. use those values to run a lightweight numerical fluid simulation so you end up with both a velocity profile and a pressure profile across the grid. both arrays need to have exactly grid_points entries, pressure should drop across the pipe, and changing the request values should change the output.

every run should write the raw simulation result to /app/workspace/data/latest_simulation.json. the response from /simulate needs to be a json object with these top-level keys: viscosity, inlet_velocity, grid_points, steps, reynolds_number, velocity_profile, pressure_profile, and analysis.

i also want the post-processing split out into python. create /app/workspace/src/postprocess.py and have the java service call it after each simulation. that helper should read the raw simulation json and compute mean_velocity, velocity_stddev, pressure_drop, and dominant_regime. save that analysis to /app/workspace/data/latest_analysis.json and return it from the api inside the analysis field.

last thing: add GET /latest-report so i can fetch the saved analysis json later, and GET /health so the harness can tell when the server is up.
