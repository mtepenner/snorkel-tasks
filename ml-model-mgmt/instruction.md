hey so we need to finish this ml model management thing. there's already a flask stub at `/app/workspace/src/api.py` — don't replace it, just build on top of it.

## milestone 1 - data preprocessing api

work inside `/app/workspace/src/api.py`

first thing is a `POST /api/v1/data/upload` endpoint. needs to handle two formats — either json (array of objects, like `[{"A": 1, "B": null}, {"A": 2, "B": 4}]`) or raw csv text with a header. don't let it blow up on bad input, return a 400 or 415, NOT a 500.

once data is uploaded run it through a preprocessing pipeline:
- fill in missing numeric values with the column mean
- standard scale the numeric cols (z-score, mean should come out ~0, std ~1)
- one-hot encode any string/categorical cols. so like a `color` column with "red" and "blue" in it becomes `color_red` and `color_blue`, drop the original

then wire up `GET /api/v1/data/processed` to return whatever's currently in the pipeline as a flat json array of objects (one dict per row).

## milestone 2 - frontend dashboard

drop a responsive html page at `/app/workspace/src/templates/index.html`. js can go in `/app/workspace/src/static/js/app.js` or just inline it, doesn't matter.

the page needs:
- a nav or sidebar — just needs the words "data", "model", and "inference" in it somewhere
- a model config form with a `<select>` dropdown (2+ options) and a range slider for hyperparams
- a chart area, `<canvas>` or `<svg>` is fine, just needs to be there
- viewport meta tag so it's not broken on mobile

## milestone 3 - wire up inference

backend side: add `POST /api/v1/predict` to the api. takes `{"features": [1, 2, 3]}` and gives back `{"prediction": <some number>}`. the number has to actually come from the features — sum them, dot product, whatever, just don't return a hardcoded value.

frontend side: hook it up. form submit should call fetch against `/api/v1/predict` with whatever the user put in. a few things that are non-negotiable:
- `e.preventDefault()` so the page doesn't reload
- show a spinner or "loading" somewhere while it's waiting
- put the prediction result in the dom when it comes back (`innerHTML` or `textContent`)
- `.catch()` for when the request bombs out


