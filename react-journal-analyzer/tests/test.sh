#!/bin/bash
set -e

if [ "$PWD" = "/" ]; then
  echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile before running this script."
  exit 1
fi

# 1. Generate the verifier fixtures for markdown and pdf uploads
mkdir -p /app/test-fixtures
cat > /app/test-fixtures/paper.md <<'EOF'
# Abstract

Quantum entanglement lets quantum systems share information across experiments [1]. Quantum sensors rely on entanglement [2].

# Results

Our quantum measurement pipeline tracks entanglement in repeated trials [3].

# Conclusion

Entanglement improves the final quantum estimate [4].
EOF

node <<'EOF'
const fs = require('fs');

function createPdf(lines, outputPath) {
  const stream = [
    'BT',
    '/F1 12 Tf',
    '72 720 Td',
    ...lines.flatMap((line, index) => {
      const escaped = line.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
      return index === 0 ? [`(${escaped}) Tj`] : ['0 -18 Td', `(${escaped}) Tj`];
    }),
    'ET',
  ].join('\n');

  const objects = [
    '1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n',
    '2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n',
    '3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>\nendobj\n',
    `4 0 obj\n<< /Length ${Buffer.byteLength(stream, 'utf8')} >>\nstream\n${stream}\nendstream\nendobj\n`,
    '5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n',
  ];

  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  for (const object of objects) {
    offsets.push(Buffer.byteLength(pdf, 'utf8'));
    pdf += object;
  }

  const startXref = Buffer.byteLength(pdf, 'utf8');
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (let i = 1; i <= objects.length; i += 1) {
    pdf += `${String(offsets[i]).padStart(10, '0')} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${startXref}\n%%EOF\n`;

  fs.writeFileSync(outputPath, pdf);
}

createPdf(
  [
    'Introduction',
    'Quantum entanglement appears in the introduction [1].',
    'Conclusion',
    'Entanglement stabilizes the quantum result [2].',
  ],
  '/app/test-fixtures/paper.pdf'
);
EOF

# 2. Run the provided UI skeleton test suite
cd /tests
npm install
export DEBIAN_FRONTEND=noninteractive
npx playwright install-deps chromium
npx playwright install chromium

UNIT_EXIT=0
E2E_EXIT=0
npm run test || UNIT_EXIT=$?
npm run test:e2e || E2E_EXIT=$?

set +e
mkdir -p /logs/verifier
[ "$UNIT_EXIT" -eq 0 ] && [ "$E2E_EXIT" -eq 0 ]
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
