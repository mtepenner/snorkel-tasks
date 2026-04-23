need a python etl backend at /app/workspace/src/app.py running flask on 0.0.0.0:5000. it should read csvs from /app/workspace/data/input/ and preserve all columns. spit the json array out to /app/workspace/data/output.json. also push those records into /app/workspace/data/etl.db. u must use this exact sqlite schema: CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT) where data is the row json.

we need 3 specific routes: POST /trigger to run the etl, GET /logs to read /app/workspace/data/etl.log (which needs timestamped logs appended), and GET /download to grab the json file.

for the frontend, just drop an index.html into /app/workspace/src/templates/. wire up a button to fetch /trigger (make sure u write js to disable it while loading so nobody spams it), a pre tag that fetches from /logs, and an anchor tag linking to /download.
