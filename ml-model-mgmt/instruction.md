need you to flesh out this ml model management system. we already have a base flask app sitting at /app/workspace/src/api.py with some dummy models, but it needs the actual logic wired up across three milestones.

milestone 1: get the data preprocessing api running. add the rest api endpoints in /app/workspace/src/api.py to handle the data cleaning and prep.

milestone 2: toss a simple web gui into /app/workspace/src/templates/index.html (put any static js you need in /app/workspace/src/static/). just need basic visualization and config controls for the models.

milestone 3: hook up the model inference api. the frontend needs to be able to actually trigger predictions and display the results without the app crashing.

keep it straightforward and make sure everything maps exactly to those paths.
