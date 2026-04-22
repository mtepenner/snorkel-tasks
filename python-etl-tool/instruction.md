we have incoming csv files dropping into /app/workspace/data/input/ and need a fast flask web interface to handle the etl. script goes in /app/workspace/src/app.py. on trigger it should parse the csvs, transform to json and spit out the master file to /app/workspace/data/output.json. also push those records into sqlite at /app/workspace/data/etl.db.

frontend should live at /app/workspace/src/templates/index.html. don't overthink the UI, just give me a manual trigger button, a box that tails /app/workspace/data/etl.log so we can debug, and a link to download the output json.
