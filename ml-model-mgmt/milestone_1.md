milestone 1: get the data preprocessing api running in `/app/workspace/src/api.py`.
- wire up a POST `/api/v1/data/upload` endpoint to swallow csv or json payloads.
- validate the data so it doesn't crash on garbage input (throw a 400 or 415 for bad input, NOT a 500).
- add some basic preprocessing: handle missing values (imputation), standard scaling for numeric columns, and one-hot encoding for categorical columns.
- slap a GET `/api/v1/data/processed` endpoint on there to spit out the cleaned dataset as a flat json array of objects.

