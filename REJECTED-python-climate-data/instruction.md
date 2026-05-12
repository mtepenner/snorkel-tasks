# [DATA-942] climate data thing is still blocking the pipeline

Need a Python script at `/app/workspace/src/analyzer.py` fixed now. It has to read `/app/workspace/data/climate.csv` plus `/app/workspace/data/metadata.json`, map region names dynamically, and not hardcode any region IDs or labels because the ingestion mapping is not stable.

Anything before year 2021 is bad data. Do not let pre-2021 rows leak into cleaned output, averages, temperature nodes, graph labels, or graph edges.

## Phase 1

Write `/app/workspace/data/cleaned.json` as a JSON array of objects built strictly from post-2020 rows. Every object has to use exactly these keys and types: `"region"` as string, `"temperature"` as float, `"year"` as integer.

## Phase 2

Write `/app/workspace/data/trends.json` as one flat JSON object mapping each dynamic region name to its computed float mean temperature. No nested structure, no stringified numbers, no hardcoded region list.

## Phase 3

Write both `/app/workspace/output/climate_graph.gv` and `/app/workspace/output/climate_graph.png`. The graph has to be a directed Graphviz graph where each dynamic region points to its computed mean temperature based only on post-2020 data. Keep the mean temperature text intact in the raw DOT source; if you use the numeric mean as a DOT node ID, quote it so decimal values like `"22.5"` survive verbatim in the `.gv` file.

Keep it exact and do not add extra outputs. Need this unstuck today.
