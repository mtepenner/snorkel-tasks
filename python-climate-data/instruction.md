we need a python script at `/app/workspace/src/analyzer.py` to crunch some climate data. the input files are `/app/workspace/data/climate.csv` and `/app/workspace/data/metadata.json`. the solution needs to keep working if those files include regions beyond the starter examples, so adding a new region should not require code changes.

one rule that really matters: anything before 2021 is invalid for this task. those rows cannot show up in outputs, and they cannot affect any averages or graph edges.

three things need to come out of this, details in the milestone files but here's the gist:

- `cleaned.json` goes in `/app/workspace/data/` — list of dicts, one per record. each one needs `region` as a string, `year` as an int, `temperature` as a float. no 2020 or earlier rows.
- `trends.json` also in `/app/workspace/data/` — just a flat `{ region_name: mean_temp }` dict, floats for the values
- graphviz png at `/app/workspace/output/climate_graph.png`, directed graph with region nodes pointing at their mean temps. keep the raw dot source file on disk after rendering because it gets checked too
