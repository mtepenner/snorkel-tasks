# ETL Dashboard

Build a Python/Flask ETL web dashboard that lets the data team trigger a processing pipeline, monitor logs, and download results — all from a browser.

## Backend

- Create `/app/workspace/src/app.py`; run the Flask app on host `0.0.0.0` at port `5000`.
- Read all `.csv` files from `/app/workspace/data/input/`, preserve all original columns, and aggregate every row into `/app/workspace/data/output.json` as a JSON array where each element is an object whose keys are the CSV column names and whose values are the corresponding string values, e.g.:
  ```json
  [
    {"col1": "val1", "col2": "val2", "col3": "val3"},
    {"col1": "val4", "col2": "val5", "col3": "val6"}
  ]
  ```
- Insert each record into `/app/workspace/data/etl.db` using the exact schema:
  ```sql
  CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT)
  ```
  The `data` column must store the JSON string for each row.
- Append a timestamped success or error entry to `/app/workspace/data/etl.log` on every ETL run.

## Endpoints

- `POST /trigger` — run the ETL pipeline (read CSVs → write output.json → insert into DB → append to log).
- `GET /logs` — return the full contents of `/app/workspace/data/etl.log`.
- `GET /download` — serve `/app/workspace/data/output.json`.

## Frontend

- Place the UI at `/app/workspace/src/templates/index.html`.
- Include a button that sends a `POST` request to `/trigger`.
  - Use JavaScript to **disable** the button while the request is in flight (set `btn.disabled = true`) and **re-enable** it (`btn.disabled = false`) once the response is received, to prevent concurrent ETL runs.
- Include a `<pre>` block that automatically fetches `/logs` and displays the log content **on page load** (use `window.onload` or a `DOMContentLoaded` event listener).
- Include a standard download link (`<a href="/download">`) for the output JSON file.
