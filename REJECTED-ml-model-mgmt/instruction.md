# [ML-404] URGENT: Model Mgmt API + Dashboard still not shippable

We are done pretending the Python stub is enough. Replace it with a small C++ service in `/app/workspace/src/ml_model_mgmt_server.cpp`. The harness is going to compile that file with `g++ -std=c++17` and run the binary, so keep it self-contained, do not pull in a giant framework, and make it listen on port `8000`.

API contract stays locked:
- `POST /api/v1/data/upload` must accept either a JSON array of objects or raw CSV text with a real header row.
- Reject empty JSON/CSV, malformed JSON, and headerless CSV with `400`.
- Reject unsupported media types like `application/xml` with `415`.
- Expected client mistakes should never turn into `500` responses.
- For numeric columns, impute missing values with the column mean before z-score normalization.
- One-hot encode categorical columns and drop the original categorical string columns.
- `GET /api/v1/data/processed` must return the cleaned dataset as one flat JSON array of row objects containing the scaled numeric fields plus the indicator columns.

UI still has to exist at `/app/workspace/src/templates/index.html` and the same C++ process needs to serve it from `GET /` for manual checking. JS can stay inline or live in `/app/workspace/src/static/js/app.js`.

UI requirements are not changing:
- include a viewport meta tag.
- the nav has to visibly contain the exact words `data`, `model`, and `inference`.
- include an empty chart area.
- include one model config form that contains a select dropdown with at least two options and a slider.

Inference contract also stays locked:
- add a deterministic `POST /api/v1/predict` route that accepts `{"features": [1, 2, 3]}` and returns JSON with a numeric `prediction`.
- the prediction must come from the submitted features, stay identical for identical input, and change when the features change.
- wire the frontend form to call `/api/v1/predict` without reloading the page.
- show a loading spinner while the request is in flight.
- render the result straight into the DOM.
- actually catch and surface request errors.

Need this merged by EOD and I really do not want a "works on my machine" excuse around the parser or the server wiring.

