we need a python script at `/app/workspace/src/analyzer.py` to crunch some climate data. the input files are `/app/workspace/data/climate.csv` and `/app/workspace/data/metadata.json` — read them dynamically, new regions get added occasionally so don't hardcode anything.

one rule that really matters: pre-2021 data is garbage, throw it out before doing any math.

three things need to come out of this, details in the milestone files but here's the gist:

- `cleaned.json` goes in `/app/workspace/data/` — list of dicts, one per record. each one needs `region` as a string, `year` as an int, `temperature` as a float. no 2020 or earlier rows.
- `trends.json` also in `/app/workspace/data/` — just a flat `{ region_name: mean_temp }` dict, floats for the values
- graphviz png at `/app/workspace/output/climate_graph.png`, directed graph with region nodes pointing at their mean temps. don't delete the .dot file after rendering, i need it
