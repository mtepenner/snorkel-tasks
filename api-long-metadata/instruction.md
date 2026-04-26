# [DOC-192] Large PDF Processing API crashing OOM

prod is literally falling over trying to process 50k+ token PDFs rn. I need a python API built at `/app/workspace/src/api.py` to stop the bleeding.

Requirements:

* bind to `0.0.0.0:8000`
* write some text chunking logic for the docs. cap it at 1000 words per chunk max so we don't nuke the server again.
* needs a `POST /extract` endpoint (must be POST!) taking `multipart/form-data` upload with the field name `file`
* grab `author` and `title` from the pdf metadata directly. if they are missing just use `"Unknown Author"` and `"Untitled"`
* you have to parse the text chunks themselves to figure out the `topics`
* MUST return a flat JSON object with these EXACT keys and types (do not change these or the downstream processor will break): `author` (str), `title` (str), `topics` (list of str), `total_chunks` (int), `filename` (str), `total_words` (int)

UI requirement:

* I need a quick way to test this manually, so throw together a really ugly test UI at `/app/workspace/src/static/index.html` (make sure your FastAPI setup actually mounts/serves static files from here using StaticFiles so I don't get 404s).
* just slap a file picker on it that hits the API via fetch (or XMLHttpRequest) and dumps the raw json response on the screen (use innerhtml, textcontent, or JSON.stringify so I can actually see the output). doesn't have to be pretty at all, just need to verify the math is right

Plz get this in today, clients are complaining
