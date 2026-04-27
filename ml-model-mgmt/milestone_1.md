milestone 1: get the data preprocessing api running in `/app/workspace/src/api.py`.
- wire up a POST `/api/v1/data/upload` endpoint to accept either json arrays of objects or raw csv text.
- csv needs a real header row. if the first row is numeric-looking data like `1,2` and not actual headers, reject it with 400 instead of silently accepting it.
- validate the data so it does not blow up on garbage input: return 400 or 415 for bad input, never a 500.
- add the preprocessing pass: missing-value imputation for numeric columns, standard scaling for numeric columns, and one-hot encoding for categorical columns.
- after encoding categoricals, do not leave the original string columns hanging around.
- slap a GET `/api/v1/data/processed` endpoint on there to spit out the cleaned dataset as a flat json array of objects.

