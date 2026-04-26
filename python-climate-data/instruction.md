# [DATA-942] Climate Data Analyzer Script

**Context:**
We need a python script to crunch some climate data ASAP. The ingestion team is complaining about hardcoded regions, so this needs to be dynamic. 

**AC:**
* Script must live at `/app/workspace/src/analyzer.py`
* Inputs are `/app/workspace/data/climate.csv` and `/app/workspace/data/metadata.json`
* **CRITICAL:** If they add new regions to the CSV, the code shouldn't break. No hardcoding!
* **Filter Rule:** Anything before year 2021 is BAD DATA. Drop those rows entirely. Do not include them in outputs, averages, or graph nodes.

**Outputs required (see milestone files for deep dive, but here's the TL;DR):**
1. `cleaned.json` goes to `/app/workspace/data/`: List of dicts (one per record). Keys needed: `region` (str), `year` (int), `temperature` (float). Again, NO 2020 OR EARLIER.
2. `trends.json` goes to `/app/workspace/data/`: Flat dict of `{ region_name: mean_temp }`. Values must be floats.
3. `climate_graph.png` goes to `/app/workspace/output/`: A Graphviz directed graph. Nodes = regions, pointing at their mean temps. 
   *(Note: Keep the raw `.gv` dot source file at `/app/workspace/output/climate_graph.gv` on disk after rendering, the test suite checks for it).*

Plz just get this working, the pipeline is blocked.
