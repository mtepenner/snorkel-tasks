# Backend ETL Processing

focus on the backend processing first. create the flask app in /app/workspace/src/app.py running on port 5000 (host 0.0.0.0). need POST /trigger to run the actual etl. it has to read the csvs from /app/workspace/data/input/, preserve all columns, dump the json array to /app/workspace/data/output.json, and insert into the db at /app/workspace/data/etl.db. use the schema CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT). 

set up GET /logs and GET /download routes too. make sure the script appends timestamped success/error states to /app/workspace/data/etl.log every run.
