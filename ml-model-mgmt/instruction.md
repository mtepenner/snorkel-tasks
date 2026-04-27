[ML-404] URGENT: Model Mgmt API + Dashboard still not shippable

Guys, we need the Flask stub at /app/workspace/src/api.py finished today, and I don't have time for downstream checks to fail because of unexpected payload shapes. Wire up POST /api/v1/data/upload to accept a JSON array or a raw CSV (strictly reject headerless data with a 400, no sneaky 500s), impute missing numeric values, z-score normalize, and one-hot encode. Once that's done, make sure GET /api/v1/data/processed returns the cleaned dataset as a single flat JSON array.

On the UI side, drop a responsive page at /app/workspace/src/templates/index.html (JS can go inline or in /app/workspace/src/static/js/app.js) with a nav containing the exact words "data", "model", and "inference", plus an empty chart area and a model config form with a select dropdown and a slider. Finally, add a purely deterministic POST /api/v1/predict route that takes {"features": [1, 2, 3]} and returns {"prediction": <number>}. Wire the frontend form to hit this endpoint without reloading the page, show a loading spinner, render the result directly in the DOM, and actually catch/handle request errors. Need this merged by EOD!

