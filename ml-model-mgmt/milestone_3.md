last piece: wire the frontend and the inference api together so it actually does something.

here is the scoring breakdown (1 point each, binary pass/fail):
* 1 pt: add a dummy prediction route in `/app/workspace/src/api.py` (like POST `/api/v1/predict`).
* 1 pt: write some fetch logic in `/app/workspace/src/static/js/app.js` to grab user input from the ui and hit the `/predict` endpoint.
* 1 pt: absolutely no full page reloads when they click the 'run prediction' button.
* 1 pt: show a loading spinner or something while the model is thinking.
* 1 pt: parse the json response and update the dom/charts with the results.
* 1 pt: handle ui errors gracefully if the fetch fails or times out.