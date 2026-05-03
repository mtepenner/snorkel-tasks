# [DOC-192] PDF extractor needs a Java version before I get paged again

support is still screaming because big PDFs keep chewing through the extractor and the current quick fix is too easy to phone in, so I need the same feature rebuilt in Java and I need the outside behavior to stay dead simple.

Put the service under `/app/workspace/src`. The harness is going to compile and start a main class named `LongMetadataApi`, so that file and class need to exist there. If you want tiny Java helpers in the same folder, fine, just do not turn this into a giant framework project.

What has to work:
- Expose an HTTP service on port `8000`.
- Provide `POST /extract` and accept `multipart/form-data` with the uploaded PDF in a field named `file`.
- `GET /extract` should not work.
- Serve a manual check page at `/static/index.html` from the same process. I only need a file picker, a submit button, and the raw JSON dumped on the page after upload.

Extractor contract is not negotiable:
- Read `author` and `title` from the PDF metadata.
- If either one is missing, fall back to exactly `"Unknown Author"` and `"Untitled"`.
- Extract text from the PDF body, count the words, and treat the document as chunks of at most `1000` words each.
- Return `total_chunks` as the exact chunk count implied by that `1000` word cap.
- Build `topics` from the extracted document text, not from the filename or metadata.
- `topics` must contain 3 to 10 single-word tokens, each at least 4 characters long, with obvious stop-words filtered out.
- Return `topics` sorted by descending term frequency so the most repeated relevant word comes first.
- Return the original uploaded filename unchanged in `filename`.

Response must be one flat JSON object with exactly these keys:
- `author`
- `title`
- `topics`
- `total_chunks`
- `filename`
- `total_words`

Environment note so nobody burns half the day rediscovering this: there is a JDK in the container and the PDF parsing jars are available under `/usr/share/java/`. Use whatever Java approach you want, just keep the deliverable small and do not change the API shape.
