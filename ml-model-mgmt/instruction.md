# [ML-404] model mgmt api + dashboard still not shippable

Need the Flask stub at `/app/workspace/src/api.py` finished today. Please do not freestyle extra routes or alternate payload shapes because the checks downstream are already wired.

## Milestone 1 - Data Preprocessing API

For `api.py`:
* **POST `/api/v1/data/upload`** has to accept exactly two upload shapes:
  1. JSON array of objects like `[{"A": 1, "B": null}, {"A": 2, "B": 4}]`
  2. Raw CSV text with a real header row
* CSV rule is not optional: if the first row is actually data and looks headerless, reject it with **400** instead of letting pandas pretend it found headers. Example: `1,2\n3,4\n` is bad input and should not be accepted as a valid header row.
* Validation rules:
  * return **400** for malformed or empty input
  * return **415** for unsupported content types
  * bad input must never bubble into a **500**
* After a successful upload, run the preprocessing pipeline:
  * impute missing numeric values with the column mean
  * z-score normalize numeric columns so the mean is roughly 0 and std dev is roughly 1
  * one-hot encode categorical/string columns and drop the original string columns afterward
* **GET `/api/v1/data/processed`** must return the processed dataset as one flat JSON array of objects

## Milestone 2 - Frontend Dashboard

For the UI:
* put a responsive page at `/app/workspace/src/templates/index.html`
* JS can live in `/app/workspace/src/static/js/app.js` or inline, whatever is faster
* the page must have a nav/sidebar area containing the exact words `data`, `model`, and `inference`
* build one model configuration form and put both of these controls inside that form:
  * a `<select>` with at least two options
  * an `<input type="range">` slider for hyperparameters
* add a chart area using either `<canvas>` or `<svg>`
* include a viewport meta tag so it works on mobile without breaking layout

Need this out by EOD.

## Milestone 3 - Inference Flow

Add `POST /api/v1/predict` in `/app/workspace/src/api.py`. It must accept `{"features": [1, 2, 3]}` and return `{"prediction": <number>}`. The prediction has to be derived from the submitted features, and it also has to be deterministic for the same feature list. Do not use randomness, clock time, or request state.

Wire the frontend form to call `/api/v1/predict` exactly with the user-provided input. The frontend implementation must:
* call `e.preventDefault()` so the form does not trigger a full page reload
* show a spinner or visible `loading` indicator while the request is in flight
* write the returned prediction into the DOM using `innerHTML` or `textContent`
* use `.catch()` or equivalent `try`/`catch` handling for request failures


