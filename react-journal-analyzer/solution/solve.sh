#!/bin/bash
# Oracle solution: Create the app at /app and inject the oracle HTML
mkdir -p /app

cat > /app/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Journal Analyzer</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        body { font-family: sans-serif; padding: 2rem; background: #f4f4f5; }
        .dashboard { background: white; padding: 2rem; border-radius: 8px; }
        pre { background: #1e293b; color: #38bdf8; padding: 1rem; }
    </style>
  </head>
  <body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        function App() {
            const [stats, setStats] = useState(null);

            useEffect(() => {
                fetch('/data/paper.md')
                    .then(res => res.text())
                    .then(text => {
                        const citations = (text.match(/\[\d+\]/g) || []).length;
                        const quantumCount = (text.match(/quantum/gi) || []).length;
                        const entanglementCount = (text.match(/entanglement/gi) || []).length;
                        const headers = (text.match(/^#\s+(.*)/gm) || []).map(h => h.replace('# ', '').trim());

                        setStats({
                            citations: citations,
                            keywords: {
                                quantum: quantumCount,
                                entanglement: entanglementCount
                            },
                            headers: headers
                        });
                    })
                    .catch(err => console.error("Error loading paper:", err));
            }, []);

            if (!stats) return <div>Loading and parsing paper...</div>;

            return (
                <div className="dashboard">
                    <h1>Journal Analyzer Dashboard</h1>
                    <p>Total Citations: {stats.citations}</p>
                    <p>Quantum Mentions: {stats.keywords.quantum}</p>
                    <p>Entanglement Mentions: {stats.keywords.entanglement}</p>
                    <pre id="stats-output">
                        {JSON.stringify(stats, null, 2)}
                    </pre>
                </div>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
  </body>
</html>
EOF
