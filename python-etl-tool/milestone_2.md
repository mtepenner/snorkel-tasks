okay so next part is the UI. drop an index.html into /app/workspace/src/templates/ ... just basic vanilla js. 

we need a button to run the etl that sends a POST to /trigger. but make sure u write a script to disable that button while its loading bcuz last time someone spammed it and locked the database. 

then just add a pre tag or something that pulls from the /logs endpoint so we can see the output. oh and a download link to /download for the json file.  Ensure everything meets standards for final release.