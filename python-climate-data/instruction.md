can someone write a script at /app/workspace/src/analyzer.py for the climate logs? the files are at /app/workspace/data/climate.csv and /app/workspace/data/metadata.json

just merge the regions to the temps but toss out anything older than 2021 since its messing up our charts. save the filtered list of dicts to /app/workspace/data/cleaned.json and make sure region is a string and temperature is a float.

after that get the average temp per region and drop it in /app/workspace/data/trends.json as a flat dict. region name is the key, mean temp is the value.

for the visual use the python graphviz lib to make a directed graph. have the regions point straight to their averages. export the png to /app/workspace/output/climate_graph.png but turn cleanup to False. i need to check the raw dot file so dont let it auto delete.
