# [DATA-942] Climate Data Analyzer Script

We need a python script to crunch some climate data at `/app/workspace/src/analyzer.py` ASAP. The ingestion team requires the regions to map dynamically, so do not hardcode them. We also have a strict filtering rule: anything before year 2021 is considered bad data and must be completely excluded from outputs, averages, and graph nodes.

## Deliverables
The python script must ingest `/app/workspace/data/climate.csv` alongside the mappings in `/app/workspace/data/metadata.json` and generate the following outputs automatically based strictly on post-2020 valid data:

1. **/app/workspace/data/cleaned.json**: A dynamically mapped JSON array containing the cleaned records where each object must use exactly the keys `"region"` (string), `"temperature"` (float), and `"year"` (integer).
2. **/app/workspace/data/trends.json**: A single flat JSON object mapping each region text to its computed float average temperature.
3. **/app/workspace/output/climate_graph.png**: A rendered Graphviz directed graph illustrating the regions generating directed edges pointing to their calculated mean temperatures, alongside the raw `climate_graph.gv` dot source file on disk.

Plz just get this working, the pipeline is blocked.
