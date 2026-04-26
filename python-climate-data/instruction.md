# [DATA-942] Climate Data Analyzer Script

**Context:**
We need a python script to crunch some climate data ASAP. The ingestion team is complaining about hardcoded regions, so this needs to be dynamic. 

**AC:**
* Script must live at `/app/workspace/src/analyzer.py`
* Inputs are `/app/workspace/data/climate.csv` and `/app/workspace/data/metadata.json`
* **CRITICAL:** If they add new regions to the CSV, the code shouldn't break. No hardcoding!
* **Filter Rule:** Anything before year 2021 is BAD DATA. Drop those rows entirely. Do not include them in outputs, averages, or graph nodes.

## Requirements & Output Specifications
All output files below must exclude pre-2021 records and apply the dynamic regions.

### 1. `cleaned.json`
* **Path:** `/app/workspace/data/cleaned.json`
* **Structure:** A JSON array of objects (one per record).
* **Fields & Types:**
  * `region`: Extracted region string from `metadata.json` (e.g. "North America").
  * `year`: The year from the CSV cast strictly as an integer.
  * `temperature`: The temperature value cast strictly as a float.

### 2. `trends.json`
* **Path:** `/app/workspace/data/trends.json`
* **Structure:** A single flat JSON object mapping the region text directly to its computed float average temperature: `{ "North America": 15.5, ... }`

### 3. `climate_graph.png` and `climate_graph.gv`
* **Paths:** `/app/workspace/output/climate_graph.png` and `/app/workspace/output/climate_graph.gv`
* **Structure:** A Graphviz directed graph.
* **Nodes & Edges:** Generate nodes for the regions and the mean temps. Establish directed edges pointing from the regions to their respective mean temperatures (e.g. `North America -> 15.5`).
* **Note:** Render the graph to the `.png` format, and explicitly retain the raw `.gv` dot source file on disk afterwards for manual test verifications.

Plz just get this working, the pipeline is blocked.
