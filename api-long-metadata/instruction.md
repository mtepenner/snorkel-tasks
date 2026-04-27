# [DOC-192] PDF extractor is eating prod

Need this patched today. Support is already yelling because big PDFs keep blowing up the extractor and I do not have time for a cleanup pass after this.

Build the API in `/app/workspace/src/api.py`. FastAPI app instance has to be exactly named `app` because the runner calls `uvicorn api:app` and I am not changing that now. Use `PyPDF2.PdfReader` only, no alternate PDF library, no extra dependency surprise.

The endpoint is `POST /extract` only. It must take `multipart/form-data` with the upload field named `file`. Pull `author` and `title` from PDF metadata directly, and if either one is missing use exactly `"Unknown Author"` and `"Untitled"`.

For the document body, actually parse the PDF text, split it into chunks capped at 1000 words each, and derive `topics` from the parsed content. I need 3 to 10 meaningful non-empty keyword strings, not filler, not obvious stop-words, and they need to reflect the document instead of generic junk.

Return one flat JSON object and do not rename anything because downstream is brittle. The response must contain these exact keys and types: `author` (str), `title` (str), `topics` (list[str]), `total_chunks` (int), `filename` (str, exactly the original uploaded filename), `total_words` (int).

Also drop a throwaway manual check page at `/app/workspace/src/static/index.html`. Mount that directory at `/static` using `StaticFiles` so `/static/index.html` really loads. The page can be ugly, I do not care. It just needs a file picker, a fetch/XHR call to `/extract`, and the raw JSON rendered on screen so I can sanity check the numbers.

Please do not get cute with extra routes, alternate shapes, or helper files I did not ask for. I need this exact contract working today.
