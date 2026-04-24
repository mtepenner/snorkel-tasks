need to get the data prep api off the ground for the ml system. just basic backend stuff to clean and prep data before training.

put the logic in `/app/workspace/src/api.py`.

here is the scoring breakdown (1 point each, binary pass/fail):
* 1 pt: wire up a POST `/api/v1/data/upload` endpoint to swallow csv or json payloads.
* 1 pt: validate the data so it doesn't crash on garbage input.
* 1 pt: add some basic preprocessing: handle missing values (mean/median/drop), standard/min-max scaling, and one-hot encoding for categorical columns.
* 1 pt: slap a GET `/api/v1/data/processed` endpoint on there to spit out the cleaned dataset.
* 1 pt: make sure it throws a 400 for bad input and 500 if the server actually catches fire.
