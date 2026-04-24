we need a python script located at /app/workspace/src/analyzer.py to process our latest climate metrics. goal is a graphviz directed network with region nodes pointing to their calculated mean temperatures. big rule: skip any data from before 2021 -> if it's old, it's just noise and ruins the math.

deliverables include the following:
1. /app/workspace/data/cleaned.json -> this is a list of dictionaries where each record must include the mapped 'region' (string), 'year' (integer) and 'temperature' (float)
2. /app/workspace/data/trends.json -> this is a flat json directory mapping region names (string) to their mean temperature (float)
3. /app/workspace/output/climate_graph.png -> this is a directed graphviz graph where regions point to their respective mean temps. The script must retain the raw dot src file on disk, output/climate_graph.gv or similar, to allow inspection.
