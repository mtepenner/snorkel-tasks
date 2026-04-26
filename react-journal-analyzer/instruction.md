# [UI-505] React Client-Side Journal Analyzer

**Context:**
Need a quick tool for the researchers to analyze journals. Keeping it entirely client-side is fine.

**AC:**
* Build the app in `/app/index.html`.
* You can just use React, ReactDOM, and Babel CDNs in the HTML file, don't bother setting up a full build pipeline.
* Put a real file picker on the page that accepts `.md`, `.markdown`, and `.pdf` files.
* App should analyze the file as soon as it's loaded and update the dashboard automatically.

**Analysis Requirements:**
* **Citations:** Count bracket style citations e.g., `[1]` or `[42]`.
* **Keywords:** Count frequency & density for "quantum" and "entanglement" (case-insensitive). Density = `count / totalWords` (round to 3 decimals).
* **Summaries:**
  * For Markdown: Treat lines starting with `#` as headers. Summarize with the first non-empty sentence under that heading.
  * For PDF: Extract text, recover headings if possible, and do the same summary logic.

**UI Requirements:**
* Upload control & status message.
* Citation frequency summary widget.
* Keyword density display.
* Section summaries list.
* **CRITICAL FOR TESTS:** A machine-readable mirror of the data in a `<pre id="analysis-output"></pre>`. 
  Must be this exact JSON shape:
  ```json
  {
    "fileType": "markdown" | "pdf",
    "citations": number,
    "totalWords": number,
    "keywordDensity": {
      "quantum": { "count": number, "density": number },
      "entanglement": { "count": number, "density": number }
    },
    "sectionSummaries": [
      { "title": string, "summary": string }
    ]
  }
  ```

Plz match that JSON schema exactly, the e2e test will blow up otherwise.
