# [DOC-192] Large PDF Processing API

**Context:**
We are having massive OOM issues processing 50k+ token PDFs. I need a python API built at `/app/workspace/src/api.py` to handle this. 

**AC:**
* Bind the server to `0.0.0.0:8000`.
* Implement text chunking for the docs (cap at 1000 words per chunk MAX) so the server doesn't crash.
* **Endpoint:** `POST /extract`
  * Must accept `multipart/form-data` upload
  * Field name MUST be `file`.
* **Metadata extraction:**
  * Pull `author` and `title` directly from the PDF metadata properties.
  * Fallbacks if missing: `"Unknown Author"` and `"Untitled"`.
* **Processing:**
  * Parse the text chunks to figure out the `topics`.
* **Response Format:**
  * Must be a flat JSON object. DO NOT CHANGE THESE KEYS OR TYPES:
    * `author` (string)
    * `title` (string)
    * `topics` (array of strings)
    * `total_chunks` (int)
    * `filename` (string)
    * `total_words` (int)

**UI AC:**
* Throw together a really basic, ugly test UI at `/app/workspace/src/static/index.html`. 
* Just needs a file picker that hits the API and dumps the raw JSON response onto the screen so I can verify the math manually.

Plz fix this, prod is struggling with big files.
