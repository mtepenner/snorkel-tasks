# Backend ETL Processing

Need the backend done first. Create the Flask app in `/app/workspace/src/app.py`, bind it to `0.0.0.0:5000`, and make `POST /trigger` run the real ETL. It has to read the CSVs from `/app/workspace/data/input/`, preserve every column, write the JSON array to `/app/workspace/data/output.json`, and insert records into `/app/workspace/data/etl.db` using the exact schema `CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT)`.

Also wire up `GET /logs` and `GET /download`. Every ETL run has to append a timestamped success or error entry to `/app/workspace/data/etl.log`.
