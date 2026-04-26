# ML Model Management API

Extend the Flask stub at `/app/workspace/src/api.py`. Add your implementation on top of the existing stub rather than replacing the file outright.

## Milestone 1 - Data Preprocessing API

Implement the backend work in `/app/workspace/src/api.py`.

Add `POST /api/v1/data/upload` with support for both of the following input formats:
- a JSON array of objects, for example `[{"A": 1, "B": null}, {"A": 2, "B": 4}]`
- raw CSV text with a header row

Validation requirements:
- return HTTP 400 for malformed or empty input
- return HTTP 415 for unsupported content types
- do not allow invalid input to surface as an HTTP 500 response

After a successful upload, run this preprocessing pipeline:
- fill missing numeric values with the column mean
- standard-scale numeric columns with z-score normalization so the mean is approximately `0` and the standard deviation is approximately `1`
- one-hot encode string or categorical columns and drop the original categorical columns

Add `GET /api/v1/data/processed` to return the current processed dataset as a flat JSON array of row objects.

## Milestone 2 - Frontend Dashboard

Create a responsive HTML page at `/app/workspace/src/templates/index.html`. Client-side JavaScript may be placed in `/app/workspace/src/static/js/app.js` or written inline in the HTML.

The page must include:
- a navigation area or sidebar containing the words `data`, `model`, and `inference`
- a model configuration form with a `<select>` element containing at least two options
- an `<input type="range">` slider for hyperparameters
- a chart area using either `<canvas>` or `<svg>`
- a viewport meta tag so the layout works on mobile screens

## Milestone 3 - Inference Flow

Add `POST /api/v1/predict` in `/app/workspace/src/api.py`. The endpoint must accept `{"features": [1, 2, 3]}` and return `{"prediction": <number>}`. The prediction value must be derived from the submitted features rather than returned as a hardcoded constant.

Wire the frontend form to call `/api/v1/predict` with the user-provided input. The frontend implementation must:
- call `e.preventDefault()` so the form does not trigger a full page reload
- show a spinner or visible `loading` indicator while the request is in flight
- write the returned prediction into the DOM using `innerHTML` or `textContent`
- use `.catch()` or equivalent `try`/`catch` handling for request failures


