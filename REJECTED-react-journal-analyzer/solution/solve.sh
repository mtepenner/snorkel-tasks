#!/bin/bash
set -euo pipefail

# Oracle solution: Create the app at /app and inject the oracle HTML
mkdir -p /app

cat > /app/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Scientific Journal Analyzer</title>
    <script src="vendor/react.js"></script>
    <script src="vendor/react-dom.js"></script>
    <script src="vendor/babel.js"></script>
    <script src="vendor/pdf.js"></script>
    <script>
      pdfjsLib.GlobalWorkerOptions.workerSrc = "vendor/pdf.worker.js";
    </script>
    <style>
                :root {
                    color-scheme: light;
                    --bg: #f2efe7;
                    --panel: #fffaf0;
                    --ink: #1f2933;
                    --accent: #0f766e;
                    --accent-soft: #d9f3ef;
                    --border: #d8cfc2;
                }

                * { box-sizing: border-box; }
                body {
                    margin: 0;
                    font-family: Georgia, "Times New Roman", serif;
                    background:
                        radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 30%),
                        linear-gradient(180deg, #faf7f0 0%, var(--bg) 100%);
                    color: var(--ink);
                }

                .shell {
                    max-width: 1080px;
                    margin: 0 auto;
                    padding: 32px 20px 48px;
                }

                .hero {
                    display: grid;
                    gap: 12px;
                    margin-bottom: 24px;
                }

                .hero h1 {
                    margin: 0;
                    font-size: clamp(2rem, 3vw, 3.2rem);
                }

                .hero p {
                    margin: 0;
                    max-width: 64ch;
                    line-height: 1.6;
                }

                .panel {
                    background: rgba(255, 250, 240, 0.9);
                    border: 1px solid var(--border);
                    border-radius: 20px;
                    box-shadow: 0 24px 60px rgba(70, 53, 33, 0.08);
                    backdrop-filter: blur(10px);
                }

                .uploader {
                    padding: 20px;
                    display: grid;
                    gap: 12px;
                    margin-bottom: 20px;
                }

                .uploader label {
                    font-weight: 700;
                }

                .uploader input[type="file"] {
                    padding: 14px;
                    border: 1px dashed var(--border);
                    border-radius: 14px;
                    background: white;
                }

                .status {
                    font-size: 0.95rem;
                    color: #36514c;
                }

                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 16px;
                    margin-bottom: 20px;
                }

                .card {
                    padding: 18px;
                }

                .card h2 {
                    margin: 0 0 8px;
                    font-size: 1rem;
                    letter-spacing: 0.04em;
                    text-transform: uppercase;
                }

                .metric-value {
                    font-size: 2.4rem;
                    font-weight: 700;
                    color: var(--accent);
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th, td {
                    padding: 8px 0;
                    text-align: left;
                    border-bottom: 1px solid rgba(216, 207, 194, 0.8);
                }

                .sections,
                .json-panel {
                    padding: 20px;
                    margin-bottom: 20px;
                }

                .sections ul {
                    margin: 0;
                    padding-left: 20px;
                    display: grid;
                    gap: 12px;
                }

                .sections strong {
                    display: block;
                    margin-bottom: 4px;
                }

                pre {
                    margin: 0;
                    padding: 16px;
                    overflow: auto;
                    background: #102a27;
                    color: #dff8f2;
                    border-radius: 14px;
                }

                @media (max-width: 640px) {
                    .shell {
                        padding: 20px 14px 32px;
                    }
                }
    </style>
  </head>
  <body>
    <div id="root"></div>

    <script type="text/babel">
                const { useState } = React;

                // if (window.pdfjsLib) {
                //     window.pdfjsLib.GlobalWorkerOptions.workerSrc =
                //         'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                // }

                function countWords(text) {
                    return (text.match(/\b[\w'-]+\b/g) || []).length;
                }

                function keywordStats(text, keyword, totalWords) {
                    const count = (text.match(new RegExp(`\\b${keyword}\\b`, 'gi')) || []).length;
                    return {
                        count,
                        density: totalWords ? Number((count / totalWords).toFixed(3)) : 0,
                    };
                }

                function extractSummary(block) {
                    const compact = block.replace(/\s+/g, ' ').trim();
                    if (!compact) {
                        return 'No summary available.';
                    }

                    const firstSentence = compact.match(/.*?[.!?](?=\s|$)/);
                    if (firstSentence) {
                        return firstSentence[0].trim();
                    }

                    return compact.split(/\s+/).slice(0, 20).join(' ');
                }

                function extractMarkdownSections(text) {
                    const normalized = text.replace(/\r\n/g, '\n');
                    const headingPattern = /^#\s+(.+)$/gm;
                    const matches = [...normalized.matchAll(headingPattern)];

                    return matches.map((match, index) => {
                        const title = match[1].trim();
                        const sectionStart = match.index + match[0].length;
                        const sectionEnd = index + 1 < matches.length ? matches[index + 1].index : normalized.length;
                        const sectionBody = normalized.slice(sectionStart, sectionEnd).trim();
                        return {
                            title,
                            summary: extractSummary(sectionBody),
                        };
                    });
                }

                function extractPdfSections(text) {
                    const lines = text
                        .split(/\n+/)
                        .map((line) => line.trim())
                        .filter(Boolean);

                    const sections = [];
                    for (let index = 0; index < lines.length; index += 1) {
                        const line = lines[index];
                        const words = line.split(/\s+/).filter(Boolean);
                        if (words.length > 0 && words.length <= 4 && /^[A-Z][A-Za-z0-9\s-]+$/.test(line)) {
                            sections.push({
                                title: line,
                                summary: extractSummary(lines[index + 1] || ''),
                            });
                        }
                    }

                    return sections;
                }

                function analyzeDocument(text, fileType) {
                    const citations = (text.match(/\[\d+\]/g) || []).length;
                    const totalWords = countWords(text);

                    return {
                        fileType,
                        citations,
                        totalWords,
                        keywordDensity: {
                            quantum: keywordStats(text, 'quantum', totalWords),
                            entanglement: keywordStats(text, 'entanglement', totalWords),
                        },
                        sectionSummaries: fileType === 'markdown' ? extractMarkdownSections(text) : extractPdfSections(text),
                    };
                }

                async function readPdf(file) {
                    const arrayBuffer = await file.arrayBuffer();
                    const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
                    const pages = [];

                    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
                        const page = await pdf.getPage(pageNumber);
                        const content = await page.getTextContent();
                        let lastY = null;
                        const tokens = [];

                        content.items.forEach((item) => {
                            if (lastY !== null && Math.abs(item.transform[5] - lastY) > 5) {
                                tokens.push('\n');
                            }
                            tokens.push(item.str);
                            lastY = item.transform[5];
                        });

                        pages.push(tokens.join(' ').replace(/\s*\n\s*/g, '\n'));
                    }

                    return pages.join('\n');
                }

                async function readFileText(file) {
                    const lowerName = file.name.toLowerCase();
                    if (lowerName.endsWith('.pdf')) {
                        return readPdf(file);
                    }

                    return file.text();
                }

                function App() {
                    const [status, setStatus] = useState('Choose a Markdown or PDF paper to begin.');
                    const [analysis, setAnalysis] = useState(null);
                    const [error, setError] = useState('');

                    const handleFileChange = async (event) => {
                        const file = event.target.files && event.target.files[0];
                        if (!file) {
                            return;
                        }

                        setStatus(`Analyzing ${file.name}...`);
                        setError('');

                        try {
                            const text = await readFileText(file);
                            const fileType = file.name.toLowerCase().endsWith('.pdf') ? 'pdf' : 'markdown';
                            const nextAnalysis = analyzeDocument(text, fileType);
                            setAnalysis(nextAnalysis);
                            setStatus(`Analysis ready for ${file.name}.`);
                        } catch (analysisError) {
                            console.error(analysisError);
                            setAnalysis(null);
                            setError('Could not analyze that document.');
                            setStatus('Analysis failed.');
                        }
                    };

                    return (
                        <div className="shell">
                            <header className="hero">
                                <p>Scientific Computing & Analysis</p>
                                <h1>Interactive Journal Analyzer</h1>
                                <p>
                                    Load a scientific paper in Markdown or PDF format to inspect citation frequency,
                                    keyword density, and section summaries without leaving the browser.
                                </p>
                            </header>

                            <section className="panel uploader">
                                <label htmlFor="paper-upload">Paper file</label>
                                <input
                                    id="paper-upload"
                                    type="file"
                                    accept=".md,.markdown,.pdf"
                                    onChange={handleFileChange}
                                />
                                <p className="status">{status}</p>
                                {error ? <p role="alert">{error}</p> : null}
                            </section>

                            <div className="grid">
                                <section className="panel card">
                                    <h2>Citation Frequency</h2>
                                    <div className="metric-value">{analysis ? analysis.citations : 0}</div>
                                    <p>Total bracket citations found in the current paper.</p>
                                </section>

                                <section className="panel card">
                                    <h2>Keyword Density</h2>
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Keyword</th>
                                                <th>Count</th>
                                                <th>Density</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {['quantum', 'entanglement'].map((keyword) => {
                                                const stats = analysis ? analysis.keywordDensity[keyword] : { count: 0, density: 0 };
                                                return (
                                                    <tr key={keyword}>
                                                        <td>{keyword}</td>
                                                        <td>{stats.count}</td>
                                                        <td>{stats.density}</td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </section>

                                <section className="panel card">
                                    <h2>Total Words</h2>
                                    <div className="metric-value">{analysis ? analysis.totalWords : 0}</div>
                                    <p>Keyword density is calculated as count / totalWords.</p>
                                </section>
                            </div>

                            <section className="panel sections">
                                <h2>Section Summaries</h2>
                                <ul>
                                    {analysis && analysis.sectionSummaries.length > 0 ? (
                                        analysis.sectionSummaries.map((section) => (
                                            <li key={section.title}>
                                                <strong>{section.title}</strong>
                                                <span>{section.summary}</span>
                                            </li>
                                        ))
                                    ) : (
                                        <li>No section summaries yet.</li>
                                    )}
                                </ul>
                            </section>

                            <section className="panel json-panel">
                                <h2>Analysis JSON</h2>
                                <pre id="analysis-output">
                                    {analysis ? JSON.stringify(analysis, null, 2) : 'No analysis yet.'}
                                </pre>
                            </section>
                        </div>
                    );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
  </body>
</html>
EOF
