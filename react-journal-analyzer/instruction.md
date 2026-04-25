# React Journal Analyzer

build a react-based interactive journal analyzer in /app/index.html. keeping it as a client-side app is fine, and using the React, ReactDOM, and Babel CDNs is completely acceptable here.

the UI needs to let a user load a long scientific paper from either a Markdown file or a PDF file. use a real file picker in the browser and accept .md, .markdown, and .pdf files.

once a file is loaded, analyze it in the browser and update the dashboard right away. the analyzer needs to compute these things:

- citation frequency: count bracket citations like [1] or [42]
- keyword density for the terms quantum and entanglement, case-insensitive. include both the raw count and density, where density is count / totalWords rounded to 3 decimals
- section summaries. for markdown, treat lines starting with # as section headings and summarize each section with the first non-empty sentence under that heading. for pdf files, extract the text and produce section summaries when headings are recoverable from the extracted text

render the results in a readable react UI. at minimum the page needs:

- an upload control and a visible file/status message
- a citation frequency summary
- a keyword density display
- a section summaries list
- a machine-readable mirror of the current analysis in `<pre id="analysis-output"></pre>`

the JSON shown in that analysis block should follow this shape:

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
