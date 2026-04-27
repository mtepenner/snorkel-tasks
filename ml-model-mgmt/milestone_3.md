milestone 3: hook up the model inference api to the frontend.
- add a dummy prediction route POST `/api/v1/predict` in the python api. it must accept json like `{"features": [1, 2, 3]}` and return a json response with the key `prediction` (e.g., `{"prediction": 6}`).
- the prediction must come from the submitted features and it must be deterministic for the same input. no hardcoded constant, no randomness, no time-based nonsense.
- write fetch logic in the frontend to grab user input from the ui and hit `/api/v1/predict` exactly.
- absolutely no full page reloads when they click the 'run prediction' button (use `e.preventDefault()`).
- show a loading spinner or 'loading' text while the model is thinking.
- parse the json response and use javascript to actually update the dom (`innerHTML` or `textContent`) to display the prediction result.
- handle ui errors gracefully with `.catch()` if the fetch fails.
