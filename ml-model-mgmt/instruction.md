# [ML-404] ML Model Management API & Dashboard

**Context:**
We need to extend the Flask stub at `/app/workspace/src/api.py`.

## Milestone 1 - Data Preprocessing API

**AC for `api.py`:**
* **POST `/api/v1/data/upload`**: Needs to handle TWO formats:
  1. JSON array of objects (e.g. `[{"A": 1, "B": null}, {"A": 2, "B": 4}]`)
  2. Raw CSV text (must have a header row)
* **Validation requirements:**
  * Throw 400 for malformed/empty input.
  * Throw 415 if the content-type is unsupported.
  * **NO 500 ERRORS** from bad input. Handle it gracefully!
* **Processing Pipeline (runs after successful upload):**
  * Impute missing numeric values with the column mean.
  * Z-score normalization for numeric columns (mean approx 0, std dev approx 1).
  * One-hot encode categorical/string columns (and drop the original string columns).
* **GET `/api/v1/data/processed`**: Return the processed dataset as a flat JSON array of objects.

## Milestone 2 - Frontend Dashboard

**AC for UI:**
* Create a responsive HTML page at `/app/workspace/src/templates/index.html`. 
* You can put JS in `/app/workspace/src/static/js/app.js` or just inline it in the HTML, I don't care.
* Page MUST have a nav area or sidebar containing the exact words `data`, `model`, and `inference`.
- a model configuration form with a `<select>` element containing at least two options
- an `<input type="range">` slider for hyperparameters
- a chart area using either `<canvas>` or `<svg>`
- a viewport meta tag so the layout works on mobile screens

Need this deployed by EOD. Thx.

## Milestone 3 - Inference Flow

Add `POST /api/v1/predict` in `/app/workspace/src/api.py`. The endpoint must accept `{"features": [1, 2, 3]}` and return `{"prediction": <number>}`. The prediction value must be derived from the submitted features rather than returned as a hardcoded constant.

Wire the frontend form to call `/api/v1/predict` with the user-provided input. The frontend implementation must:
- call `e.preventDefault()` so the form does not trigger a full page reload
- show a spinner or visible `loading` indicator while the request is in flight
- write the returned prediction into the DOM using `innerHTML` or `textContent`
- use `.catch()` or equivalent `try`/`catch` handling for request failures


