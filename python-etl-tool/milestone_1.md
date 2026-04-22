For this first milestone, please just focus on the data processing backend. 

Create the Flask app at `/app/workspace/src/app.py`. It needs to handle the core ETL logic: reading any CSVs in `/app/workspace/data/input/`, converting them, writing out `/app/workspace/data/output.json`, and inserting the JSON strings into a `records` table in `/app/workspace/data/etl.db`. 

Make sure to set up the backend endpoints for triggering the process (`/trigger`, via POST), fetching the logs (`/logs`, via GET), and downloading the JSON (`/download`, via GET). Every time the ETL runs, append a success or error message with a timestamp to `/app/workspace/data/etl.log`.

