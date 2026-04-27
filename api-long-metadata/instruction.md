**[DOC-192] URGENT: PDF extractor is eating prod**

**Priority:** Highest / Blocker
**Assignee:** Unassigned
**Reporter:** [SysAdmin/Lead Dev]

**Description:**
Guys, support is already yelling at me. Big PDFs are blowing up the extractor and eating prod. We need this patched TODAY and I absolutely do not have time to do a cleanup pass on this later, so please get it right the first time. 

**Acceptance Criteria:**
* **Location:** Build the API in `/app/workspace/src/api.py`.
* **Framework:** FastAPI. The app instance MUST be named exactly `app`. The runner is hardcoded to `uvicorn api:app` and I am not fighting with devops to change that today.
* **Library:** Use `PyPDF2.PdfReader` ONLY. No alternate libraries, no weird new dependencies. 
* **Endpoint:** `POST /extract` ONLY.
    * Must accept `multipart/form-data` (upload field must be named `file`).
* **Metadata handling:** * Pull `author` and `title` directly from the PDF metadata. 
    * Fallbacks: If missing, use exactly `"Unknown Author"` and `"Untitled"`.
* **Text parsing:**
    * Parse the body text and split it into chunks capped at exactly 1000 words each.
    * Derive `topics` from the parsed content. I need 3 to 10 *meaningful*, non-empty keyword strings. No obvious stop-words, no generic filler. It needs to actually reflect the document.
* **Response Payload:** Return ONE flat JSON object. Do not rename *anything*—downstream is incredibly brittle right now. Must contain exactly:
    * `author` (str)
    * `title` (str)
    * `topics` (list[str])
    * `total_chunks` (int)
    * `filename` (str - strictly the original uploaded filename)
    * `total_words` (int)
* **Testing UI:** * Throw a manual check page into `/app/workspace/src/static/index.html`. 
    * Mount it at `/static` using `StaticFiles` so `/static/index.html` actually loads. 
    * I don't care if it's ugly as sin. It just needs a basic file picker, a fetch/XHR call to `/extract`, and it needs to dump the raw JSON on the screen so I can sanity-check the numbers.

**Notes:**
Please do not get cute with extra routes, alternate JSON shapes, or extra helper files I didn't ask for. I just need this exact contract working by EOD.
