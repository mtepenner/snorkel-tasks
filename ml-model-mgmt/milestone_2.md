next up, the frontend. need a simple, responsive gui so users can actually see and tweak the models.

drop the main html into `/app/workspace/src/templates/index.html` and any static css/js in `/app/workspace/src/static/`.

here is the scoring breakdown (1 point each, binary pass/fail):
* 1 pt: build a basic dashboard layout. sidebar for nav (data prep, model config, inference), main area for the active workspace.
* 1 pt: make a config form so users can pick a dummy model (like random forest or linear regression) and mess with the hyperparameters using sliders/dropdowns.
* 1 pt: throw in a basic chart area (chart.js or whatever works) to show dataset distributions or basic metrics.
* 1 pt: keep it responsive and cleanly linked to the backend.