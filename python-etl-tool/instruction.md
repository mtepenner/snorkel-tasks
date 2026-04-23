we need an etl system that processes some incoming csv files and brings the results to light on a simple web dashboard interface.  the primary objective is to allow the data team to manually trigger the pipeline, monitor the processing logs, and download the final aggregated data without needing terminal access.

# implementation and constraints:
* backend must be built in python
* frontend in html and js
* backend goes into app/workspace/src/app.py and run flask app on host 0.0.0.0 at port 5000
* etl logic -> all csvs must come in from /app/workspace/data/output.json
* after that, insert the records into /app/workspace/data/etl.db
* it is also important you make use of this exact sqlite schema: CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT) where the data column stores the json string for the row.
* for endpoints -> set up POST /trigger to run the etl process.  GET /logs needs to return the contents of /app/workspace/data/etl.log, ensuring your script appends timestamped successes and error logs
* GET /download serves the generated json file.
* ui behavior -> put the frontend at /app/workspace/src/templates/index.html
* the interface will need a button to trigger the endpoint, but you have to include js to temporarily disable it while the request is in flight to prevent db locks. 
* include <pre> block that fetches logs and standard download link
