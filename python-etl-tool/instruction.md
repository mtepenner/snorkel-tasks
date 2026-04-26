# [ETL-31] Build ETL Dashboard

**Description:**
Hey, I need a Python/Flask ETL web dashboard built out. Our data team is complaining they can't trigger the processing pipeline, monitor logs, or download results from their browser. Need this fixed ASAP.

## Backend
**AC:**
* Create `/app/workspace/src/app.py`; run the Flask app on host `0.0.0.0` at port `5000`.
* Read all `.csv` files from `/app/workspace/data/input/`.
  * MUST preserve all original columns.
  * Aggregate every row into `/app/workspace/data/output.json` as a JSON array (where each element is an object whose keys are the CSV column names and whose values are the string values).
* Insert each record into `/app/workspace/data/etl.db`. 
  * Schema MUST be exactly: `CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT)`
  * The `data` column has to store the JSON string for each row.
* Append a timestamped success or error entry to `/app/workspace/data/etl.log` on every ETL run.

**Endpoints:**
* `GET /` — serve the frontend dashboard (render `templates/index.html`).
* `POST /trigger` — run the ETL pipeline (read CSVs → write output.json → insert into DB → append to log).
* `GET /logs` — return the full contents of `/app/workspace/data/etl.log`.
* `GET /download` — serve `/app/workspace/data/output.json`.

## Frontend
**AC:**
* Place the UI exactly at `/app/workspace/src/templates/index.html`.
* Include a button that sends a `POST` request to `/trigger`.
  * **CRITICAL:** Use JS to disable the button while the request is running (`btn.disabled = true`), and re-enable it when it finishes. Otherwise, users span-click and we get concurrent runs. 
* Add a `<pre>` block that automatically fetches `/logs` and throws it on the screen **on page load** (use `window.onload` or a `DOMContentLoaded` event listener).
* Add a standard download link (`<a href="/download">`) for the output JSON file.

Please don't over-engineer this, just make sure it meets the requirements so tests don't break. Thx!
