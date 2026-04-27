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
* **Word counting:** Keep `totalWords` deterministic. Count words from the raw uploaded text with the same behavior as `/\b[\w'-]+\b/g`, so heading words and citation numbers like the `1` in `[1]` still count.
* **Keywords:** Count frequency & density for "quantum" and "entanglement" (case-insensitive). Density = `count / totalWords` (round to 3 decimals).
* **Summaries:**
  * For Markdown: Treat lines starting with `#` as headers. Summarize with the first non-empty sentence under that heading.
  * For PDF: Extract text client-side, recover headings if possible, and do the same summary logic.
  * Do not overengineer the PDF path. The verifier uses a simple text-based PDF fixture, so a lightweight client-side parser or fallback that can pull text from a basic PDF stream is enough.
  * Whatever PDF approach you take, make sure uploading a `.pdf` actually updates the JSON mirror with `fileType: "pdf"` and the parsed counts instead of leaving the initial empty state behind.

**UI Requirements:**

* Upload control & status message.
* Show visible dashboard sections titled exactly `Citation Frequency`, `Keyword Density`, and `Section Summaries`.
* The section summaries list needs to render each section title clearly in the UI, not just bury it inside the JSON mirror.
* Put that rendered section summary list inside a `.sections` container and render each section title in a `<strong>` element so the titles are easy to scan.
* **CRITICAL FOR TESTS:** Render a machine-readable mirror of the analysis in a `<pre id="analysis-output"></pre>`.
* The data shown there must stay valid JSON and expose a consistent parseable shape with fields named `fileType`, `citations`, `totalWords`, `keywordDensity`, and `sectionSummaries`.
* Under `keywordDensity`, include `quantum` and `entanglement`, each with `count` and `density`. Under `sectionSummaries`, include each section's `title` and `summary` text.
* Do not hide any of that information behind visual-only formatting. The `<pre>` content needs to expose the same analysis the dashboard shows.
