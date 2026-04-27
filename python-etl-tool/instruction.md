# [ETL-31] ETL dashboard is still busted

Need the Python/Flask dashboard wired up now because the data team cannot trigger ETL, check logs, or pull the output file from the browser. Keep it simple and do not improvise route names, file paths, or schema because downstream checks are already pinned to the contract below.

## Backend

Need `/app/workspace/src/app.py` created and the Flask app has to run on host `0.0.0.0` and port `5000`.

ETL behavior has to be exact:

* Read every `.csv` file from `/app/workspace/data/input/`.
* Preserve all original CSV columns.
* Write `/app/workspace/data/output.json` as one flat JSON array where every element is an object keyed by the CSV column names and every stored value stays a string value from the CSV.
* Insert every record into `/app/workspace/data/etl.db`.
  * Schema MUST be exactly: `CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT)`
  * The `data` column must store the JSON string for the full row.
* Append a timestamped success or error line to `/app/workspace/data/etl.log` on every ETL run.

Endpoints also have to be exact:

* `GET /` serves the dashboard via `templates/index.html`.
* `POST /trigger` runs the ETL pipeline end to end.
* `GET /logs` returns the full contents of `/app/workspace/data/etl.log`.
* `GET /download` serves `/app/workspace/data/output.json`.

## Frontend

Put the UI exactly at `/app/workspace/src/templates/index.html`.

Frontend requirements are not optional:

* Include a button that sends a `POST` request to `/trigger`.
* Disable that button while the request is running with JS and re-enable it when the request finishes. If the button stays active during the run, users spam it and we get overlapping ETL jobs.
* Add a `<pre>` block that fetches `/logs` automatically on page load using `window.onload` or `DOMContentLoaded` and renders the returned text into the page.
* Add a normal download link with `<a href="/download">` for the JSON output.

Do not overbuild this. Just hit the contract exactly and keep the browser flow working.
